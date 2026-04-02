# AI-JIE: Technical Report

**Project**: Automated Job Information Extraction (AI-JIE)
**Started**: 2026-03-29
**Status**: Active development

---

## 1. Project Overview

AI-JIE is a pipeline that extracts structured information from raw job postings at scale. The extracted data is stored on HuggingFace Hub and evaluated using an LLM-as-a-Judge framework to measure and improve extraction quality over time.

**Data source**: Two Kaggle CSV datasets (`DataScientist.csv`, `DataAnalyst.csv`) — 3,892 and 2,242 usable rows respectively after filtering short descriptions.

**Goal**: Produce a clean, structured dataset of job postings (company, role, skills, compensation) that can feed downstream analysis and ML applications.

---

## 2. Architecture

```
raw CSVs → loader.py (unify, clean) → pipeline.py (async extraction) → jobs_lite/full.jsonl
         ↓
    HuggingFace Hub (Parquet, public — lite + full repos)
         ↓
    evals/runner.py → extractions + scores → eval_results/
         ↓
    ground_truth_sampler.py → gt_sample.jsonl → ground_truth_annotator.py (human labels)
```

### Modules

| Module | Responsibility |
|--------|----------------|
| `src/data_ingestion/models.py` | Pydantic schemas: `Job`, `EvaluationScore`, enums |
| `src/data_ingestion/parser.py` | LLM extraction — `gpt-5.4-mini`, `instructor`, async |
| `src/data_ingestion/loader.py` | Unified CSV loader — concat, -1→NaN, common columns, clean index |
| `src/data_ingestion/pipeline.py` | Batch runner — lite/full modes, semaphore concurrency, checkpoint/resume |
| `src/data_ingestion/hub.py` | HuggingFace Hub push/pull — separate lite/full repos, public |
| `src/evals/judge.py` | LLM-as-a-Judge — `gpt-4o`, `instructor`, 17-dimension scoring |
| `src/evals/runner.py` | Eval orchestrator — sample, extract, judge, save |
| `src/evals/report.py` | Score aggregation, group summaries, report persistence |
| `src/evals/human_eval.py` | Human scoring — same 17-dimension schema as judge; `compare()` for calibration |

---

## 3. Key Design Decisions

### 3.1 `instructor` library over raw OpenAI client

**Decision**: Use `instructor.from_openai()` for both parser and judge.

**Justification**: The raw `OpenAI()` client + manual `json.loads()` + `Model(**raw)` had zero tolerance for type mismatches (e.g. `"2"` vs `2`). Any field error silently swallowed the entire response (0 out of 20 evaluations returned in early testing). `instructor` adds:
- Pydantic validation of every response
- Automatic retry with corrective feedback if the model returns wrong types or missing fields
- Consistent interface between async and sync paths

### 3.2 Lazy client initialisation

**Decision**: Clients are not created at module import time; they are created on first call via `_get_async_client()` / `_get_sync_client()`.

**Justification**: Module-level `AsyncOpenAI()` reads `OPENAI_API_KEY` at import time. If the key is not yet set (e.g. tests, or `dotenv` loaded after imports), this raises an error. Lazy initialisation avoids this entirely.

### 3.3 Async pipeline with semaphore rate limiting

**Decision**: `asyncio.Semaphore(concurrency=20)` for extraction; `concurrency=3` for eval (judge uses gpt-4o which has tighter limits).

**Justification**: Sequential processing of 3,000–4,000 records would take hours. Concurrency brings this down to minutes. The semaphore prevents hitting OpenAI rate limits (429s were encountered at higher concurrency with gpt-4o).

### 3.4 JSONL checkpoint/resume

**Decision**: Results are written to JSONL incrementally, one record per flush. On restart the pipeline reads existing `_row_id` values and skips them.

**Justification**: A long batch job over 3,000 records will hit rate limits or network errors. Without checkpointing, a failure at record 2,500 wastes all prior API spend and time. The `_row_id` is assigned before the async call so each coroutine has an isolated copy — ordering of completions does not matter.

### 3.5 Pipeline artifacts stripped before HuggingFace push

**Decision**: `_row_id` and `prompt_version` are written to every JSONL record but stripped by `push_to_hub` before uploading to HF.

**Justification**:
- `_row_id`: checkpoint/resume artifact — identifies which rows have been processed. Not a feature of the job data.
- `prompt_version`: traceability label (e.g. `"v9"`) stamped on each record at extraction time so any downstream analysis can identify which prompt produced it. Not a job feature; stripped to keep the public schema clean. Tracked in `_PIPELINE_INTERNAL_COLS` in `hub.py`.

### 3.6 HuggingFace Hub with `datasets` library

**Decision**: Use `datasets.Dataset.push_to_hub()` rather than raw `huggingface_hub` file upload.

**Justification**: The `datasets` library handles Parquet serialisation automatically, including Arrow `list<string>` types for fields like `skills_technical` and `key_responsibilities`. A raw file upload would require manual Parquet serialisation and schema management. `to_pandas()` round-trips perfectly with no manual JSON parsing.

### 3.7 `temperature=0` for both extractor and judge

**Decision**: Both `parser.py` and `judge.py` set `temperature=0`.

**Justification**:
- **Extractor**: structured extraction should be deterministic. The same job posting should always produce the same structured output. Stochastic variation adds noise with no benefit.
- **Judge**: score consistency is critical for meaningful version comparisons. A judge that gives different scores on the same extraction on different runs makes it impossible to tell whether a prompt change improved quality or just got lucky samples.

---

## 4. Schema Design

### `Job` model (extraction target)

Passthrough fields (copied verbatim from input, not extracted by the LLM):
- `title` — job title from the raw CSV
- `description` — original posting text
- `location` — from the explicit "Location:" field in the user message

All other fields are extracted. Key design choices:
- `seniority: Seniority` — enum enforced at validation; `unknown` is a valid value, not an error
- `job_family: JobFamily` — assigned from primary responsibilities, not job title
- `years_experience_min / max: Optional[float]` — only if explicitly stated; never inferred
- `skills_technical: Optional[list[str]]` — includes ALL named tools, categories (cloud computing, BI tools), and methodology terms (machine learning, NLP, A/B testing)
- `salary_min / max: Optional[float]` — only if stated as a number; never inferred from seniority

### `EvaluationScore` model (judge output)

17 integer dimensions (1–3 scale) across five groups, plus `flags: list[str]`:

| Group | Dimensions |
|-------|------------|
| Company | name, description, industry, remote_policy, employment_type |
| Role | seniority, job_family, years_experience, education, responsibilities |
| Skills | technical_precision, technical_recall, soft, nice_to_have |
| Compensation | salary |
| Overall | null_appropriateness, overall |

`location_accuracy` was removed (see §5.2).

---

## 5. Issues Found and Fixed

### 5.1 Circular evaluation (inflated scores)

**Symptom**: v1 eval returned suspiciously high scores (~2.96 overall on n=50).

**Root cause**: `Job.description` (the full original posting text) was included in `extracted.model_dump()` sent to the judge. The judge had the source text embedded inside the extraction JSON, making it trivially easy to verify every field.

**Fix**: `_build_user_message()` strips `title`, `description`, and `location` from the extracted dict before sending to the judge. These are passthrough fields — raw inputs, not extracted values.

**Impact**: After fix (v2), scores dropped to realistic levels.

### 5.2 Location accuracy scores — removed dimension

**Symptom**: `location_accuracy` consistently scored low even though location is a passthrough field (copied directly, not extracted by the LLM).

**Root cause (phase 1)**: The original `SYSTEM_PROMPT` said "extract as written", implying the LLM should pull location from the description body. When city was not in the description, the LLM nulled it instead of using the explicit `Location:` field.

**Fix (phase 1)**: Updated `SYSTEM_PROMPT` to explicitly use the `Location:` field from the user message.

**Root cause (phase 2)**: After making location a passthrough field, the judge still scored it but had no ground truth to compare against (location was stripped from the extracted dict).

**Fix (phase 2)**: Removed `location_accuracy` from `EvaluationScore`, `JUDGE_PROMPT`, and `SCORE_GROUPS` entirely. A passthrough field cannot be meaningfully evaluated by the judge.

### 5.3 Judge misalignment with extraction rules

**Symptom**: v4 scores were *lower* than v3 on `skills_technical_precision` (-0.18) even though the extraction prompt was relaxed to explicitly allow broad skill categories (cloud computing, BI tools) after user feedback.

**Root cause**: The judge was evaluating based on its own convention, not the extraction rules. When the extractor followed our explicit rule to include broad categories and methodology terms, the judge (using GPT-4o defaults) flagged them as "too generic" or "vague".

**User feedback**: "I think the cloud experience and bi tools are valid skills, make sure you are not imposing too hard constraints."

**Fix (v5 judge)**: Rewrote `JUDGE_PROMPT` to include the full extraction rules verbatim under an "EXTRACTION RULES THE EXTRACTOR FOLLOWED" header. The judge now evaluates compliance with the stated rules, not its own opinion. Key additions:
- Full seniority priority ladder with year-to-level mapping
- Explicit statement that broad categories AND methodology terms are expected in `skills_technical`
- "When in doubt, score 2 not 1" guidance for dimensions where the judge can't verify from description alone (e.g. industry classification where sector is genuinely ambiguous)

---

## 6. Prompt Version History

| Version | n | seed | Overall | pct_score_1 | skills_soft | Key change |
|---------|---|------|---------|-------------|-------------|------------|
| v1 | 50 | 42 | ~2.96 | — | — | Baseline — circular eval bug (invalid) |
| v2 | 30 | 42 | — | — | — | Fixed circular eval; removed location_accuracy |
| v3 | 50 | 42 | 2.54 | 36% | 2.52 | Clean baseline |
| v4 | 50 | 42 | 2.40 | 42% | 2.40 | Relaxed skills rules — judge misalignment exposed |
| v5 | 50 | 42 | 2.92 | 10% | 2.44 | Judge rewritten with full extraction rules; temperature=0 |
| v6 | 50 | 42 | 2.78 | 18% | 2.50 | Regression: preferred skills rule broke skills_technical recall |
| v7 | 50 | 42 | 2.90 | 12% | 2.44 | Fixed: preferred skills belong in both fields |
| v8 | 50 | 42 | 2.84 | 18% | 2.36 | Regression: job_family enum in extraction prompt hurt attention |
| v8b | 50 | 42 | 2.90 | 12% | 2.36 | Fixed judge contradiction; enum removed from extractor |
| **v9** | 50 | 42 | **2.92** | 22% | **2.84** | Inclusive skills_soft default; title-first job_family |
| v9b | 50 | 123 | 2.88 | 24% | 2.90 | Cross-seed validation |
| v9c | 50 | 999 | 2.88 | 32% | 2.94 | Cross-seed validation |
| v10 | 50 | 42 | 2.86 | 30% | 2.90 | Glassdoor hint experiment — judge saw hint, penalised overrides |
| v10b | 50 | 42 | 2.86 | 24% | 2.92 | Hint hidden from judge — skills_technical still regressed |
| v10c | 50 | 42 | 2.92 | 20% | 2.80 | Hint removed entirely — v9 parity confirmed; reverted |
| v9d | 44 | 42 | 2.91 | 23% | 2.84 | v9 re-validation; n=44 due to 6 judge TPM failures |
| v9e | 47 | 123 | 2.89 | 23% | 2.89 | v9 re-validation |
| v9f | 47 | 999 | 2.85 | 23% | 2.96 | v9 re-validation |
| **v9g** | **50** | **42** | **2.98** | **10%** | **2.82** | **Fixed judge** — anti-anchoring + forced recall enumeration. **Canonical baseline.** |
| v9h | 50 | 123 | 2.94 | 18% | 2.90 | Fixed judge cross-seed validation |
| v9i | 50 | 999 | 2.88 | 18% | 2.94 | Fixed judge cross-seed validation |

### v6 regression: preferred skills rule
`skills_technical_recall` dropped -0.28 after adding a "preferred skills → nice_to_have only" rule. The extractor interpreted this as a reason to exclude preferred skills from `skills_technical`. Fix: clarified that preferred-only skills belong in **both** fields — `skills_technical` is exhaustive.

A judge contradiction was also introduced in v6: the `skills_technical_precision` dimension said "preferred-section skills must not appear here", directly opposing the correct rule. Fixed in v8b.

### v8/v8b regression: skills_soft worst-ever (2.36)
Two compounding problems:
1. Adding job_family enum descriptions to the extraction prompt (v8) consumed attention and hurt multiple dimensions.
2. The `Field(description=...)` for `skills_soft` in `models.py` said "Null if only generic filler with no qualifier" — a restrictive default that contradicted the system prompt's "when in doubt, include".

Fix (v9): removed enum from extractor prompt (kept in judge only), and flipped the `skills_soft` Field description to inclusive.

### v10 experiment: Glassdoor industry hint

**Hypothesis**: Injecting the Glassdoor `Industry` label as context in the extractor prompt would improve `industry` extraction, which is the weakest remaining dimension (~2.66–2.76 across seeds).

**Ground-truth test** (`tests/test_industry_extraction.py`): With the hint, exact-match accuracy rose from 36% → 78% on 50 samples. Clearly useful information.

**Judge eval result (v10)**: `industry_accuracy` *dropped* from 2.76 → 2.44. The judge saw the hint in the user message and held the extractor to it strictly — any case where the extractor correctly overrode the hint (e.g. a staffing agency posting for a pharma client, where the correct industry is "Pharmaceutical" not "Staffing") was penalised.

**Fix attempt (v10b)**: Hide the hint from the judge, pass it only to the extractor. `industry_accuracy` remained low (2.42), and `skills_technical` regressed (2.96→2.96 precision but visible noise). The added context in the user message appeared to pull attention away from skills.

**Fix attempt (v10c)**: Different injection mechanism (system prompt addendum), judge still blind. Same `skills_technical` regression.

**Conclusion**: The Glassdoor hint is genuinely useful but the cost (attention dilution on skills fields) outweighs the benefit within the current prompt architecture. `industry_accuracy` in the judge eval is also unreliable regardless — the Glassdoor taxonomy is itself noisy (staffing agencies labelled as the industry they recruit for, labels like "Accounting" on data-tech companies). Reverted fully to v9.

### v9: key prompt engineering findings
- **`Field(description=...)` values are a second prompt channel** — `instructor` passes them to the LLM as JSON schema. A mismatch between the system prompt rule and the Field description causes the model to hedge, producing under-extraction.
- **Inclusive defaults outperform restrictive defaults for fuzzy fields** — for `skills_soft`, "include if the employer emphasises it" outperformed "null unless qualifier". The LLM's language understanding is an asset here; fighting it with prescriptive nulling rules hurts quality.
- **Title-first for job_family** — mirroring the seniority priority ladder (title keyword → responsibilities → other) improved `job_family` from 2.72 to 2.82. Title IS the primary signal.

---

## 7. Evaluation Design

### Sample size: 50

30 samples gives ~85% power to detect a 0.2-point shift in overall score at α=0.05. 50 samples improves this to ~92% and is still affordable (50 × 2 LLM calls = 100 API calls per run). 25 was considered too low given the noisiness of 1–3 integer scores.

### Judge model: gpt-4o

The judge needs to assess nuanced extraction quality — industry classification, seniority ladder application, skills completeness. `gpt-4o-mini` lacks the reasoning depth needed for consistent judgement on edge cases.

### Seeded sampling

`seed=42` ensures the same 50 rows are drawn on every run, making version comparisons valid. A different seed would change which rows are sampled and could mask real improvements or introduce spurious differences.

---

## 8. Judge Bias Analysis

### Precision/recall coupling

`skills_technical_precision` and `skills_technical_recall` have been exactly equal in every run from v6 onwards (confirmed by inspecting `trend.csv`). Before v5, when the judge used its own conventions, they diverged. After v5's judge rewrite with full extraction rules, they locked.

**Root cause**: the judge cannot evaluate recall independently. To assess recall it must first enumerate all skills in the description — which is the same task as the extractor. Since both models share training distribution, they have the same blind spots. In practice the judge answers one question ("is this skills list good?") and assigns the same answer to both dimensions. They are not independent measurements.

**Implication**: `skills_technical_recall` is not a reliable measure of completeness. It is useful for regression detection (if it drops, something broke) but not as an absolute completeness score. The human ground-truth eval converts recall into a real set comparison and is the correct fix.

**Fix attempted (v9g, 2026-03-30)**: added a forced-enumeration instruction to the `skills_technical_recall` dimension: *"Before scoring: mentally enumerate every technical skill present in the description, then check what the extractor missed. Base your score only on omissions."* Result: precision and recall remained locked at 2.98/2.98 across all three validation seeds — zero measurable effect.

**Confirmed diagnosis**: the locking is a **ceiling effect**, not a prompt gap. The extractor is genuinely near-perfect on skills at n=50, so both metrics independently converge to ~2.98 regardless of how they are scored. Forced enumeration would only matter on a sample where the extractor has systematic recall failures.

### Ceiling effects — dimensions with no discriminative power

Analysis of score ranges across all 17 runs (`max - min`):

| Dimension | Range | Assessment |
|-----------|-------|------------|
| `company_name_accuracy` | 0.040 | Dead — always ~3.0. Company name is either present or not. |
| `salary_accuracy` | 0.040 | Dead — always ~3.0. Salary is either stated or not. |
| `responsibilities_quality` | 0.100 | Near-dead — instructions are clear, extractor consistently meets the bar. |
| `employment_type_accuracy` | 0.140 | Low signal. |
| `remote_policy_accuracy` | 0.160 | Low signal. |

These dimensions consume judge attention without providing regression detection value. In a future judge revision, consider consolidating them or removing them to free attention budget for higher-signal dimensions.

High-signal dimensions (range ≥ 0.35): `skills_soft_accuracy` (0.597), `null_appropriateness` (0.767), `overall` (0.720), `skills_technical_precision/recall` (~0.54–0.59), `seniority_accuracy` (0.460), `industry_accuracy` (0.360).

### `overall` ↔ `null_appropriateness` coupling (r = 0.979)

`overall` and `null_appropriateness` are correlated at r = 0.979 across all runs — near-perfect. `seniority_accuracy` is also tightly coupled to both (r ≈ 0.96).

**Root cause**: the judge appeared to anchor its holistic `overall` judgment primarily on null handling and seniority compliance, rather than forming a genuinely independent quality assessment.

**Fix applied (v9g, 2026-03-30)**: added an anti-anchoring instruction to the `overall` dimension: *"Do not anchor on null_appropriateness — that is scored separately. Weight every group equally; penalise any group with clear rule violations."*

**Outcome**: `overall` improved consistently (+0.07 seed=42, +0.05 seed=123, +0.03 seed=999). The gap between `overall` and `null_appropriateness` narrowed. Residual correlation is genuine signal (good extractions tend to handle both nulls and all other fields correctly) — the contamination portion has been reduced.

**Implication**: For version comparisons, group-level means (Company, Role, Skills, Compensation) remain more informative than the single `overall` score. `overall` is now better calibrated but still not fully independent of `null_appropriateness`.

### Industry ground-truth test (`tests/test_industry_extraction.py`)

The raw CSVs contain Glassdoor-sourced `Industry` (specific) and `Sector` (broader) columns — the only structured ground-truth labels in the dataset. These are used to evaluate the extractor's `industry` field directly.

Since the extractor produces free-form text ("Insurance") while the ground truth has its own taxonomy ("Insurance Carriers"), a lightweight LLM comparison call is used rather than string matching.

Scoring: 2 = matches `Industry`, 1 = matches `Sector` only, 0 = wrong, -1 = null.

This is the first evaluation in the project with an objective reference — the result cannot be inflated by shared model blind spots.

---

## 9. Stage 2 — Schema Redesign and Prompt Engineering (v16+)

### 9.1 Why v9 was not selected for the full batch run

After completing the v9 evaluation series, a human audit of the v9g extractions revealed three systematic problems that had been masked by the LLM-as-a-Judge:

1. **skills_technical/nice_to_have boundary failure**: The extractor frequently duplicated items across both fields or made inconsistent required/preferred judgements. The distinction between `skills_technical` (required) and `nice_to_have` (preferred) was structurally ambiguous — the model had no reliable signal to distinguish them from context alone.

2. **Soft skills contaminating skills_technical**: Items like "communication", "leadership", and "facilitation" regularly appeared in `skills_technical`. The judge was not catching this as an error.

3. **`industry` field unreliable**: The Glassdoor `Industry` label was the only available ground truth, but the label itself is noisy (staffing agencies labelled as the industry they recruit for). The judge was evaluating against its own interpretation, not any objective standard, making `industry_accuracy` meaningless as a signal.

**Decision**: Drop `industry`, redesign the skills schema, and treat v9g as a stage 1 reference point rather than the production prompt.

### 9.2 Schema redesign (v16 breaking change)

The skills schema was redesigned from two fields to three:

| Old (v1–v15) | New (v16+) |
|---|---|
| `skills_technical` — required tech skills | `skills_required` — required tech + domain skills |
| `nice_to_have` — preferred skills | `skills_preferred` — optional/desirable skills |
| `skills_soft` — soft skills | `skills_soft` — interpersonal skills (condensed phrases) |
| `industry` — company sector | *(removed)* |

The key improvements:
- `skills_required` explicitly includes **domain expertise areas** (investment finance, security analytics, regulatory compliance) alongside precise tool tokens — senior roles often have no listed tool requirements, only domain competencies.
- A **HARD BOUNDARY** between `skills_required` and `skills_soft` prevents soft skills from leaking into technical skill lists.
- `skills_soft` requires **condensed phrases (2–7 words)**, not verbatim sentences.
- All three skill fields are evaluated by the judge as a single cohesive group.

**Note**: v16+ scores are not comparable to v1–v15. The schema change resets the baseline.

### 9.3 Judge limitations identified through human evaluation

A human evaluation of 10 v20 extractions (seed=42) revealed systematic divergences between human and judge scores:

| Dimension | Human avg | Judge avg | Gap |
|---|---|---|---|
| `skills_soft_accuracy` | 3.0 | 1.9 | −1.1 |
| `seniority_accuracy` | 3.0 | 2.6 | −0.4 |
| `skills_required_accuracy` | 2.8 | 2.2 | −0.6 |
| `skills_preferred_accuracy` | 2.8 | 2.5 | −0.3 |

Human assessment: **extraction quality was genuinely excellent** across all 10 reviewed jobs. The judge was systematically over-penalising.

**Root causes identified:**

1. **skills_soft format penalty too harsh**: The judge was scoring 1 (clearly wrong) on items that were correct in content but slightly verbose in format. Fix: format issues cap the score at 2; score 1 is reserved for content errors (Agile/Scrum in this field, or null when the posting clearly emphasises soft skills).

2. **Seniority inference over-penalisation**: The judge was calling reasonable inferences wrong (scoring 1 on rows where human scored 3). Fix: score 1 only when the extracted value is **clearly contradicted** by explicit signals in the posting.

3. **Abstract rubrics insufficient for calibration**: Without concrete anchor examples, the judge drifted toward strictness on interpretive fields. Few-shot calibration examples would improve this further, but were not added to avoid overfitting to the specific 10-row human eval sample.

**Approach taken**: Fix the structural flaws in the judge (score-1 thresholds, format vs content separation) rather than adding specific examples, to preserve generalisation.

### 9.4 Prompt engineering decisions (v16–v21)

**Decisions confirmed during this stage:**

- **"Do not paraphrase or interpret" removed**: This instruction conflicted with legitimate semantic judgment required for seniority inference, skills classification, and optional framing detection. Replaced with a nuanced rule: semantic judgment is explicitly allowed only where the field rules require it; all other fields extract faithfully.

- **Responsibilities scanning for implicit skills**: A common failure mode was the extractor missing tools named in responsibility bullets (e.g. "Optimise jobs to utilise Kafka, Hadoop, Spark Streaming and Kubernetes" — all four are required skills). Explicit instruction added: scan the entire posting including responsibilities; tools named there are implicitly required.

- **"Most important 7" → "first 7 listed"**: Selecting the "most important" responsibilities introduces run-to-run variance. The first 7 listed is consistent and approximately correct (postings lead with their most important responsibilities).

- **Emphasis words ≠ required**: "Strong knowledge of X" or "proficiency in Y" describe the desired level of a skill, not whether it is required. Added to both skills_required and skills_preferred to prevent misclassification based on wording intensity alone.

- **AVP → senior (not director)**: In banking and finance, AVP (Associate Vice President) is an early-to-mid career title. The original mapping (AVP → director) produced systematic errors for finance-sector postings.

- **"Data Scientist" treated as ambiguous**: Despite having a clear title keyword, "Data Scientist" responsibilities span data_science, data_engineering, and ml_engineering. Explicitly noted as an exception to the title-first rule.

- **Product management under management**: Product Manager titles don't trigger the `manager` seniority path (not a people-management role) and map to the `management` job_family via the product management clarification added to that category's description.

### 9.5 Stage 2 version trajectory

| Version | overall | skills_required | skills_preferred | skills_soft | responsibilities | n_flags | Key change |
|---------|---------|----------------|-----------------|-------------|-----------------|---------|------------|
| v16 | 2.88 | 2.78 | 2.80 | 2.52 | 2.98 | 15 | Schema redesign baseline |
| v17 | 2.76 | 2.44 | 2.76 | 2.62 | 2.94 | 36 | company_name extraction fix; judge stricter post-redesign |
| v18 | 2.68 | 2.44 | 2.80 | 2.42 | 2.88 | 42 | HARD BOUNDARY for soft skills in skills_required |
| v19 | 2.68 | 2.34 | 2.72 | 2.30 | 2.88 | 44 | skills_soft condensing instruction added |
| v21 | **2.80** | 2.48 | **2.82** | 2.48 | **3.00** | **25** | Full prompt polish + judge recalibration |
| v22 | 2.80 | 2.40 | 2.74 | 2.30 | 3.00 | 21 | temperature=0.3 — skills regressed, reverted |
| v20b | 2.80 | 2.46 | 2.80 | 2.52 | 3.00 | 21 | v20 extractor + v21 judge — plateau confirmed |
| v23 | — | — | — | — | — | — | Three targeted fixes: seniority verb/title, Senior+Manager, leadership exclusion + 6 structural refinements (extraction-only) |
| **v24** | — | — | — | — | — | — | Schema field completion (remote_policy, employment_type, salary_min/max rules); analyst catch-all for job_family; CRITICAL dual-field skills/responsibilities rule. Extraction-only, manual eval pending. |

v17–v19 downward trend was driven by two compounding factors: (1) the judge became stricter after the schema change exposed new failure modes it could evaluate, and (2) the HARD BOUNDARY instruction caused format regressions in skills_soft (verbatim sentences instead of condensed phrases). v21 recovers through judge recalibration and prompt refinement.

**v21 notable results**:
- `responsibilities_quality` hits 3.00 — first perfect score for this dimension
- `skills_preferred_accuracy` at 2.82 — new stage 2 high
- n_flags down from 44 (v19) to 25 — 43% reduction
- Human evaluation confirmed extraction quality is genuinely excellent; remaining judge gaps are in interpretive fields (skills_soft, seniority)

**Current canonical reference: v21 (seed=42)**

### 9.6 Plateau analysis — v22, v20b (2026-03-31)

After v21, two further experiments were run to understand whether the skills_required regression from v16 (2.78) could be recovered:

**v22 — temperature=0.3 (extractor only, judge unchanged)**

Hypothesis: temperature=0 forces overly literal extraction for a task requiring semantic judgment. Raising temperature might improve skills allocation.

Result: skills regressed across all three skills dimensions, overall unchanged at 2.80.

| | v21 (t=0) | v22 (t=0.3) |
|---|---|---|
| overall | 2.80 | 2.80 |
| skills_required | 2.48 | 2.40 |
| skills_preferred | 2.82 | 2.74 |
| skills_soft | 2.48 | 2.30 |

Temperature adds variance but the model makes worse allocation decisions on average, not better. Hypothesis rejected — the issue is not literal extraction. Reverted to temperature=0.

**v20b — v20 prompt re-run with v21 judge**

To determine whether the v21 extractor changes (responsibilities scanning paragraph, emphasis words note) were helping or hurting relative to v20, v20 was re-run against the same seed=42 sample using the current (v21-calibrated) judge.

| | v16 | v20b | v21 | v22 |
|---|---|---|---|---|
| overall | 2.88 | 2.80 | 2.80 | 2.80 |
| skills_required | 2.78 | 2.46 | 2.48 | 2.40 |
| skills_preferred | 2.80 | 2.80 | 2.82 | 2.74 |
| skills_soft | 2.52 | **2.52** | 2.48 | 2.30 |
| n_flags | 15 | 21 | 25 | 21 |

**Key finding**: three structurally different prompts (v20b, v21, v22) all plateau at overall=2.80. The v21 extractor additions had no meaningful effect on skills_required (2.46 vs 2.48) and slightly hurt skills_soft (2.52 → 2.48). v20b recovers skills_soft to 2.52, matching the v16 baseline.

**Interpretation**: The skills_required gap from v16 (2.78 → ~2.46) is persistent across all prompt variants, including the original v20. This suggests the gap is not caused by the v21 extractor additions but rather by judge drift following the schema change — the v21-calibrated judge applies a stricter standard to skills_required than the v16-era judge did. Further prompt iteration within this parameter space is unlikely to recover the gap.

**Initial decision**: batch with v20b. However, this decision was based partly on a single edge case (the Kafka/Hadoop posting performing worse in v21 than v20). Given inherent LLM variability even at temperature=0, a single posting is not a reliable signal.

**Revised decision**: restore v21 prompt (= v22 prompt text), conduct a final critical review, apply only changes that could meaningfully mislead the model, then run extraction-only as v23. A proper manual evaluation on the first 10 jobs will make the final batch prompt decision on human evidence, not judge scores or individual edge cases.

**Current canonical reference: v21 (seed=42, overall=2.80) — pending manual eval of v23**

### 9.7 Final prompt review — v23 (2026-03-31)

After restoring the v21/v22 prompt, a final exhaustive review was conducted before batch commit, targeting seniority and skills fields (the highest-stakes dimensions). The goal: identify any phrasing that could cause the model to be biased, confused, or misled — particularly rules that feel like hard constraints when they should be guiding heuristics.

Three targeted fixes were applied:

**1. Seniority: "Lead" as verb vs. title keyword (step 1)**

Original: The list of title patterns did not distinguish "Lead" appearing as a title keyword from "Lead" appearing as a verb in the description body (e.g., "lead a team of analysts", "will lead cross-functional projects"). A model primed by step 1 could incorrectly trigger on these.

Fix: Added an explicit carve-out — "The patterns below apply to the job title; 'Lead' and similar words used as verbs in the description body are NOT seniority signals."

**2. Seniority: Senior + Manager title conflict (step 1)**

Original: The rule for "Manager" in the title returned `manager`, but the rule for "Senior" also returned `senior`. For titles like "Senior Analytics Manager" or "Senior Engineering Manager", a model applying both rules faces ambiguity.

Fix: Added an explicit tie-breaker — "When a title combines a rank modifier with a management keyword (e.g. 'Senior Analytics Manager', 'Senior Engineering Manager'), the management keyword takes precedence — return manager."

**3. skills_required: unqualified "leadership" exclusion**

Original: The exclusion list for soft skills said "leadership" must not appear in skills_required. This was too broad — concrete leadership experience stated as a role requirement (e.g., "experience leading data engineering teams", "technical leadership of ML projects") is a domain competency, not a soft skill.

Fix: Qualified the exclusion with an explicit distinction — "leadership as an interpersonal trait (e.g. 'strong leadership skills', 'natural leader') — note: concrete leadership experience stated as a role requirement (e.g. 'experience leading data engineering teams', 'technical leadership of ML projects') is a domain competency and belongs here."

**v23 vs v20 full diff summary (6 changes total)**:
1. `company_name`: added "Return null (not the string 'null')" — defensive normalisation
2. `seniority` step 1: "Intern ..." or "... Intern" or "internship" → intern (explicit internship keyword)
3. `seniority` step 1: "Lead" as verb carve-out + Senior+Manager tie-breaker (v23 additions)
4. `education_required`: added "If the posting adds 'or equivalent experience', retain it"
5. `skills_required`: added emphasis words note ("strong", "proficiency in" describe level, not required vs preferred) + responsibilities scanning paragraph + qualified leadership exclusion (v23 addition)
6. `salary_period`: added "Infer from context (e.g. a six-figure figure with no qualifier → annual)"

**Extraction-only run**: v23 run as seed=42, n=50, judge=False. Pending manual evaluation of the first 10 jobs before batch commit.

### 9.8 Final batch prompt — post-v23 structural refinements (2026-03-31)

After the v23 extraction run, a second review pass was conducted using extended-thinking feedback (Claude Opus). Six structural improvements were identified and applied to the prompt. These target edge cases and under-specified paths rather than directional changes — no new eval run was needed.

**1. Explicit seniority enum**

Added a valid-values line at the top of the seniority section: `intern, junior, mid, senior, lead, principal, manager, director, unknown` in ascending order. The enum was previously implicit, and `mid` only appeared inside the years mapping. Makes the "adjust up by one level" instruction unambiguous.

**2. Scope-based seniority anchors for the no-years case**

Step 2 previously said "assess responsibilities alone using the same scope signals" with no baseline to anchor from. Added explicit mappings: individual contributor executing defined tasks → junior; competent IC with some ownership of specific components → mid; owns a system or domain area, or mentors others → senior; cross-team technical authority or architectural ownership → lead. Default to mid if responsibilities describe competent IC work with no clear scope signals.

**3. Default for unlabelled skills**

Made explicit what was previously implicit: skills listed without any optional framing default to `skills_required`. Absence of the word "required" is not sufficient to classify a skill as preferred — there must be a positive signal of optionality.

**4. Conflict resolution rule**

Added: "If the same skill appears in both a required context (responsibilities section, required skills section) and a preferred/optional context, classify it as skills_required — the stronger signal takes precedence." This handles a real pattern in poorly structured postings.

**5. Sharpened leadership boundary**

The original carve-out ("concrete leadership experience stated as a role requirement belongs in skills_required") left grey areas like "leading cross-functional initiatives." Sharpened the test: leadership belongs in skills_required only when it specifies what is being led in technical or domain terms. Leadership framed around people dynamics or influence without a technical object belongs in skills_soft.

**6. Skill name normalisation**

Added a normalisation instruction: normalise to the most commonly used professional form (e.g. "Amazon Web Services" → "AWS", "Python 3" → "Python", "MS Excel" → "Excel"). Prevents noisy duplicates at scale.

**This is the final batch prompt.** The v23 extraction (seed=42, n=50) is the validation sample for manual evaluation. If the manual eval confirms extraction quality, this prompt is used as-is for the full ~3,892 DS record batch and for all future data ingestion runs.

### 9.9 v24 — Schema field completion and prompt reinforcement (2026-04-01)

A review of every field in `models.py` against the system prompt revealed three fields with no extraction rules — only `Field(description=...)` hints, which are insufficient procedural guidance. Four additional prompt fixes were applied.

**Schema gaps filled:**

- **`remote_policy`**: No system prompt rule existed. Added: explicit-only extraction, normalise to Remote / Hybrid / On-site, null if not stated. `Field()` description was already present but relied solely on the schema hint.
- **`employment_type`**: No system prompt rule existed. Added: explicit-only extraction, normalise to Full-time / Part-time / Contract / Casual / Temporary (may appear in title or body), null if not stated.
- **`salary_min` / `salary_max`**: The compensation section had only a general preamble ("only if explicitly stated"). Added field-level rules covering range semantics: stated range → min/max split; open-ended ("$80k+") → min = stated number, max = null. Also added `Field()` descriptions to both (were bare `= None`). Judge prompt updated to match.

**Prompt reinforcements:**

- **`job_family` analyst catch-all**: "Data Analyst" was the only explicit mapping. All other analyst-type titles (Business Analyst, Financial Analyst, Operations Analyst, etc.) fell through to `other`. Added: "Any role with 'Analyst' in the title → data_analytics, unless the title also contains a more specific family keyword that takes precedence (e.g. 'Data Science Analyst' → data_science, 'ML Analyst' → ml_engineering)."

- **`skills_required` dual-field extraction (CRITICAL)**: The original "Important:" note at the end of the skills_required rule was being deprioritised. Upgraded to a CRITICAL-labelled instruction and made explicit that the same sentence may simultaneously populate `key_responsibilities` AND `skills_required` — this is correct behaviour, not double-counting. Added: "For example (one of many possible cases)..." to generalise the example and prevent the model from treating named tokens as the exhaustive case.

**Extraction run**: seed=42, n=50, judge=False — saved as `v23-final-updated`, corresponds to v24. Manual eval pending.

### 9.10 Model upgrade — gpt-5.4-mini (2026-04-01)

After confirming v24 prompt stability, the extraction model was upgraded from `gpt-4o-mini` to `gpt-5.4-mini`.

**Motivation**: gpt-5.4-mini supports structured outputs via the OpenAI API (compatible with `instructor`), making it a drop-in replacement. Initial test run (seed=42, n=50) completed in ~1.5 minutes vs ~4.5 minutes for gpt-4o-mini — **~3× faster** with no API errors.

**Issue discovered**: gpt-5.4-mini's higher instruction compliance caused unintended noise in `skills_required`. The CRITICAL dual-field rule ("the same sentence may contribute to two fields") was being interpreted too broadly — the model was pulling full responsibility phrases into `skills_required` rather than extracting only the named skill tokens embedded within them.

**Prompt adjustments made for gpt-5.4-mini:**

1. **CRITICAL block rewritten** — made explicit that only discrete skill tokens transfer from responsibilities ("not the responsibility itself"), and that "generic verbs, actions, and descriptions do not" transfer.
2. **`skills_required` opener tightened** — "technical and domain knowledge" → "technical and critical domain skills"; "A skill named" → "A core skill named"; "broader knowledge domain areas" → "key knowledge domain areas". These qualifiers reduce noise on a more compliant model without changing the intended extraction scope.
3. **`employment_type`** — added "Do not infer." as an explicit reinforcement (was implicit from "only extract if explicitly stated").
4. **`skills_preferred`** — "domain expertise areas" → "key domain skills" for consistency with the tightened skills_required language.

**Current state**: `gpt-5.4-mini` is the production extraction model. Prompt version `v24-gpt5.4-mini` (seed=42, n=50, extraction-only) pending manual evaluation.

### 9.11 v25 — skills_preferred systematic failure and prompt fixes (2026-04-02)

Manual evaluation of v24-gpt5.4-mini extractions (8 jobs reviewed) revealed a single systematic failure mode affecting approximately half of the reviewed postings: **skills_preferred misclassification**.

Two distinct patterns were identified:

**Failure 1: Proficiency/level modifiers overriding section placement**

Skills explicitly placed in a preferred or "nice to have" section were being extracted into `skills_required` when described using strong proficiency language — e.g. "proficiency in Scala is a plus", "deep knowledge of Kubernetes would be an advantage", "fluency in Spark is ideally desired". The extractor was treating the modifier (proficiency, fluency, deep knowledge) as a signal of requirement level, overriding the clear optionality signal in the surrounding language.

Root cause: the existing modifier rule ("emphasis words describe level, not required vs preferred") was stated only within `skills_required` as a caveat, and was not reinforced at the point of decision in `skills_preferred`. The model was reading the level modifier before encountering the optionality signal, and classifying accordingly.

**Failure 2: Same skill token duplicated across required and preferred**

When a posting listed a broad skill (e.g. "ML") as required in one section and a specific variant ("ML applications") as preferred in another, the extractor was producing the same short token ("ML") in both fields. This created duplicates and violated the intended field semantics.

**Fixes applied (4 targeted prompt changes):**

1. `skills_required` modifier rule: extended examples list to include "deep knowledge of", "excellent understanding of"; added explicit carve-out: "This applies within unframed or required sections only; a skill placed within an explicitly preferred/optional section is always skills_preferred regardless of these modifiers alone — note that if that same skill token also appears in a required context elsewhere in the posting, the deduplication rule below takes precedence."

2. `skills_required` deduplication rule (CRITICAL, new): "Never repeat the exact same literal skill token across skills_required and skills_preferred. If the exact same token would appear in both, place it in skills_required only. When required and preferred contexts describe related but distinct aspects of a broader skill area, you must enrich each token with enough qualifying words so that the two stored strings are literally different (e.g. 'classical ML' vs 'ML model deployment at scale')."

3. `skills_preferred` deduplication mirror (CRITICAL, new): Explicit instruction not to repeat verbatim tokens from `skills_required`, placed within the `skills_preferred` rule where the decision is made. Includes examples showing the enrichment pattern in context: "a posting that requires Python and also states 'Python for distributed computing is a huge plus' → 'Python' in skills_required and 'Python for distributed computing' in skills_preferred."

4. `skills_preferred` proficiency modifier rule (CRITICAL, new): "Words that describe the desired proficiency level of a skill (how good the candidate should be at it) are entirely separate from whether the skill is required or preferred. When any proficiency descriptor appears alongside a clear optionality signal, the skill is preferred — the proficiency word only tells you how strong a candidate should ideally be, not that the skill is a requirement." Includes direct examples matching observed failure patterns.

**Design principle applied**: all changes are stated as generalisable principles with illustrative examples, not as pattern-matched rules for specific words. This avoids over-engineering the prompt toward observed edge cases and improves generalisation.

**Prompt coherence review**: Before running v25, a full cross-field review of the skills section was conducted to check for contradictions introduced by the new rules. One tension found: the word "always" in the modifier carve-out could conflict with the deduplication rule when a skill appears in both a preferred section and a required context. Fixed by scoping: "always skills_preferred regardless of these modifiers alone — if that same token also appears in a required context, the deduplication rule takes precedence."

**v25 extraction run**: seed=42, n=50, judge=False. Output: `eval_results/20260402_020344_v25/extractions.jsonl`. Manual evaluation in progress.

### 9.12 v26–v27 — Prompt architectural redesign (2026-04-02)

Human evaluation of v25 extractions revealed that the targeted patch approach had reached its limits. While v25 addressed the two identified failure modes, the accumulated CRITICAL rules, cross-field references, and patch-on-patch structure created a new problem: skills were being extracted as a "random box of tokens" — the model was capturing almost anything listed as required regardless of whether it was a genuine skill. The enrichment exception in the deduplication rule was also being over-applied, tilting preferred skill extraction toward the exception path rather than the default omit path.

**Root cause**: The v24–v26 prompt had accumulated layers of targeted fixes that had become mutually reinforcing in unintended ways. Each patch addressed a specific failure while introducing new ambiguity at the edges of other rules. The classification logic was spread across three field definitions with cross-references between them, requiring the model to hold interacting constraints simultaneously while extracting.

**v26 — intermediate attempt**: A decision-tree structure was introduced but without a definition of what constitutes a skill. The model applied the tree correctly but to the wrong inputs — it classified everything in the posting, not just skill tokens.

**v27 — full architectural redesign**: The entire skills section was rewritten as a three-stage framework, separating concerns that had been conflated:

**Stage 1 — Skill definition gate**: Before any classification, a token must pass a skill definition test. A skill is a capability a candidate would credibly list on their CV, falling into: (a) named technology/tool/platform, (b) named framework/library/language feature, (c) named methodology/standard, (d) domain expertise area. Explicit exclusions: job duties disguised as skills ("deliver insights", "build scalable systems"), vague trait-adjacent descriptors ("analytical mindset", "data-driven thinking"), and industry sectors used as company context rather than required candidate knowledge.

**Stage 2 — Soft skill routing**: Any token matching interpersonal/behavioural/organisational patterns routes directly to skills_soft before any required/preferred classification. Hard boundary with explicit tie-breaker: "when in doubt whether a token is soft or technical, route it to skills_soft."

**Stage 3 — Required vs preferred classification**: Rebuilt around two key architectural decisions:
1. **Scope concept**: An optionality signal has a scope. A scope-opening signal (e.g. "Preferred:", "Nice to have:") opens a preferred context window for all skills that follow, until text clearly shifts to a new topic or requirement context. An inline signal applies only to the adjacent skill. This directly addresses the systematic failure where postings with a "Preferred skills" section were having individual skills within it misclassified as required.
2. **Proficiency modifiers declared invisible**: Words like "strong", "proficiency in", "deep knowledge of", "fluency in" are explicitly described as orthogonal to the required/preferred decision. They do not open, close, or override any optionality context window.
3. **Required is the default**: "Required is not something you detect — it is what remains after preferred skills have been identified."
4. **Deduplication as post-classification step**: Moved to Step 4, after all classification is complete, making it a clean final check rather than an interleaved constraint.

**Design principle**: rather than adding rules for observed failure patterns (the patch approach), the redesign defines the reasoning process the model should follow. Examples illustrate patterns, not exhaustive cases.

**v27 extraction run**: seed=42, n=50, judge=False. Output: `eval_results/20260402_031323_v27/extractions.jsonl`. Manual evaluation in progress.

### 9.13 v28 — Schema-enforced chain-of-thought and structural simplification (2026-04-02)

Human evaluation of v27 extractions revealed that the three-stage decision tree, while logically sound, still failed intermittently on preferred classification — the same root failure mode as v24–v26. Diagnosing this led to a fundamental insight about how small LLMs process long prompts, which drove the most significant architectural change in the entire project.

#### Why simpler prompts lead to better output

This is counterintuitive if you think of the LLM as a rule engine — more rules should mean more precise behaviour. But a small LLM has a finite attention budget. Every token in the prompt competes for attention during generation. The v27 skills section was ~250 lines. When the model is filling `skills_preferred`, it is not attending equally to all 250 lines — it attends most strongly to what is recent and prominent, and less to what is buried deep.

The proficiency-vs-optionality rule was the most important rule in the entire skills section, and it was buried 150 lines into the skills section, inside a CRITICAL block, after stages, steps, scope types, and hierarchy explanations. By the time the model reached the point of generating `skills_preferred`, that rule had been pushed out of effective attention range by everything that came after it.

**The patch paradox**: every time a rule was added to fix the proficiency problem, it made the problem worse, because the new rule pushed the original proficiency rule even further from the generation point. The asymmetric hierarchy explanation, the processing order, the grammatical form paragraph — each was correct in isolation but collectively they diluted attention on the one thing that mattered. Rules do not stack in an LLM the way they stack in code. They compete.

The simplified prompt works better because the optionality-vs-proficiency distinction is now the first thing in the skills section, not the last. The model reads it, and there are only ~60 more lines before it starts generating — not 150. Less dilution, stronger signal at generation time.

#### Why preferred signals are stored in the schema

The core failure was a sequencing problem. With instructor, the model fills fields in schema declaration order. In the old schema, the model would hit `skills_required` first and start generating. At that point it had not systematically thought about which skills were preferred — it was making classification decisions on the fly, skill by skill, while also trying to retain 250 lines of rules. By the time it reached `skills_preferred`, it had already committed most skills to required.

Two scaffolding fields were added to enforce this. The model's generation order is now:

1. Fill `responsibility_skills_found` → scan every responsibility bullet and write down all embedded skill tokens
2. Fill `preferred_signals_found` → write down every optionality phrase in the posting
3. Fill `skills_preferred` → FILL FIRST from skills, using preferred zones as anchors (bounded blast radius — see below)
4. Fill `skills_required` → everything not already in preferred, plus all responsibility-embedded tokens
5. Fill `skills_soft` → interpersonal and behavioural skills

The model's own output becomes its working memory. It cannot forget the preferred zones because they are in the tokens it just generated, which are in its context window during subsequent field generation. This is the difference between "hold these abstract rules in mind while generating" and "look at what you just wrote down."

#### Why not extract all skills first, then classify?

That would work — same principle of separating extraction from classification. But it would require either two API calls (doubling cost and latency) or a complex intermediate schema. The two scaffolding fields are the minimal version of that idea: instead of extracting all skills into a flat list and reclassifying, they extract just the reasoning inputs — the responsibility-embedded tokens and the optionality phrases — and then the model uses those inputs during extraction. One pass, one API call, but with the reasoning inputs written down before the reasoning outputs are generated.

The analogy: the old approach asked the model to simultaneously read a map, plan a route, and drive. The new approach asks it to mark the key landmarks on the map first, then drive using its own markings.

The general principle is well-established: you do not improve a model by adding more parameters, you improve it by choosing the right structure. The scaffolding fields are structural constraints on the model's reasoning — like well-chosen priors that guide inference without needing a more complex likelihood. The intelligence is in the schema design, not in the rules.

#### Why other sections should not regress

The seniority section is identical — not a single word changed. Same for `job_family`, company fields, education, responsibilities, and years of experience. Every rule that was working is preserved verbatim. The restructuring only touched the skills section.

Additionally, the prompt is now ~300 lines shorter (salary, `remote_policy`, `employment_type` fields removed in schema simplification; ~150 lines of skills scaffolding replaced with ~60). Less total content competing for attention means more attention budget available for the unchanged sections. Removing irrelevant content improves performance on remaining content — the same principle as regularisation in model training.

#### The mental model shift

The v1–v27 approach treated the LLM as a rule interpreter: give it precise rules, expect precise execution. That works for a large model with deep reasoning capacity. For a small model doing structured output generation, the effective approach is different: make the rules simple enough that the model can hold them, then structure the output schema so the model's own generation helps it reason. The intelligence is no longer in the rules — it is in the schema design that enforces the right reasoning sequence.

`preferred_signals_found` is a structural constraint on the model's reasoning process: the schema design forces the model to externalise its classification anchors before the fields that depend on them. This is more reliable than relying on the model to hold and apply multiple interacting rules from memory during generation.

**Implementation details**:
- Two scaffolding fields declared before all skills fields in `Job` schema; instructor fills in declaration order:
  - `responsibility_skills_found` — model scans responsibility statements and lists all embedded skill tokens first
  - `preferred_signals_found` — model lists all optionality phrases second
- Both fields stripped from HuggingFace push (`_PIPELINE_INTERNAL_COLS` in `hub.py`) and excluded from judge evaluation (`_JUDGE_EXCLUDE` in `judge.py`) — scaffolding, not dataset features
- Both displayed in `human_eval.py` `show_extraction()` as dedicated debug sections — show exactly what the model externalised before classifying, directly useful for verifying both responsibility scanning and preferred zone detection
- Prompt simplified from ~250 lines (skills section) to ~60 lines; total prompt ~300 lines shorter than v27

**v29–v30 — iterative refinements**: Four extraction runs (v29, v29b, v29c, v30) applied micro-refinements to field descriptions, scope constraints, and CV test calibration after reviewing v28 extractions. Each addressed narrow observed noise without structural change.

**Field ordering — preferred before required (v31)**: Skills field order in the schema was tested in both directions. Empirical finding: `skills_preferred` must be declared before `skills_required` in the schema (instructor fills in declaration order). The blast radius is asymmetric — preferred-first can only pull a bounded set of skills out of required (those near optionality language), whereas required-first can pull any preferred skill from anywhere in the posting into required (unbounded). Required-first produces larger, less predictable required lists; preferred-first produces tighter required lists with a small bounded error risk on the preferred side. Final schema order: `responsibility_skills_found` → `preferred_signals_found` → `skills_preferred` → `skills_required` → `skills_soft`.

**Schema simplification**: `salary_min`, `salary_max`, `salary_currency`, `salary_period`, `remote_policy`, `employment_type` removed from `Job` and `EvaluationScore`. These fields are almost never disclosed in the postings used, producing near-universal nulls. Their extraction rules and judge dimensions were contributing prompt length and attention cost with negligible signal value.

### 9.14 Post-processing layer — rationale and design

#### Why it's needed

The extraction prompt and schema are optimised for the hard classification problem: separating required, preferred, and soft skills using chain-of-thought scaffolding. This works. However, a small model (gpt-5.4-mini) has a ceiling on semantic judgment tasks that no amount of prompt engineering can raise. Four categories of noise survive the prompt and are observed consistently across test postings:

1. **Activity nouns in `skills_required`** — tokens like "quantum approaches", "visualizing data", "data quality", "analytics platform" describe what the person will do, not what they must know. The CV test instruction exists in the prompt but the model applies it inconsistently.

2. **Responsibilities leaking into `skills_soft`** — tokens like "collaborate within a small team", "train Developers/Analysts", "independently research problems" are job duties phrased as soft skills. The model does not reliably distinguish a behavioural skill from a responsibility that involves interpersonal behaviour.

3. **Normalisation inconsistency** — "Tensor" instead of "TensorFlow", "MS Visual Studio" instead of "Visual Studio", "ML/DL" as a combined token. These multiply across thousands of postings into fragmented aggregations where the same skill appears under multiple names.

4. **Occasional classification errors despite correct detection** — the scaffolding field correctly captures optionality signals but the model occasionally ignores its own prior output when filling downstream fields.

These are model-level limitations, not prompt-level bugs. Additional prompt rules for these issues were tested and had no measurable effect on output. The correct fix is a deterministic post-processing pass, not more prompt engineering.

#### Design

A deterministic Python function applied to each extracted `Job` object after the LLM returns it — no additional LLM calls, pure rule-based cleanup:

```python
def postprocess(job: Job) -> Job:
    """Deterministic cleanup of known model-level noise patterns."""
    ...
    return job
```

Called in `pipeline.py` between extraction and serialisation. Four components:

- **Skills normalisation map** — dictionary mapping known variants to canonical forms (e.g. "Tensor" → "TensorFlow", "MS Excel" → "Excel", "Amazon Web Services" → "AWS"). Built iteratively from the actual dataset: run the full batch first, aggregate all skill tokens, identify variant clusters, build the map.
- **Slash/combined token splitting** — split tokens like "ML/DL" or "Scala/Java" into separate entries.
- **Activity token filter** — blocklist of generic nouns and activity phrases that consistently appear as false-positive skills. Built from the full dataset by identifying high-frequency tokens that would not pass manual review as CV skills.
- **Soft skill responsibility filter** — remove `skills_soft` entries that are clearly responsibilities (leading verb + task description pattern rather than a behavioural quality).
- **Post-normalisation deduplication** — remove any literal string that appears in both `skills_required` and `skills_preferred` after normalisation (normalisation can create new collisions that the LLM dedup rule didn't catch).

#### When to build it

After the full batch extraction completes. The filters must be data-driven — built from the actual distribution of noise tokens across thousands of postings, not from a handful of test cases. Run first, analyse the aggregated skill token distribution, then build targeted filters for the patterns that appear at scale.

---

## 10. Outstanding Issues / Next Steps

- [x] Judge misalignment fixed (v5)
- [x] Preferred skills regression fixed (v7)
- [x] skills_soft over-nulling fixed (v9)
- [x] job_family title-first priority (v9)
- [x] v9 validated on three independent seeds (v9/v9b/v9c, confirmed stable by v9d/v9e/v9f)
- [x] Glassdoor hint experiment completed and reverted (v10/v10b/v10c)
- [x] Judge bias analysis completed — precision/recall coupling, ceiling effects, overall/null_appropriateness coupling documented (§8)
- [x] eval_trend tracker added (`src/evals/eval_trend.py`) — reads all report.json files, writes trend.csv + three trajectory plots
- [x] runner.py updated to save both `extraction_prompt.txt` and `judge_prompt.txt` per run
- [x] **Judge recalibrated (v9g/h/i)** — anti-anchoring on `overall` + forced recall enumeration. Overall improved +0.03–0.07 across all seeds, pct_score_1 down, n_flags halved. Forced enumeration had no effect on precision/recall (ceiling confirmed). Canonical baseline: **v9g (seed=42)**.
- [x] `compare_versions()` removed from `report.py` — was dead code (never called, broken README example). All multi-version comparisons go through `eval_trend.py`.
- [x] **Ground truth annotation deferred** — human annotation was evaluated and rejected as a pre-batch gate. Key reasons: (1) many fields require interpretation, making annotations a second opinion rather than objective ground truth; (2) annotator shares domain blind spots with the extractor; (3) the 9-run eval history with stable ceiling scores provides sufficient confidence. Annotation framework preserved in `tests/ground_truth_annotation/` for future use if a domain expert or downstream task demands it.
- [x] **Human evaluation completed** — 10 jobs scored on v20 extractions. Extraction quality confirmed excellent. Judge bias identified and structurally fixed in v21 (skills_soft, seniority). `compare()` used for calibration check.
- [x] **Schema field completion (v24, 2026-04-01)** — added missing system prompt rules for `remote_policy`, `employment_type`, `salary_min`/`salary_max`; analyst catch-all for `job_family`; CRITICAL dual-field skills/responsibilities rule. Judge prompt updated to match. See §9.9.
- [x] **Manual evaluation of v24-gpt5.4-mini extractions** — systematic skills_preferred misclassification identified across ~4 of 8 reviewed jobs. Prompt fixes applied in v25. See §9.11.
- [x] **v25–v26 patch attempts** — v25 targeted modifier/deduplication fixes; v26 added decision-tree structure without skill definition gate. Both superseded by v27 architectural redesign. See §9.12.
- [x] **v28–v31 architectural redesign and refinement** — schema-enforced chain-of-thought via two scaffolding fields (`responsibility_skills_found`, `preferred_signals_found`); prompt simplified from ~250 to ~60 lines; salary/remote/employment fields removed; preferred-first field ordering confirmed. See §9.13.
- [x] **v31 locked as batch prompt** — preferred-first field ordering confirmed (blast radius asymmetry); v29–v30 micro-refinements applied; post-processing layer design documented. Human eval of v31 in progress.
- [ ] **Human eval of v31 extractions** — validate final locked prompt before batch. Run dir: `eval_results/20260402_061928_v31`.
- [ ] `industry_accuracy` (~2.66) is the weakest remaining dimension. **Architectural fix deferred**: a company enrichment agent (web search / company page lookup) will supply ground-truth sector context at the recommendation step, rather than inferring from recruiter-written job descriptions. No further prompt iteration planned.
- [ ] Run full pipeline on all ~3,892 DS records (lite mode, `python -m src.data_ingestion.pipeline`). **Prompt locked pending manual eval confirmation.**
- [ ] **Post-processing layer** — build `postprocess(job: Job) -> Job` in `pipeline.py` after full batch run. Four components: normalisation map, slash-token splitter, activity token blocklist, soft skill responsibility filter. Data-driven — build from full batch aggregated token distribution. See §9.14.
- [ ] This prompt is the ingestion pipeline for all future data — treat as stable unless a systematic extraction failure is identified through human audit.
- [ ] Push lite dataset to HuggingFace Hub (`Alejandrofupi/ai-jie-jobs-lite`) after batch run.

---

## 11. Prompt Engineering Retrospective

This section documents the full arc of the prompt development process — including the false starts, dead ends, and unexpected findings. The goal is to preserve the reasoning behind decisions that aren't obvious from the version history alone.

### 11.1 The process was messier than the version numbers suggest

The stage 2 trajectory table (§9.5) looks clean in hindsight. The actual process involved frequent back-and-forth: reverting decisions, re-running the same prompt to isolate variables, mistaking noise for signal, and discovering that the metric being optimised (judge score) was itself unreliable for certain dimensions.

Key moments that shaped the final prompt:

**The v9 wall**: After nine versions of careful prompt iteration, a human audit of the outputs revealed that the judge had masked three systematic extraction failures. The eval framework was measuring compliance with what the judge understood the rules to mean — not whether the extraction was actually correct. This was the first indication that judge scores and extraction quality are not the same thing.

**The schema trap**: `nice_to_have` was defined as a subset of `skills_technical`. The intent was that required and preferred skills would be listed in `skills_technical`, with the preferred ones also flagged in `nice_to_have`. In practice the LLM treated them as mutually exclusive — a skill went into one or the other, never both. This is a known failure mode of multi-field schemas with overlapping semantics: the model resolves the ambiguity by picking one, consistently but incorrectly. The fix was a clean semantic split: `skills_required` (intent: required) and `skills_preferred` (intent: optional), no overlap by design.

**The v17–v19 trough**: Adding the HARD BOUNDARY instruction (v18) caused a skills_soft regression because the judge then started penalising format instead of content. The instruction made the extractor more careful about what went into skills_required, but inadvertently made it dump verbatim sentences into skills_soft instead of condensed phrases. Three separate rule changes were needed to fully untangle this: the HARD BOUNDARY itself, the condensing instruction, and the judge score-1 threshold restructure. They only worked together.

**The plateau discovery**: v20b, v21, and v22 all scored 2.80 overall despite being structurally different prompts. This was unexpected — the assumption going in was that each prompt change would move the needle. Instead, the plateau revealed that the judge had drifted after the schema change and was applying a stricter standard to `skills_required` than it had under v16. The ~0.30 drop in `skills_required` from v16 (2.78) to v21 (2.48) is almost certainly a judge calibration artefact, not an extraction quality regression. This distinction matters: continuing to optimise against a miscalibrated metric would have introduced real regressions in pursuit of a phantom improvement.

**The v20b detour**: After the plateau was confirmed, a single edge case (the Kafka/Hadoop posting performing differently under v20 vs v21) led to a brief decision to revert to v20. This was reversed within the same session. At temperature=0, individual posting variance is irrelevant — the prompt should be evaluated on the distribution, not on outliers. The lesson: at n=50, Δ ≥ 0.06 on overall is meaningful; a single posting is not.

**Human eval as the true calibration signal**: The single most informative data point in the entire process was 10 manually scored jobs. It took ~45 minutes, revealed a −1.1 judge gap on skills_soft and a −0.4 gap on seniority, and confirmed that extraction quality was "genuinely impressive" — a conclusion that 9 automated eval runs had obscured behind systematic under-scoring. The judge scores for skills_soft should be treated as a lower bound, not a ground truth.

### 11.2 What the LLM-as-a-Judge framework is and isn't good for

**Good for:**
- Catching obvious structural errors (wrong field type, null where content exists, content where null is correct)
- Comparing prompt versions on the same fixed sample — directional signal is reliable even when absolute scores are not
- Detecting regressions quickly: a 5+ flag increase or 0.1+ overall drop is a real signal
- Evaluating unambiguous fields (company_name, years_experience, salary) where there is a clear right/wrong answer

**Not good for:**
- Calibrated absolute scores on interpretive fields (skills_soft, seniority when scope-based inference is required)
- Detecting when the judge itself has drifted relative to an earlier version
- Replacing human judgment on whether the output is useful

**The fundamental limitation**: the judge evaluates compliance with the extraction rules as it understands them. When the rules are ambiguous (as they inevitably are at the edges), the judge fills in with its own interpretation, which may differ from the intended interpretation. Human evaluation catches this; automated evaluation cannot.

### 11.3 What actually moves extraction quality

In order of observed impact:

1. **Schema design** — the biggest lever. `nice_to_have` as a subset of `skills_technical` was a category error that no amount of prompt refinement could fix. The v16 schema redesign did more for extraction quality in a single change than all v1–v15 prompt iterations combined.

2. **Field boundaries** — the HARD BOUNDARY instruction on `skills_required` eliminated an entire class of error (soft skills leaking into technical skill lists). Boundaries work best when they are stated as constraints with examples, not as implications.

3. **Default assumptions made explicit** — the model fills in unstated defaults, and those defaults are often wrong. Making the intended default explicit (e.g., "skills listed without optional framing default to skills_required") removes an entire category of arbitrary variance.

4. **Judge calibration** — structural judge fixes (score-1 thresholds, format vs content separation) had more impact than extractor prompt changes across v17–v21. A miscalibrated judge makes every metric unreliable.

5. **Scope signals for seniority** — adding explicit scope anchors for the no-years, no-title path (IC → mid, owns domain → senior, cross-team authority → lead) closes the most common seniority failure mode.

6. **Example quality** — examples should illustrate the principle, not substitute for it. Where examples dominated the rule (as in early skills_soft), the extractor would generalise to the examples rather than the intent. Principle-first, examples-to-illustrate.

### 11.4 The attention budget constraint

The most important insight from the v24–v28 trajectory is that prompt engineering for small LLMs doing structured output generation is not a rule-writing problem — it is an attention allocation problem.

Rules in a prompt are not executed sequentially like code. They compete for attention at generation time, with recency bias (later content attends more strongly) and salience bias (headers, CRITICAL labels, dense instruction blocks). When the most important rule is buried deep in a long section, it will systematically lose to less important rules that happen to be closer to the generation point.

The practical implications:

1. **Prompt length is a direct cost, not a neutral expansion** — every token added to the prompt dilutes attention on every other token. The correct question is not "is this rule correct?" but "does adding this rule buy more than it costs in attention dilution?"

2. **The most important rule should be the first thing the model reads in its section, not the last** — recency bias means the rule the model encounters last (closest to generation) has the strongest effect. Place the most critical constraint at the start of the section, not as a trailing CRITICAL block.

3. **Adding a rule to fix a rule violation often makes it worse** — if the root cause is the existing rule being buried, adding another rule buries it further. The correct fix is structural: shorten everything else so the critical rule is closer to generation.

4. **Schema structure is a stronger constraint than prompt rules** — forcing the model to externalise intermediate reasoning into schema fields (like `preferred_signals_found`) is more reliable than asking it to retain that reasoning in implicit working memory while generating subsequent fields. Schema design is the highest-leverage prompt engineering tool available when using instructor.

5. **Removing irrelevant content improves performance on retained content** — stripping the salary, remote, and employment sections improved the entire prompt, not just those fields. Less noise improves signal on everything that remains. This is the same principle as L1 regularisation: sparsity is a feature, not just efficiency.

### 11.5 What was deliberately not done

- **Few-shot examples in the extractor prompt**: Would improve scores on the specific examples but risk over-fitting the model to those patterns. Structural rules generalise better.
- **Ground truth annotation as a pre-batch gate**: Evaluated and rejected. Many fields require interpretation; a human annotator shares the same domain blind spots as the model. The human eval of 10 extractions was more useful as a calibration check than formal annotation would have been.
- **Continued prompt iteration after the plateau**: Once the plateau was confirmed at v20b/v21/v22, further optimisation against judge scores would have been overfitting. The remaining judge gaps (skills_required ~2.46 vs v16 baseline ~2.78) are judge drift, not extraction failures.
