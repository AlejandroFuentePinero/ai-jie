# AI-JIE: Technical Report

**Project**: Automated Job Information Extraction (AI-JIE)
**Started**: 2026-03-29
**Status**: Active development

---

## 1. Project Overview

AI-JIE is a pipeline that extracts structured information from raw job postings at scale. The extracted data is stored on HuggingFace Hub and evaluated using an LLM-as-a-Judge framework to measure and improve extraction quality over time.

**Data source**: Two Kaggle CSV datasets (`DataScientist.csv`, `DataAnalyst.csv`) totalling ~3,000–4,000 raw job postings.

**Goal**: Produce a clean, structured dataset of job postings (company, role, skills, compensation) that can feed downstream analysis and ML applications.

---

## 2. Architecture

```
raw CSVs → pipeline.py (async extraction) → jobs.jsonl (checkpoint)
         ↓
    HuggingFace Hub (Parquet, versioned)
         ↓
    evals/runner.py → extractions + scores → eval_results/
```

### Modules

| Module | Responsibility |
|--------|----------------|
| `src/data_ingestion/models.py` | Pydantic schemas: `Job`, `EvaluationScore`, enums |
| `src/data_ingestion/parser.py` | LLM extraction — `gpt-4o-mini`, `instructor`, async |
| `src/data_ingestion/pipeline.py` | Batch runner — semaphore concurrency, checkpoint/resume |
| `src/data_ingestion/hub.py` | HuggingFace Hub push/pull |
| `src/evals/judge.py` | LLM-as-a-Judge — `gpt-4o`, `instructor`, 17-dimension scoring |
| `src/evals/runner.py` | Eval orchestrator — sample, extract, judge, save |
| `src/evals/report.py` | Score aggregation, group summaries, version comparison |

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

### 3.5 `_row_id` as pipeline artifact (not schema)

**Decision**: `_row_id` is stripped before pushing to HuggingFace Hub (`push_to_hub` drops it).

**Justification**: `_row_id` is a checkpoint/tracing artifact, not a feature of the job data. Keeping it in the public dataset would be confusing and wasteful.

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
| v9d | 44 | 42 | 2.91 | 23% | 2.84 | v9 re-validation after judge.py bug fix |
| v9e | 47 | 123 | 2.89 | 23% | 2.89 | v9 re-validation |
| v9f | 47 | 999 | 2.85 | 23% | 2.96 | v9 re-validation — **v9 selected for batch run** |

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

## 8. Ground-Truth Testing

### LLM-as-a-Judge recall limitation

The judge evaluates `skills_technical_recall` by reading the description and checking whether the extractor missed any skills. This is structurally unreliable: the judge must independently enumerate all skills first, which is the same task as the extractor. Since both models share training distribution, they have the same blind spots — systematic omissions go unpenalised.

`skills_technical_recall` scores (~2.9+) are likely inflated. Useful for detecting regressions, but not as an absolute measure of completeness.

### Industry ground-truth test (`tests/test_industry_extraction.py`)

The raw CSVs contain Glassdoor-sourced `Industry` (specific) and `Sector` (broader) columns — the only structured ground-truth labels in the dataset. These are used to evaluate the extractor's `industry` field directly.

Since the extractor produces free-form text ("Insurance") while the ground truth has its own taxonomy ("Insurance Carriers"), a lightweight LLM comparison call is used rather than string matching.

Scoring: 2 = matches `Industry`, 1 = matches `Sector` only, 0 = wrong, -1 = null.

This is the first evaluation in the project with an objective reference — the result cannot be inflated by shared model blind spots.

---

## 9. Outstanding Issues / Next Steps

- [x] Judge misalignment fixed (v5)
- [x] Preferred skills regression fixed (v7)
- [x] skills_soft over-nulling fixed (v9)
- [x] job_family title-first priority (v9)
- [x] v9 validated on three independent seeds (v9/v9b/v9c, confirmed stable by v9d/v9e/v9f)
- [x] Glassdoor hint experiment completed and reverted (v10/v10b/v10c)
- [x] eval_trend tracker added (`src/evals/eval_trend.py`) — reads all report.json files, writes trend.csv + three trajectory plots
- [x] runner.py updated to save both `extraction_prompt.txt` and `judge_prompt.txt` per run
- [ ] **Create human-annotated ground-truth eval set** (20–30 postings, all fields manually labelled) before running the full batch. The LLM judge cannot reliably measure recall — it shares blind spots with the extractor. This is the most important quality gate before batch mode.
- [ ] `industry_accuracy` (2.66–2.76) is the weakest remaining dimension. The ground-truth test (`tests/test_industry_extraction.py`) confirmed extractor reaches 36% exact-match without hints. Judge scores are unreliable for this dimension due to Glassdoor taxonomy noise. Acceptable for batch run; revisit with a cleaner ground-truth source.
- [ ] Run full pipeline on all ~3,900 records. **v9 is the selected prompt.**
- [ ] Push full dataset to HuggingFace Hub (`Alejandrofupi/ai-jie-jobs`) after batch run.
