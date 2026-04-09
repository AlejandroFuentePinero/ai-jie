# Extraction Evaluation — 10 Test Postings

## Non-Skills Fields: Excellent

| Field | Score | Detail |
|-------|-------|--------|
| company_name | 10/10 | Perfect. Correctly null for [1][2][3] where company unnamed. Canonical names used (IBM not "International Business Machines", Axon not "Axon Enterprise"). |
| seniority | 10/10 | All correct including edge cases: "Associate Scientist" → junior [1], "Director" → director [2][3], AVP in finance → senior [6], "Principal" → principal [0]. |
| job_family | 10/10 | All defensible. [3] correctly classified as management despite "Data Science" in title — the role is about leading teams and market strategy, not doing data science. |
| years_experience | 10/10 | Correctly extracted where stated, null where not. Open-ended ranges handled correctly (min set, max null). |
| education | 10/10 | Only required education extracted, preferred education correctly excluded. |
| responsibilities | 9/10 | [3] extracted 12 responsibilities, exceeding the 7-item limit. All others are concrete, verb-led, directly from posting text. |


## Preferred Signal Detection: Strong

9/10 postings have correct detection.

| Posting | Signals in posting | Captured | Missed |
|---------|-------------------|----------|--------|
| [0] IBM | Section: "Preferred Technical and Professional Expertise" | ✅ Full section captured | — |
| [1] PCR | "is desirable" | ✅ | — |
| [2] Director DS | "is a plus" | ✅ | — |
| [3] Director Strategic | None | ✅ Correctly null | — |
| [4] PulsePoint | 3x "is a (huge) plus" | ✅ All three | — |
| [5] Axon | Section: "Preferred Qualifications" | ✅ Both items | — |
| [6] Oaktree | 3x "is a plus" / "preferred" + "Preference will be given" | 3 of 4 | "Preference will be given to CFA/FRM candidates" |
| [7] NPD | 4x "preferred" / "is preferred" | ✅ All four | — |
| [8] Vertex | Section: "Preferred Qualifications" | ✅ | — |
| [9] Aerospace | 2x "strongly preferred" | ✅ Both | — |

The one miss: Oaktree's "Preference will be given to CFA/FRM candidates"
uses an uncommon optionality pattern. CFA and FRM are missing from the
extraction entirely.


## Preferred Classification: The Core Test

This was the problem we redesigned the architecture to solve. Results are
substantially improved but inconsistent on three postings.

**Working correctly (7/10):**
- [1] clinical validation → preferred ✅
- [2] people/consumer information → preferred ✅
- [3] null → correct, no signals ✅
- [5] All 8 preferred skills correctly classified ✅ (best extraction)
- [7] Agile, Lean, Scrum, JIRA, Confluence, Github/Gitlab, Trello, TFS → preferred ✅
- [8] Ph.D. → preferred ✅
- [9] advanced degree, TS/SCI → preferred ✅

**Classification errors despite correct detection (3/10):**

[0] IBM: The scaffolding captured the entire "Preferred Technical and
Professional Expertise" section. But Python, Jupyter, Tensor, NumPy
landed in skills_required. Only linear programming, mathematical
programming, ML/DL, quantum concepts, HPC made it to preferred. The
model detected the zone but didn't apply it to all skills within it.

[4] PulsePoint: Python went to skills_preferred when it should be
required. The sentence "Fluency in Python, Experience in Scala/Java is a
huge plus" has the optionality signal only on "Experience in Scala/Java",
but the model applied it to the entire sentence including Python. Scala,
Java, Cloud migration are correctly preferred.

[6] Oaktree: Python, R, C#, MS Visual Studio are in skills_required
despite "Experience using Python, R, C#, and MS Visual Studio preferred"
being captured in the scaffolding. investment platforms, alternative
asset management, investment lifecycle are also in required despite the
"is a plus" signal being captured. Big Data, ML, AI, Deep Learning,
investment financial models are correctly preferred. CFA/FRM missing
entirely (detection failure).


## Skills_required Quality: Noisy

The CV test is not reliably enforced. Every posting has some correct
technical skills alongside noise tokens.

**Systematic noise patterns across the batch:**

Activities extracted as skills:
- [0]: "quantum approaches", "data pre-/post-processing", "numerics",
  "visualizing data"
- [2]: "data analysis", "consumer preference information", "data sources",
  "analytic approaches", "predictive models"
- [7]: "simulations", "historical data", "survey", "scanner",
  "point-of-sale data", "unit tests", "code reviews", "pair programming"
- [9]: "fabrication", "testing"

Team roles and organisational terms extracted as skills:
- [3]: "data scientists", "data analysts", "database manager",
  "market researchers", "Demand Generation"

Marketing activities extracted as skills:
- [3]: "webinars", "social media advertising", "email blasts"

Professional associations extracted as skills:
- [3]: AIA, NECA, PMA, ACEC, MCAA, SMACNA, CICPAC, CFMA

Posting [3] is the worst extraction — almost everything in skills_required
is wrong. The role is a strategic management position and the model could
not distinguish team composition and partner organisations from skills.

**Notable missing skills:**
- [1]: BSL-2, nucleic acids, primer/DNA sequence analysis, FDA 510k,
  Word, PowerPoint, Excel — all explicitly required
- [4]: Linux (explicitly stated as required), Airflow, Docker, Impala,
  SQL Server, Sqoop
- [5]: Java, Scala, C++ missing from preferred (listed under "Backend
  engineering experience" in Preferred Qualifications)
- [8]: organic reaction mechanism, synthetic methods, medicinal chemistry


## Skills_soft Quality: Weakest Field

Responsibilities consistently leak in, and boilerplate passes through.

**Responsibilities misclassified as soft skills:**
- [2]: ALL four entries are responsibilities — "hiring and building a
  high caliber data science team", "customer and partner discussions",
  "operate at a strategic level", "remain hands on"
- [4]: "collaborate within a small team", "training developers/analysts"
- [5]: "mentoring junior team members", "advising senior leaders"
- [8]: "work independently", "multi-task", "work collaboratively in
  teams", "adaptable to changing needs"

**Boilerplate that should be filtered:**
- [1]: "attention to detail", "goal-driven", "milestone-driven"
- [6]: "initiative", "work ethic", "integrity", "professionalism"
- [0]: "coaching", "development of training course material"


## Summary

| Dimension | Rating | Comment |
|-----------|--------|---------|
| Company / Role / Education / Years | Excellent | Production-ready. No changes needed. |
| Preferred signal detection | Strong | 9/10 correct. Misses uncommon patterns. |
| Preferred classification | Good | 7/10 correct. Major improvement from baseline (was ~2/10). Three postings show detection without application. |
| skills_required content | Acceptable with noise | Real skills are present but mixed with activities, vague nouns, team roles. Post-processing needed. |
| skills_preferred content | Good | When classified correctly, the tokens are appropriate. |
| skills_soft content | Weak | Responsibilities leak in systematically. Boilerplate filter ineffective. Post-processing essential. |

**Recommendation:** The architecture and prompt are at their practical
ceiling for this model. Non-skills fields are production-ready. Preferred
classification is the best achievable without a larger model — 70%
accuracy with correct detection is a known model-level limitation. Run
the full batch, then build the post-processing layer to clean
skills_required noise, skills_soft responsibility leakage, and
normalisation inconsistencies.