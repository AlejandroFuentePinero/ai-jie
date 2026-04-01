# Job Intelligence Engine V2 — Initial Architecture Brainstorm

> This document captures the founding ideas, pillars, and design decisions for V2.
> It is not a contract. Pathways will change as we build and learn. Use it to stay
> grounded on *what we are trying to achieve* and *why*, not as a blueprint to follow literally.

---

## Why V2 — and What That Means

V2 is not a rewrite for its own sake. It is the same problem — job recommendation and upskilling
for data professionals — approached from a fundamentally different angle, because V1 hit a ceiling
that cannot be resolved by better ML.

V1 was built on personal expertise encoded into deterministic rules: 27 skill families defined by
hand, seniority extracted by a prioritized regex hierarchy, suitability computed as cosine distance
in PCA skill space. Every decision fork in that system required a human to anticipate it and hard-code
the right answer. The system is essentially a formalisation of the builder's own market understanding
— which means it is only as good as that understanding, and it mimics semantic reasoning rather than
performing it. Competitiveness was modelled as a probabilistic barrier-to-entry score derived from
skill classifier outputs. It is a clever approximation of what a market-aware human would assess.

V2 replaces that approximation with the real thing. Large language models do not mimic contextual
understanding of suitability and competitiveness — they perform it directly. An LLM reading a job
posting and a candidate profile does not need a pre-defined skill taxonomy to know that "Kafka
experience preferred for real-time pipeline work" is a stronger signal in an MLE role than in a
data analyst role. It does not need a regex to infer seniority from language. It does not need
cosine distance to judge whether a candidate's background is genuinely competitive or superficially
matching. That reasoning is native to the model.

This is expected to be a dramatic improvement — not an incremental one. The gap between mimicking
contextual judgement and actually performing it is large, and it is precisely the gap that makes
current recommendation systems (including V1) feel off to people who know the field.

The goal is to put this to production if the improvement holds. That is the bar this is being built
to meet.

---

## The Problem Worth Solving

Current job recommendation systems (LinkedIn, Seek, Indeed) match candidates to jobs based on
literal skill density — what percentage of listed skills does the candidate have. This makes
them blind to two things that actually determine whether a candidate is competitive:

**Gatekeeper skills** — the skills that determine entry into a role niche. Not baseline skills
(Python, SQL) that everyone has and carry no discriminatory signal, but the specific skills
whose presence in a posting signals a particular tier of role and a particular set of expectations.

**Market structure** — the ecology of the job market. Which skills are codependent, which are
foundational vs specialised, which are emerging vs declining, how role families are structured.
Without this context, no system can provide meaningful upskilling recommendations — which is why
none of them do.

The core bet: an ecological model of the job market is the layer that is entirely absent from
every current system, and it is what makes both recommendation and upskilling genuinely
intelligent rather than pattern-matching on keyword overlap.

---

## The Four Pillars

### 1. Structured Market Data (the foundation)

Everything downstream depends on a clean, structured, semantically rich representation of job
postings. This is already built in V1: the extraction pipeline uses `gpt-5.4-mini` + `instructor`
to produce validated Pydantic `Job` objects from raw postings, with skills segregated by intent
(`skills_required`, `skills_preferred`, `skills_soft`), seniority inferred from language signals,
and each posting tagged with a `job_family`.

The `job_family` field is the taxonomy that ties the entire V2 system together. It is the key
that links postings, knowledge bases, user profiles, and statistical layers.

**Why this matters:** Downstream reasoning is only as good as the data it reasons over.
Structured token-level skill lists with intent classification (required vs preferred) are
meaningfully different from raw text — they are a pre-processed feature set that makes both
statistical analysis and LLM reasoning more reliable.

### 2. Market Ecology Knowledge Base (the macro lens)

An expert synthesis document per `job_family`, built by a research agent using web search
and subagents. Each document captures: the canonical skill clusters for the family, what
distinguishes junior from senior roles, what the genuine gatekeeper skills are (vs baseline
assumptions), and how this family relates to adjacent ones.

These documents are stable, human-inspectable, and editable. They represent expert market
knowledge — not derived from our corpus, but from broader understanding of how these roles
actually work. They are retrieved by `job_family` ID (a lookup, not similarity search) and
injected into the LLM context window when reasoning about a candidate-job pair.

**Key tradeoff:** These documents encode general market knowledge, not corpus-specific signals.
They can be wrong or out of date. They should be treated as informed priors, not ground truth.
The statistical layer (Pillar 3) provides the corpus-grounded check.

### 3. Statistical Corpus Layer (the evidence base)

A batch-computed analysis of the job corpus per `job_family`: skill frequency, co-occurrence
matrix, conditional probabilities (P(skill B | skill A)), seniority-stratified frequencies,
and gatekeeper scoring. Gatekeeper identification is a graph centrality problem — a skill is
a gatekeeper candidate when its presence in a posting reduces uncertainty about many other
skills simultaneously (hub centrality in the co-occurrence graph).

This layer feeds the upskilling engine, not the recommender. The questions it answers are
about market trajectory: which skills are increasing in co-occurrence with senior titles,
which are pre-gatekeeper (growing but not yet dominant), which unlock the most adjacent role
families. These questions require computation over a corpus; they cannot be answered by a
model reasoning from training data alone.

**Key constraint:** Reliable gatekeeper detection requires meaningful volume per family
(~150–200 postings minimum). The stats pipeline should be re-runnable as the dataset grows —
same checkpoint-safe, versioned batch philosophy as the V1 extraction pipeline.

**Implementation note:** `skills_required` should be weighted significantly higher than
`skills_preferred` in co-occurrence analysis. A skill appearing in 80% of required lists
is a gatekeeper candidate; the same frequency in preferred lists may just be aspirational
hiring language.

### 4. Traceable, Grounded Reasoning (the design constraint)

Every recommendation should have an auditable reasoning chain. This is both a product
differentiator and a quality constraint: if the system cannot explain *why* a job was
surfaced or *why* a skill was recommended, the recommendation is not trustworthy.

This shapes the architecture throughout: structured inputs at every stage, explicit knowledge
sources (not implicit embeddings alone), statistical computations that are reproducible and
inspectable, LLM reasoning that produces arguments not just scores.

---

## How It Ties Together

```
Stage 1 (existing)
  Raw postings → [gpt-5.4-mini + instructor] → structured Job objects (JSONL → HF Hub)
                                                         |
                    ┌────────────────────────────────────┴───────────────────────────────┐
                    │                                                                     │
         Expert Synthesis Docs                                                 Statistical Pipeline
    [Research agents per job_family]                              [Batch computation on corpus]
    Canonical skill clusters, gatekeepers,                        Frequency, co-occurrence, gatekeeper
    seniority signals, family relationships                       scores, seniority stratification,
    — general market knowledge                                    temporal drift signals
                    │                                                                     │
                    └────────────────────┬────────────────────────────────────────────────┘
                                         │
                              User Profile (structured)
                    Skills, experience, seniority inference,
                    current + aspirational job_family positioning
                                         │
                          ┌──────────────┴──────────────┐
                          │                             │
               Recommender Agent                 Upskilling Agent
          user + top-N jobs (dense              user + stats KB +
          retrieval) + expert doc               expert doc →
          → suitability reasoning,              keystone skill plan,
          gatekeeper gap analysis,              market trajectory,
          competitive vs surface fit            argued justification
```

---

## Key Design Decisions

**Why two separate knowledge bases instead of one?**
Expert docs and statistical corpus serve different purposes. Expert docs encode general market
knowledge and are stable. Stats encode what your specific corpus shows and are dynamic.
Conflating them would mean the knowledge base is either always stale (if you update only once)
or noisy (if you mix general knowledge with corpus-specific signals). Keeping them separate
also allows each to be validated independently.

**Why LLM reasoning for suitability rather than pure vector matching?**
Embedding similarity can surface jobs where a candidate has 70% of the listed skills but is
missing the one gatekeeper skill that makes the role inaccessible. An LLM reasoning over the
job + user profile + expert doc for the family can make that distinction. The expert doc gives
it the canonical knowledge to judge gatekeepers vs baseline assumptions. Vector retrieval is
used for *finding candidates*, not for *ranking or explaining* them.

**Why is the statistical layer reserved for upskilling?**
For suitability reasoning, the LLM's context understanding is sufficient — it can infer from
posting language whether SQL is load-bearing for a data analyst role. But for upskilling, the
model's training data is global and historical, not grounded in your current corpus. "Learn
dbt because it appears in 68% of senior analyst postings in this corpus and grew 40%
year-over-year" is a fundamentally different recommendation than a model guessing from
training data. The stats layer makes upskilling defensible.

---

## What Will Likely Change

- The specific retrieval architecture (pure dense search, hybrid, reranking) — not locked.
- How the expert synthesis docs are built and updated — the research agent approach is a
  starting point; it may evolve into a human-curated + agent-maintained hybrid.
- The user profile structure — not yet designed in detail; will be shaped by what users
  actually provide (resume, LinkedIn, conversation).
- The exact gatekeeper scoring algorithm — the hub centrality framing is an initial
  hypothesis; the right formulation will be validated against real data.
- Whether the stats KB is exposed directly to the upskilling agent or first synthesised
  by an intermediate layer into a structured document.

---

## Transferable Assets from the ML Version

The ML version of this project (V1) was built on the same dataset using deterministic,
statistics-based methods. It hit a hard ceiling on semantic understanding — the root problem
V2 is designed to solve. But it contains well-validated ideas, algorithms, and code worth
borrowing rather than rebuilding from scratch.

Reference repo: https://github.com/AlejandroFuentePinero/job-intelligence-engine

---

### Concepts to carry forward directly

**Dual positioning metric (suitability vs competitiveness as orthogonal axes)**
V1 computed these via cosine similarity and a probabilistic barrier-to-entry score. V2 will
compute them via LLM reasoning, but the two-question framing is the right output structure:
"does this person fit right now?" and "how hard is entry into this tier?". The naming and
bucketing logic should be preserved.
→ `src/job_intel/positioning.py`

**best_now / stretch bucketing**
Jobs are split into two recommendation tiers: high fit + low barriers ("best_now") and
high fit + higher barriers ("stretch"). Clean UX decision, already validated. Carry forward
as-is into the recommender agent's output format.
→ `src/job_intel/job_recommender.py`

**Frozen-universe counterfactual for upskilling**
Inject one missing skill at a time into the user profile, recompute positioning against an
unchanged job universe, measure the delta. This pattern ensures scenarios are comparable
and the upskilling ROI is defensible. V2's statistical layer provides richer signal than
V1's LightGBM probability matrix, but the simulation logic is the same.
→ `src/job_intel/job_recommender.py` (counterfactual simulation section)

**Seniority extraction logic**
V1 uses a prioritized regex hierarchy (principal → staff → manager → lead → senior → mid →
junior → assistant) with description-first precedence over title. This is a useful reference
for edge cases and ordering decisions, even though V2 infers seniority semantically.
→ `src/job_intel/features/`

**Hard-constraint candidate filtering before scoring**
V1 filters the job universe by salary range, domain, seniority, and location before any
scoring runs. This keeps scoring focused and prevents noise from irrelevant postings.
The same pre-filter pattern should apply in V2's retrieval stage before the LLM ranks candidates.
→ `src/job_intel/positioning.py` (`run_positioning()`)

---

### Statistical methods worth revisiting for the V2 corpus layer

**Node2Vec bipartite graph embeddings**
V1 builds a weighted job × skill bipartite graph (edge weights = predicted skill requirement
probabilities) and derives 64-dimensional Node2Vec embeddings. These embeddings capture
skill similarity through probabilistic co-occurrence neighborhoods — a more sophisticated
foundation for skill clustering than naive co-occurrence counts. Worth revisiting when
building the V2 statistical layer, especially for gatekeeper identification.
→ Chapter 2 pipeline, `src/job_intel/pipelines/`

**Skill co-occurrence network via embedding k-NN**
V1 computes pairwise cosine similarities between skill embeddings, extracts top-5 nearest
neighbors per skill, and deduplicates to a symmetric edge list. This produces interpretable
skill bundles (e.g., analytics ↔ ML ↔ programming ecosystems). The same approach applied
to V2's richer LLM-extracted skill tokens would yield more semantically accurate clusters.
→ Chapter 2 pipeline

**KMeans on embeddings with silhouette-based k selection**
V1 clusters jobs into 20 families using KMeans on L2-normalized embeddings, with k selected
by silhouette score optimisation. This is a principled, reproducible clustering approach
that could validate or enrich the `job_family` taxonomy in V2.
→ Chapter 2 pipeline

**LightGBM skill probability matrix**
V1 trains 27 independent binary classifiers to produce a dense job × skill probability
matrix. This is less relevant for V2 (LLM extraction replaces dictionary-based skill
detection), but the calibrated probability framing — treating skill requirements as
continuous rather than binary — is a useful conceptual anchor for the stats layer.
→ `src/job_intel/models/`

---

### What V2 is explicitly not borrowing

**Dictionary-based skill extraction (27 canonical families)**
V1 maps ~1,300 raw tokens to 27 skill families via regex and word-boundary matching. This
is the primary limitation V2 is designed to overcome. The LLM extraction layer produces
semantically richer, intent-classified skill tokens that don't require a manually maintained
dictionary. Do not regress to this approach.
→ `src/job_intel/features/` (skill extraction)

**Regex-based seniority and title normalisation**
Works at scale but is brittle at edges. V2 infers these from language signals semantically.
The V1 patterns are useful as a reference for edge cases, not as implementation.

**Cosine similarity for suitability scoring**
V1 computes suitability as cosine similarity in PCA-transformed skill space. This is exactly
the skill-density matching problem V2 is solving — it cannot distinguish a missing gatekeeper
from a missing nice-to-have. LLM reasoning with ecology context is the replacement.

---

## What Should Not Change

- The `job_family` taxonomy as the unifying key across all layers.
- The separation between suitability reasoning (recommender) and market trajectory reasoning
  (upskilling) — these require different inputs and should not be collapsed into one agent.
- The commitment to traceability — every recommendation should cite its sources and reasoning.
- The structured extraction layer as the foundation — garbage in, garbage out applies at
  every downstream stage.
