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

| Version | n | Overall | pct_score_1 | Key change |
|---------|---|---------|-------------|------------|
| v1 | 50 | ~2.96 | — | Baseline — circular eval (invalid) |
| v2 | 30 | — | — | After fixing circular eval |
| v3 | 50 | 2.54 | 36% | Clean baseline; extractor v3 rules |
| v4 | 50 | 2.40 | 42% | Relaxed skills rules — judge misalignment exposed |
| v5 | 50 | TBD | — | Judge v5: extraction rules in prompt + temperature=0 |

### v3 notable flags (clean baseline)
- `industry_incorrect` — judge applying its own classification vs. stated rule
- `seniority_incorrect` — disagreement on priority ladder application
- `skills_technical_precision` — judge penalising broad categories we allow
- `nice_to_have_accuracy` — skills in requirements section mis-labelled as nice-to-have

### v4 regression analysis
`skills_technical_precision` dropped from 2.64 → 2.46. The extraction prompt v4 explicitly allowed broad categories and methodology terms. The judge was penalising exactly what the extractor was now explicitly told to include. This confirmed the judge needed its own update.

---

## 7. Evaluation Design

### Sample size: 50

30 samples gives ~85% power to detect a 0.2-point shift in overall score at α=0.05. 50 samples improves this to ~92% and is still affordable (50 × 2 LLM calls = 100 API calls per run). 25 was considered too low given the noisiness of 1–3 integer scores.

### Judge model: gpt-4o

The judge needs to assess nuanced extraction quality — industry classification, seniority ladder application, skills completeness. `gpt-4o-mini` lacks the reasoning depth needed for consistent judgement on edge cases.

### Seeded sampling

`seed=42` ensures the same 50 rows are drawn on every run, making version comparisons valid. A different seed would change which rows are sampled and could mask real improvements or introduce spurious differences.

---

## 8. Outstanding Issues / Next Steps

- [ ] Analyse v5 eval results vs v3/v4 (run in progress)
- [ ] Investigate recurring `seniority_incorrect` flags — the priority ladder rule may need clearer examples
- [ ] Investigate `industry_accuracy` flags — ambiguous cases (e.g. "FinTech" vs "Financial Services") may need tie-breaking examples in the prompt
- [ ] Consider running full pipeline on all ~3,000–4,000 records once v5 eval confirms improvement
- [ ] Push full dataset to HuggingFace Hub after final pipeline run
