# v32b vs v33 — head-to-head diff


*1/50 rows identical across all fields.*


Comparing all 50 rows across: responsibility_skills_found, preferred_signals_found, all_technical_skills, skills_required, skills_preferred


Rows flagged in v32 human eval (skills_required_accuracy ≤ 4): [0, 2, 3, 5, 6, 7, 9, 10, 12, 16, 17, 19, 20, 22, 23, 24, 25, 27]


- 🔴 only in v32b = dropped by v33 (noise candidates)


- 🟢 only in v33  = introduced by v33 (regression candidates)


---


## row_id 0 ⚑ — Quantum Principal Data Scientist- Industrial Process Sector Industry
*v32 human skills_required_accuracy: 4*

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `deep knowledge and application expertise in ml/dl.` · `experience with linear programming and/or general mathematical programming.` · `experience with some aspect of high-performance computing use within an industry context.` · `familiarity with qiskit and quantum concepts and principles, able to model classical ml/dl algorithms within quantum principles.` · `proficiency in python with good knowledge of jupyter, tensor, numpy.` |
| 🟢 only in v33  | `* experience with linear programming and/or general mathematical programming* proficiency in python with good knowledge of jupyter, tensor, numpy* deep knowledge and application expertise in ml/dl* familiarity with qiskit and quantum concepts and principles, able to model classical ml/dl algorithms within quantum principles* experience with some aspect of high-performance computing use within an industry context` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `data engineering` · `data science` |

---

## row_id 1 — Associate Scientist - PCR
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `qa` · `qc` |
| 🟢 only in v33  | `multiplexed assay methods` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `nucleic acids` · `primer analysis` · `qa` · `qc` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `nucleic acids` · `primer analysis` · `qa` · `qc` |

---

## row_id 2 ⚑ — Director of Data Science - Big Data + Machine Learning
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `hadoop` · `machine learning` · `python` · `relational databases` |
| 🟢 only in v33  | `analytic approaches` · `architecture` · `consumer preference information` · `data sources` · `methodologies` · `sw tools` · `technology stack` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `analytic approaches` · `consumer based information` · `predictive models` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `analytic approaches` · `predictive models` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `consumer based information` |
| 🟢 only in v33  | `methodologies of collecting and analyzing people/consumer based information` |

---

## row_id 3 ⚑ — Director, Strategic Research Data Science
*v32 human skills_required_accuracy: 1*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `acec` · `aia` · `cfma` · `cicpac` · `cpa` · `demand generation` · `mcaa` · `neca` · `pma` · `smacna` |
| 🟢 only in v33  | `social media advertising` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `cpa` · `demand generation` |
| 🟢 only in v33  | `social media advertising` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `cpa` |
| 🟢 only in v33  | `social media advertising` |

---

## row_id 4 — Data Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `airflow` · `beacon` · `ddl` · `docker` · `graphite` · `impala` · `rdbms` · `sqoop` |

### Skills required
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `python` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `python` |

---

## row_id 5 ⚑ — Senior Data Engineer
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `business intelligence` · `data pipelines` · `data warehouse` · `etl` · `reporting systems` · `streaming` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `ad-hoc access` · `business intelligence` · `data pipelines` · `data processing` · `data storage` · `data warehouse` · `resource optimization` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `spark` |
| 🟢 only in v33  | `ad-hoc access` · `business intelligence` · `data processing` · `data storage` · `data warehouse` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `spark` |

---

## row_id 6 ⚑ — AVP, Quantitative Analyst, Portfolio Analytics, Risk and Reporting
*v32 human skills_required_accuracy: 3*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `c#` · `ms visual studio` · `python` · `r` · `sql` |
| 🟢 only in v33  | `analytics` · `analytics calculators` · `data flows` · `debugging` · `financial engineering` · `portfolio construction` · `report outputs` · `security analytics` · `software development` · `testing` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `bonds` · `convertible securities` · `credit` · `credit products` · `derivatives` · `equity` · `interest rates` · `leveraged loans` · `operations` · `processes` · `structured products` · `systems` |
| 🟢 only in v33  | `cfa` · `debugging` · `frm` · `testing` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `bonds` · `c#` · `convertible securities` · `credit` · `credit products` · `equity` · `leveraged loans` · `ms visual studio` · `processes` · `python` · `r` |
| 🟢 only in v33  | `cfa` · `debugging` · `frm` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `c#` · `ms visual studio` · `python` · `r` |

---

## row_id 7 ⚑ — Data Scientist
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `agile` · `confluence` · `devops server` · `github` · `gitlab` · `jira` · `lean` · `team foundation server` · `trello` |
| 🟢 only in v33  | `acceptance test` · `agile management tools` · `simulations` · `unit test` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `graduate-level experience preferred.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `computer science` · `data analysis` · `data sources` · `frequency of collection` · `issue tracker` · `levels of measurement` · `mathematics` · `model-based approaches` · `mrp` · `multilevel regression and post stratification` · `production scale` · `quantitative social science` · `research science` · `sample frames` · `software development` · `statistical and analytic techniques` · `statistics` |
| 🟢 only in v33  | `agile management tools` · `code reviews` · `historical data` · `multilevel regression and post stratification (mrp)` · `pair programming` · `simulations` · `test-driven development` · `unit tests` · `version control` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `agile` · `confluence` · `data sources` · `devops server` · `frequency of collection` · `github` · `gitlab` · `issue tracker` · `jira` · `lean` · `levels of measurement` · `mathematics` · `model-based approaches` · `mrp` · `multilevel regression and post stratification` · `quantitative social science` · `research science` · `sample frames` · `software development` · `statistical and analytic techniques` · `statistics` · `team foundation server` · `trello` |
| 🟢 only in v33  | `agile management tools` · `code reviews` · `historical data` · `multilevel regression and post stratification (mrp)` · `pair programming` · `simulations` · `test-driven development` · `unit tests` · `version control` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `agile` · `confluence` · `devops server` · `github` · `gitlab` · `jira` · `lean` · `team foundation server` · `trello` |

---

## row_id 8 — Temporary Research Scientist, Medicinal Chemistry
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `organic synthesis` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `a desire to be part of a highly innovative company aimed at transforming the lives of people with serious diseases, their families and society` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `medicinal chemistry` · `ph.d.` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `medicinal chemistry` |

---

## row_id 9 ⚑ — Research Scientist/Senior Scientist
*v32 human skills_required_accuracy: 4*

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `seta contractors` |
| 🟢 only in v33  | `seta` |

### Skills required
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `seta` |

---

## row_id 10 ⚑ — Director Data Scientist - Data Science Hub
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `analytical methods` · `data and information exploration` · `data science` · `data sets` · `it` · `systems` |
| 🟢 only in v33  | `advanced analytics` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `analytical methods` · `applied mathematics` · `data and information exploration` · `data sets` · `large data analysis` · `predictive modeling` · `quantitative economics` · `statistics` · `systems` |
| 🟢 only in v33  | `data science solutions` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `analytical methods` · `applied mathematics` · `data and information exploration` · `data sets` · `large data analysis` · `predictive modeling` · `quantitative economics` · `statistics` |

---

## row_id 11 — Data Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `data warehouse` · `sql server` |
| 🟢 only in v33  | `data integrations` · `data pipelines` · `query performance tuning` · `stored procedures` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `banking domain` · `data warehouse` · `sql server` · `stored procedures` |
| 🟢 only in v33  | `architecture` · `data warehouse databases` · `self-service data platform` · `sql server 2014` · `sql server 2017` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `data warehouse` · `sql server` · `stored procedures` |
| 🟢 only in v33  | `architecture` · `data warehouse databases` · `self-service data platform` · `sql server 2014` · `sql server 2017` |

---

## row_id 12 ⚑ — Analytical Scientist I
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `dea` · `epa` · `fda` · `osha` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `b.s. in chemistry` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `b.s. in chemistry` |

---

## row_id 13 — Analytics Manager (Web / Social)
*No differences.*

---

## row_id 14 — VP, Data Scientist
### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `advantage for hands on experience with emerging statistical methods/techniques (e.g. machine learning and/or artificial intelligence).` |
| 🟢 only in v33  | `advantage for hands on experience with emerging statistical methods/techniques (e.g. machine learning and/or artificial intelligence)` |

---

## row_id 15 — Data Scientist - Alpha Insights
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `pandas` · `r` |
| 🟢 only in v33  | `exploratory techniques` · `ranking algorithms` · `recommendation algorithms` · `statistical analysis` · `visualizations` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `computer science` · `data analysis` · `economics` · `statistics` |
| 🟢 only in v33  | `exploratory techniques` · `imperative programming language` · `statistical analysis` · `visualizations` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `economics` · `statistics` |
| 🟢 only in v33  | `exploratory techniques` · `imperative programming language` · `statistical analysis` |

---

## row_id 16 ⚑ — Data Engineer
*v32 human skills_required_accuracy: 3*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `data governance` |
| 🟢 only in v33  | `dax` · `ms excel` · `power pivot` · `sql` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `azure cloud` · `computer engineering` · `computer science` · `data architect` · `data governance` · `database` · `enterprise data models` · `healthcare` · `information systems` · `ms excel` · `programming courses` · `queries` · `reports` |
| 🟢 only in v33  | `data dictionaries` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `azure cloud` · `data architect` · `data governance` · `database` · `enterprise data models` · `healthcare` · `information systems` · `ms excel` |
| 🟢 only in v33  | `data dictionaries` |

---

## row_id 17 ⚑ — Microsoft Analytics Consultant
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `business process` · `data` · `intelligence tools` · `microsoft` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `at least 2 years of experience in azure cosmosdb consumption via web applications` · `at least 3 years of experience in mdx(ssas)` · `at least 3 years of experience in sql server, ssis, ssrs, ssas` · `microsoft certification in azure based technology` |
| 🟢 only in v33  | `candidates from all locations considered; however candidates that live in or near one of the following cities preferred: atlanta, chicago, columbus, houston, dallas, raleigh, washington dc metro area, piscataway, philadelphia.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `business intelligence consulting` · `report data modelling` |
| 🟢 only in v33  | `data mining` · `data modeling` · `process modeling` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `business intelligence consulting` · `report data modelling` |
| 🟢 only in v33  | `azure cosmosdb` · `data mining` · `data modeling` · `erp` · `mdx` · `process modeling` · `sql server` · `ssas` · `ssis` · `ssrs` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `azure cosmosdb` · `mdx` · `sql server` · `ssas` · `ssis` · `ssrs` |

---

## row_id 18 — Big Data Engineer
### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `experience in hadoop cluster administration is a big plus` |
| 🟢 only in v33  | `experience in hadoop cluster administration is a big plus.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `data lake` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `data lake` |

---

## row_id 19 ⚑ — Pre-Clinical Imaging Field Application Scientist
*v32 human skills_required_accuracy: 3*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `multimodality imaging` · `optical imaging` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `phd with a focus on optical imaging or alternative doctoral degree (dvm, phd, md) within academia or the pharmaceutical/biotechnology industry, or equivalent.` · `proven track record of experience in non-invasive, live animal imaging (ivis and multimodality), laboratory animal models, cell culture and molecular biology.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `bioluminescence` · `cerenkov` · `fluorescence` · `microct` · `multimodal imaging` · `preclinical models` · `vivarium` |
| 🟢 only in v33  | `dvm` · `md` · `multimodality imaging` · `phd` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `cell culture` · `cerenkov` · `laboratory animal models` · `microct` · `molecular biology` · `multimodal imaging` · `non-invasive live animal imaging` · `preclinical models` · `vivarium` |
| 🟢 only in v33  | `multimodality imaging` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `cell culture` · `laboratory animal models` · `molecular biology` · `non-invasive live animal imaging` |

---

## row_id 20 ⚑ — Python Data Engineer Trading
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `hadoop` · `linux` · `spark` |

---

## row_id 21 — Data Engineer- Customer Data Platform
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `agile` |
| 🟢 only in v33  | `data models` · `external apis` · `queries` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `database extracts` · `database systems` · `elt` |
| 🟢 only in v33  | `data models` · `external apis` · `s3` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `database extracts` · `database systems` · `elt` |
| 🟢 only in v33  | `data models` · `external apis` · `s3` |

---

## row_id 22 ⚑ — AWS/Big Data Engineer
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `machine learning` |
| 🟢 only in v33  | `machine learning models` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `machine learning` |
| 🟢 only in v33  | `machine learning models` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `machine learning` |
| 🟢 only in v33  | `machine learning models` |

---

## row_id 23 ⚑ — Business Intelligence Analyst
*v32 human skills_required_accuracy: 2*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `architectures` · `it guidelines` |
| 🟢 only in v33  | `geo-spatial analysis` · `process flow design` · `process flow documentation` · `statistical analysis` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `2 - 5 years experience in a healthcare environment` · `call center reporting experience` · `clinical analytics experience` · `experience developing tableau dashboards` · `experience with geo-spatial analysis tools (e.g. esri)` · `experience with statistical analysis tools (e.g. sas, r, etc.)` · `experienced tableau user` · `healthcare claims reporting experience` |
| 🟢 only in v33  | `o 2 - 5 years experience in a healthcare environment` · `o call center reporting experience` · `o clinical analytics experience` · `o experience developing tableau dashboards` · `o experience with geo-spatial analysis tools (e.g. esri)` · `o experience with statistical analysis tools (e.g. sas, r, etc.)` · `o experienced tableau user` · `o healthcare claims reporting experience` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `application design` · `architectures` · `best-practices` · `business intelligence` · `business process improvement` · `business processes` · `data analysis` · `design` · `geo-spatial analysis tools` · `healthcare environment` · `it guidelines` · `reporting` · `statistical analysis tools` |
| 🟢 only in v33  | `process flow design` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `application design` · `architectures` · `best-practices` · `business intelligence` · `business process improvement` · `business processes` · `design` · `healthcare environment` · `it guidelines` · `reporting` · `statistical analysis tools` |
| 🟢 only in v33  | `process flow design` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `geo-spatial analysis tools` |

---

## row_id 24 ⚑ — Senior Data Analyst
*v32 human skills_required_accuracy: 2*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `3d pdfs` · `data analytics` · `data integration` · `geospatial analysis` · `pdfs` |
| 🟢 only in v33  | `3d pdf` · `anomaly detection` · `digital maps` · `global positioning systems` · `pattern recognition` · `pdf` · `predictive analytics` · `remotely sensed imagery` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `baccalaureate or higher degree in information technology, statistics, data analysis, geographic information systems (gis) [or in a related field that included 60 semester hours of course work in information technology, statistics, data analysis, geographic information systems (gis) or related disciplines of which at least (1) and 30 semester hours were in data visualization]` · `experience and proficiency with statistical analysis methods and related statistical analysis software (i.e.- r, spss, matlab)` · `experience with process mapping and workflow visualization tools such as visio` · `mastery of esri arcgis, arcsde, and related open source gis solutions. broad professional knowledge of federal geospatial data standards and use of relational databases for managing and processing data` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `3d pdfs` · `algebra` · `architecture` · `calculus` · `cartography` · `civil structural engineering` · `computer engineering` · `data analytics` · `data integration` · `data modeling` · `data modeling tools` · `data performance` · `electrical engineering` · `engineering` · `environmental engineering` · `geographic information systems` · `geography` · `geology` · `geophysics` · `geospatial analysis` · `hydrology` · `land surveying` · `mathematical and statistical sciences` · `mechanical engineering` · `natural resource management` · `object oriented paradigm` · `ontologies` · `pdfs` · `physical sciences` · `statistical analysis methods` · `topographical sciences` · `workflow visualization tools` |
| 🟢 only in v33  | `3d pdf` · `anomaly detection` · `arcsde` · `digital maps` · `esri arcgis` · `geographic information systems (gis)` · `global positioning systems` · `open source gis solutions` · `pattern recognition` · `pdf` · `predictive analytics` · `remotely sensed imagery` · `workflow visualization` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `3d pdfs` · `algebra` · `architecture` · `calculus` · `cartography` · `civil structural engineering` · `data integration` · `data modeling` · `data modeling tools` · `data performance` · `electrical engineering` · `engineering` · `environmental engineering` · `federal geospatial data standards` · `geographic information systems` · `geography` · `geology` · `geophysics` · `geospatial analysis` · `hydrology` · `land surveying` · `mathematical and statistical sciences` · `matlab` · `mechanical engineering` · `natural resource management` · `object oriented paradigm` · `ontologies` · `pdfs` · `physical sciences` · `r` · `spss` · `statistical analysis methods` · `topographical sciences` · `visio` · `workflow visualization tools` |
| 🟢 only in v33  | `3d pdf` · `anomaly detection` · `digital maps` · `geographic information systems (gis)` · `global positioning systems` · `pattern recognition` · `pdf` · `predictive analytics` · `remotely sensed imagery` · `workflow visualization` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `arcsde` · `esri arcgis` · `federal geospatial data standards` · `matlab` · `open source gis solutions` · `r` · `spss` · `visio` |

---

## row_id 25 ⚑ — Data Scientist
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `a.i.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `a.i.` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `a.i.` |

---

## row_id 26 — Data Analyst
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `excel` · `microsoft word` · `powerpoint` |
| 🟢 only in v33  | `m6a rna rip-seq` · `m6a-seq` · `rna-clip-seq` · `rna-seq` · `sequencing libraries` · `statistical analysis` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `statistical tools` |
| 🟢 only in v33  | `computer programs` · `sequencing libraries` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `statistical tools` |
| 🟢 only in v33  | `computer programs` · `sequencing libraries` |

---

## row_id 27 ⚑ — Principal Scientist-R&D Analytical-Raw Materials
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `material characterization` · `raw material characterization` |
| 🟢 only in v33  | `dsc` · `dvs` · `particle size measurements` · `powder flow` · `rheometry` · `sem` · `xrpd` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `analytical characteristics` · `chemical characterization` · `physical characterization` · `raw material functionality` · `raw materials` · `regulated industry` |
| 🟢 only in v33  | `compressibility` · `flowability` · `morphology` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `analytical characteristics` · `chemical characterization` · `physical characterization` · `raw material functionality` · `raw materials` · `regulated industry` |
| 🟢 only in v33  | `compressibility` · `flowability` · `morphology` |

---

## row_id 28 — Quantitative Researcher/Strategy Developer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `trading models` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `algorithmic trading strategies` · `computer science` · `engineering` · `financial markets` · `mathematics` · `physics` · `quantitative finance` · `research tools` · `software` · `statistics` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `algorithmic trading strategies` · `engineering` · `financial markets` · `mathematics` · `physics` · `quantitative finance` · `research tools` · `software` · `statistics` |

---

## row_id 29 — Video Business Data Scientist, Apple Media Products Data Science
### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `strong proficiency with sql-based languages with experience with large scale analytics technologies such as hadoop and spark.` |
| 🟢 only in v33  | `familiarity with python, command line, git, keynote, and data visualization tools such as tableau for full-stack data analysis, insight synthesis and presentation.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `analytics` · `business strategy` · `data democratizing` · `data gathering` · `data governance` · `data science` · `data visualization` · `est` · `key performance indicators` · `large-scale data` · `subscription` · `transactional` · `video business` · `vod` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `business strategy` · `data democratizing` · `data gathering` · `data governance` · `data visualization` · `est` · `key performance indicators` · `large-scale data` · `subscription` · `transactional` · `video business` · `vod` |

---

## row_id 30 — Senior Scientist / Principal Scientist, DMPK
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `drug discovery` · `ind submissions` · `pharmacodynamic endpoints` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `dmpk` · `isotope-based studies` · `pharmacokinetics` |
| 🟢 only in v33  | `biological samples` · `drug proteomics` · `isotope-based` · `qualitative data` · `quantitative data` · `sample preparation techniques` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `dmpk` · `pharmacokinetics` |
| 🟢 only in v33  | `drug proteomics` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `isotope-based studies` |
| 🟢 only in v33  | `biological samples` · `isotope-based` · `qualitative data` · `quantitative data` · `sample preparation techniques` |

---

## row_id 31 — Lead Data Engineer
### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `experience with cloud data ingestion, data lake, and modern warehouse solutions (azure is a plus)` |
| 🟢 only in v33  | `experience with cloud data ingestion, data lake, and modern warehouse solutions (azure is a plus).` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `agile development methodologies` · `best practices` · `data analytics` · `data integration` · `data models` · `data pipelines` · `data platform architecture` · `data quality` · `financial services` · `modern data management` · `no-sql` · `real time data pipelines` |
| 🟢 only in v33  | `agile` · `data quality framework` · `data streaming` · `nosql` · `real-time data pipelines` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `best practices` · `data integration` · `data models` · `data platform architecture` · `data quality` · `modern data management` · `no-sql` · `real time data pipelines` |
| 🟢 only in v33  | `data quality framework` · `data streaming` · `nosql` · `real-time data pipelines` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `agile development methodologies` · `financial services` |
| 🟢 only in v33  | `agile` |

---

## row_id 32 — Modeling and Simulation / MBSE Tools Data Scientist
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `capability maturity model integrated` · `cmmi` · `integrated development environments` · `knowledge representation & reasoning` · `kr&r` · `system engineering process` |
| 🟢 only in v33  | `capability maturity model integrated (cmmi)` · `integrated development environments (ides)` · `knowledge representation & reasoning (kr&r)` · `system engineering process (sep)` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `one (1) or more years of experience developing or applying semantic web technologies including but not limited to: web ontology language (wol) and resource description framework (rdf)` · `one (1) year of experience developing or applying machine learning and/or knowledge representation & reasoning (kr&r) tools, techniques, and/or algorithms` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `abet` · `c4i` · `capability maturity model integrated` · `cmmi` · `combat` · `data models` · `hm&e` · `integrated development environments` · `knowledge representation & reasoning` · `kr&r` · `logical data models` · `m&s` · `navigation` · `rdf` · `resource description framework` · `secret clearance` · `semantic web` · `simulations` · `system engineering process` · `web ontology language` · `wol` |
| 🟢 only in v33  | `capability maturity model integrated (cmmi)` · `databases` · `integrated development environments (ides)` · `knowledge representation & reasoning (kr&r)` · `resource description framework (rdf)` · `semantic web technologies` · `system engineering process (sep)` · `web ontology language (wol)` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `abet` · `c4i` · `capability maturity model integrated` · `cmmi` · `combat` · `data models` · `hm&e` · `integrated development environments` · `knowledge representation & reasoning` · `kr&r` · `logical data models` · `m&s` · `machine learning` · `navigation` · `rdf` · `resource description framework` · `secret clearance` · `semantic web` · `simulations` · `system engineering process` · `web ontology language` · `wol` |
| 🟢 only in v33  | `capability maturity model integrated (cmmi)` · `databases` · `integrated development environments (ides)` · `knowledge representation & reasoning (kr&r)` · `system engineering process (sep)` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `machine learning` · `resource description framework (rdf)` · `semantic web technologies` · `web ontology language (wol)` |

---

## row_id 33 — Senior Big Data Engineer
### Preferred signals found
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `experience in financial services industry a plus.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `agile methodologies` · `analytical architecture` · `cloud based data technology` · `compressions` · `data lake` · `data models` · `data processing pipelines` · `hadoop file format` · `java object oriented programming` · `real time data ingestion` · `software development lifecycle` · `structured application development methodology` |
| 🟢 only in v33  | `change data capture` · `object oriented programming` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `agile methodologies` · `analytical architecture` · `cloud based data technology` · `compressions` · `data lake` · `data models` · `data processing pipelines` · `hadoop file format` · `java object oriented programming` · `real time data ingestion` · `software development lifecycle` · `structured application development methodology` · `test driven code development` |
| 🟢 only in v33  | `cdc` · `change data capture` · `object oriented programming` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `cdc` |
| 🟢 only in v33  | `test driven code development` |

---

## row_id 34 — Electronics Engineering Scientist
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `calibration` · `characterization` · `data analysis` · `testing` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `demonstrated excellent interpersonal communication skills.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `acquisition system` · `electrical engineering` · `ieee bus standards` · `instrumentation equipment` · `ipcore` · `master's degree in electrical engineering` · `professional software development` · `research oriented software development` · `transducer` |
| 🟢 only in v33  | `ipcore development` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `acquisition system` · `electrical engineering` · `instrumentation equipment` · `master's degree in electrical engineering` · `measurement and instrumentation hardware systems` · `professional software development` · `research oriented software development` · `signal processing` · `transducer` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `instrumentation equipment` · `ipcore` · `professional software development` · `research oriented software development` |
| 🟢 only in v33  | `ipcore development` |

---

## row_id 35 — Software Engineer (Data Scientist, C,C++,Linux,Unix) - SISW - MG
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `software engineering` |
| 🟢 only in v33  | `modeling data` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `semiconductor manufacturing` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `semiconductor manufacturing` |

---

## row_id 36 — Data Scientist
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `application/dashboard development` · `data modeling` · `data science` · `microsoft office` · `predictive analytics` · `python` · `r` · `sas` · `sql` · `tableau` · `tableau creator` |
| 🟢 only in v33  | `benchmarks` · `data analysis` · `data import` · `data science techniques` · `evidence-base` · `health information technology` · `literature review` · `methodologies` · `study design` · `thresholds` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `mush have expert level skills in one or more of the following: python, r, sql, sas, tableau/tableau creator and application/dashboard development.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `data science` · `naci` |
| 🟢 only in v33  | `data analysis` · `data mining` · `naci background check` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `application/dashboard development` · `naci` · `python` · `r` · `sas` · `sql` · `tableau` · `tableau creator` |
| 🟢 only in v33  | `data mining` · `naci background check` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `application/dashboard development` · `python` · `r` · `sas` · `sql` · `tableau` · `tableau creator` |

---

## row_id 37 — Principal Scientist, Computational Genomics
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `computing platforms` |
| 🟢 only in v33  | `genotype/phenotype data` · `high performance computing` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `computing platforms` · `drug discovery and development` |
| 🟢 only in v33  | `bioinformatics` · `biomedical sciences` · `computer/computational sciences` · `data science` · `drug discovery and development practices` · `engineering` · `large-scale computing` · `m.d.` · `mathematics/statistics` · `ph.d.` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `computing platforms` |
| 🟢 only in v33  | `bioinformatics` · `biomedical sciences` · `computer/computational sciences` · `engineering` · `high performance computing` · `large-scale computing` · `m.d.` · `mathematics/statistics` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `drug discovery and development` · `high performance computing` |
| 🟢 only in v33  | `drug discovery and development practices` |

---

## row_id 38 — Big Data Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `java` · `python` · `scala` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `big data` · `programming` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `big data` · `java` · `programming` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `java` |

---

## row_id 39 — Business Intelligence Analyst
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `programming languages` · `software` |
| 🟢 only in v33  | `apache spark` · `cognos` · `excel` · `microsoft office` · `oracle` · `python` · `r` · `sas` · `sql` · `tableau` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `understanding of property casualty insurance principles, laws, regulations, underwriting rules guidelines, policy contract coverage and conditions desired.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `actuarial science` · `dashboards` · `finance` · `insurance` · `mathematics` · `programming languages` · `reports` · `scorecards` · `software` · `statistics` |
| 🟢 only in v33  | `underwriting rules` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `actuarial science` · `dashboards` · `insurance` · `mathematics` · `policy contract coverage` · `programming languages` · `property casualty insurance` · `scorecards` · `software` · `statistics` · `underwriting guidelines` |
| 🟢 only in v33  | `apache spark` · `cognos` · `excel` · `microsoft office` · `oracle` · `python` · `r` · `sas` · `sql` · `tableau` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `apache spark` · `cognos` · `excel` · `microsoft office` · `oracle` · `python` · `r` · `sas` · `sql` · `tableau` |
| 🟢 only in v33  | `policy contract coverage` · `property casualty insurance` · `underwriting guidelines` · `underwriting rules` |

---

## row_id 40 — Research Scientist - Dr. Kapil N. Bhalla's Laboratory
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `analytical techniques` · `protocols` · `standard procedures` |
| 🟢 only in v33  | `2d gels` · `chromatin immunoprecipitation` · `confocal microscopy` · `crispr` · `flow cytometry` · `gene transfection` · `immunoblots` · `microarrays` · `qpcr` · `tissue culture` · `yeast-two-hybrid system` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `epigenetic mechanisms` · `gene editing` · `leukemia stem/progenitor cells` · `phd` · `post-doctoral fellowship` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `epigenetic mechanisms` · `gene editing` · `leukemia stem/progenitor cells` · `post-doctoral fellowship` |
| 🟢 only in v33  | `confocal microscopy` · `crispr` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `confocal microscopy` · `crispr` |

---

## row_id 41 — Sr. Scientist
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `electrochemical biosensor development` · `fda 510k submission` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `biochemistry` · `chemistry` · `fda 510k submission` · `ivd industry` · `quality system environment` |
| 🟢 only in v33  | `510k submission` · `biochemistry assay development` · `ivd` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `biochemistry` · `chemistry` · `fda 510k submission` · `ivd industry` · `quality system environment` |
| 🟢 only in v33  | `510k submission` · `biochemistry assay development` · `ivd` |

---

## row_id 42 — Machine Learning Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `data processing pipelines` · `machine learning models` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `pluses:
undergraduate degree in computer science
experience with sql or other database systems
experience with deep learning techniques` |
| 🟢 only in v33  | `experience with deep learning techniques` · `experience with sql or other database systems` · `pluses:
undergraduate degree in computer science` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `data science` · `deep learning` · `machine learning` |
| 🟢 only in v33  | `data processing pipelines` · `deep learning techniques` · `machine learning models` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `machine learning` |
| 🟢 only in v33  | `data processing pipelines` · `machine learning models` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `deep learning` |
| 🟢 only in v33  | `deep learning techniques` |

---

## row_id 43 — Data Analyst - Intelligent Automation
### All technical skills
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `business intelligence` · `etl` |

### Skills required
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `business intelligence` · `etl` |

---

## row_id 44 — Senior Quantitative Researcher, Strategy Developer, Buy-Side
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `trading models` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `*looking for candidates from top tier universities with a strong gpa. phd in mathematics, statistics, physics or engineering is preferred.` |
| 🟢 only in v33  | `*looking for candidates from top tier universities with a strong gpa. phd in mathematics, statistics, physics or engineering is preferred. will consider candidates who have a master's degree along with work experience.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `buy-side firm` · `financial market data` · `financial markets` · `predictive models` · `programming concepts` · `research tools` · `software` |
| 🟢 only in v33  | `phd` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `buy-side firm` · `financial market data` · `financial markets` · `predictive models` · `programming concepts` · `research tools` · `software` |
| 🟢 only in v33  | `futures` · `high frequency` · `mathematics` · `physics` · `statistics` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `futures` · `high frequency` · `mathematics` · `physics` · `statistics` |

---

## row_id 45 — Data Analyst II
### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `claims data` · `cms reporting` · `data cleansing` · `data reconciliation` · `financial data` · `health management programs` · `hedis reporting` · `hhsc reporting` · `irs reporting` · `member data` · `pharmacy data` · `predictive data modeling` · `provider data` · `trend analysis` |
| 🟢 only in v33  | `cms` · `hedis` · `hhsc` · `irs` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `claims data` · `cms reporting` · `data cleansing` · `data reconciliation` · `financial data` · `health management programs` · `hedis reporting` · `hhsc reporting` · `irs reporting` · `member data` · `pharmacy data` · `predictive data modeling` · `provider data` · `trend analysis` |
| 🟢 only in v33  | `cms` · `hedis` · `hhsc` · `irs` |

---

## row_id 46 — Data Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `agile` |
| 🟢 only in v33  | `etl` · `hadoop` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `infa` · `scoop` |
| 🟢 only in v33  | `informatica` · `sqoop` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `infa` · `scoop` |
| 🟢 only in v33  | `informatica` · `sqoop` |

---

## row_id 47 — Data Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `project management` |
| 🟢 only in v33  | `etl` · `hadoop` · `hive` · `linux` · `python` · `spark` · `sql` · `unix` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `code reviews` |

### Skills required
| Direction | Tokens |
|---|---|
| 🟢 only in v33  | `code reviews` |

---

## row_id 48 — Data Engineer
### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `familiarity or strong desire to learn quantitative analysis techniques (e.g., predictive modeling, machine learning, segmentation, optimization, clustering, regression).` · `familiarity with implementing analytics solutions with one or more hadoop distributions (cloudera, hortonworks, mapr, hdinsight, emr).` · `familiarity with streaming data ingestion.` · `proficient in python and/or java.` |
| 🟢 only in v33  | `* familiarity with implementing analytics solutions with one or more hadoop distributions (cloudera, hortonworks, mapr, hdinsight, emr)* familiarity with streaming data ingestion* proficient in python and/or java* consulting experience* familiarity or strong desire to learn quantitative analysis techniques (e.g., predictive modeling, machine learning, segmentation, optimization, clustering, regression)` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `business intelligence` |
| 🟢 only in v33  | `data engineering` · `data ingestion` · `data profiling` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `business intelligence` |
| 🟢 only in v33  | `data ingestion` · `data profiling` · `hadoop` · `streaming data ingestion` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `hadoop` · `streaming data ingestion` |

---

## row_id 49 — Big Data Engineer
### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `computer science` · `math` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32b | `math` |

---