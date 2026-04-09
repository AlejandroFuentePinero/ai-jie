# v32 vs v32b — head-to-head diff


*1/50 rows identical across all fields.*


Comparing all 50 rows across: responsibility_skills_found, preferred_signals_found, all_technical_skills, skills_required, skills_preferred


Rows flagged in v32 human eval (skills_required_accuracy ≤ 4): [0, 2, 3, 5, 6, 7, 9, 10, 12, 16, 17, 19, 20, 22, 23, 24, 25, 27]


- 🔴 only in v32 = dropped by v32b (noise candidates)


- 🟢 only in v32b = introduced by v32b (regression candidates)


---


## row_id 0 ⚑ — Quantum Principal Data Scientist- Industrial Process Sector Industry
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data pre-/post-processing` · `information architecture` · `numerics` · `quantum approaches` · `visualizing data` |
| 🟢 only in v32b | `qiskit` · `qiskit aqua` · `qiskit terra` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `optimization` · `quantum circuit design` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data engineering` · `data science` · `optimization` · `quantum circuit design` |

---

## row_id 1 — Associate Scientist - PCR
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `multiplexed` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `clinical validation experience is desirable` |
| 🟢 only in v32b | `clinical validation experience is desirable.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `biochemistry` · `molecular biology` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `biochemistry` · `molecular biology` |

---

## row_id 2 ⚑ — Director of Data Science - Big Data + Machine Learning
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytic approaches` · `consumer preference information` · `data science` · `data sources` |
| 🟢 only in v32b | `hadoop` · `machine learning` · `python` · `relational databases` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🟢 only in v32b | `analytic approaches` · `predictive models` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data engineering` · `data pipelines` · `data science` |
| 🟢 only in v32b | `analytic approaches` · `predictive models` |

---

## row_id 3 ⚑ — Director, Strategic Research Data Science
*v32 human skills_required_accuracy: 1*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data analysts` · `data scientists` · `database manager` · `market researchers` · `wip` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data analysts` · `data scientists` · `database manager` · `market researchers` · `wip` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data analysts` · `data scientists` · `database manager` · `demand generation` · `market researchers` · `wip` |

---

## row_id 4 — Data Engineer
### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `python` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🟢 only in v32b | `python` |

---

## row_id 5 ⚑ — Senior Data Engineer
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `python` · `r` · `warehouses` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `business intelligence` · `data pipelines` · `data processing` · `data storage` · `data warehouse` · `reporting systems` · `resource optimization` · `warehouses` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `business intelligence` · `data pipelines` · `data processing` · `data storage` · `data warehouse` · `reporting systems` · `resource optimization` · `warehouses` |
| 🟢 only in v32b | `spark` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `spark` |

---

## row_id 6 ⚑ — AVP, Quantitative Analyst, Portfolio Analytics, Risk and Reporting
*v32 human skills_required_accuracy: 3*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `ai` · `analytics` · `analytics calculators` · `big data` · `data flows` · `debugging` · `deep learning` · `financial engineering` · `investment financial models` · `machine learning` · `portfolio construction` · `report outputs` · `software development` · `testing` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytics` |
| 🟢 only in v32b | `credit products` · `enterprise analytics` · `processes` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `ai` · `analytics` · `big data` · `data flows` · `deep learning` · `derivatives` · `interest rates` · `investment financial models` · `machine learning` · `operations` · `report outputs` · `structured products` · `systems` |
| 🟢 only in v32b | `credit products` · `enterprise analytics` · `processes` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🟢 only in v32b | `ai` · `big data` · `deep learning` · `investment financial models` · `machine learning` |

---

## row_id 7 ⚑ — Data Scientist
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `agile management tools` · `historical data` · `modeling` · `point-of-sale data` · `scanner` · `simulations` · `survey` |
| 🟢 only in v32b | `agile` · `confluence` · `devops server` · `github` · `gitlab` · `jira` · `lean` · `r` · `team foundation server` · `trello` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🟢 only in v32b | `graduate-level experience preferred.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `additional languages` · `code` · `data imputation` · `ecological inference` · `models` · `survey` |
| 🟢 only in v32b | `computer science` · `data sources` · `frequency of collection` · `issue tracker` · `levels of measurement` · `mathematics` · `model-based approaches` · `quantitative social science` · `research science` · `sample frames` · `scanner data` · `scrum` · `software development` · `statistical and analytic techniques` · `statistics` · `survey data` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `code` · `data analysis` · `data imputation` · `ecological inference` · `models` · `optimization` · `production scale` · `sales data` · `survey` |
| 🟢 only in v32b | `confluence` · `data sources` · `devops server` · `frequency of collection` · `github` · `gitlab` · `issue tracker` · `jira` · `levels of measurement` · `mathematics` · `model-based approaches` · `quantitative social science` · `research science` · `sample frames` · `scanner data` · `software development` · `statistical and analytic techniques` · `statistics` · `survey data` · `team foundation server` · `trello` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `additional languages` · `confluence` · `devops server` · `github` · `gitlab` · `jira` · `team foundation server` · `trello` |
| 🟢 only in v32b | `scrum` |

---

## row_id 8 — Temporary Research Scientist, Medicinal Chemistry
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `biological data` · `organic synthesis` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🟢 only in v32b | `a desire to be part of a highly innovative company aimed at transforming the lives of people with serious diseases, their families and society` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `ph.d.` |

---

## row_id 9 ⚑ — Research Scientist/Senior Scientist
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `microwave devices` · `microwave semiconductor devices` · `physics-based models` |
| 🟢 only in v32b | `labview` · `matlab` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `advanced degree in science, engineering or related technical discipline is strongly preferred` · `current ts/sci clearance is strongly preferred` |
| 🟢 only in v32b | `advanced degree in science, engineering or related technical discipline is strongly preferred.` · `current ts/sci clearance is strongly preferred.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🟢 only in v32b | `cmos` · `gaas` · `gan` · `inp` · `microwave device physics` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data analysis` · `fabrication` · `ffrdc` · `reliability testing` · `security clearance` · `seta contractors` · `testing` |
| 🟢 only in v32b | `cmos` · `gaas` · `gan` · `inp` · `microwave device physics` |

---

## row_id 10 ⚑ — Director Data Scientist - Data Science Hub
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `advanced analytics` · `optimization` |
| 🟢 only in v32b | `analytical methods` · `data and information exploration` · `data sets` · `data sources` · `optimization techniques` · `systems` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data science solutions` · `optimization` |
| 🟢 only in v32b | `analytical methods` · `applied mathematics` · `data and information exploration` · `data sets` · `data sources` · `optimization techniques` · `quantitative economics` · `statistics` · `systems` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytical processes` · `computer science` · `data science` · `data science solutions` · `it` · `optimization` · `simulation` · `structured data` · `unstructured data` |
| 🟢 only in v32b | `analytical methods` · `applied mathematics` · `data and information exploration` · `data sets` · `data sources` · `optimization techniques` · `quantitative economics` · `statistics` |

---

## row_id 11 — Data Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data integrations` · `data pipelines` · `query performance tuning` · `stored procedures` |
| 🟢 only in v32b | `data warehouse` · `sql server` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `architecture` · `data integrations` · `data pipelines` · `data warehouse databases` · `query performance tuning` · `rotational databases` · `self-service data platform` · `sql` · `sql server 2014` · `sql server 2017` |
| 🟢 only in v32b | `data warehouse` · `pipeline` · `sql server` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `architecture` · `data integrations` · `data pipelines` · `data warehouse databases` · `query performance tuning` · `rotational databases` · `self-service data platform` · `sql` · `sql server 2014` · `sql server 2017` |
| 🟢 only in v32b | `data warehouse` · `pipeline` · `sql server` |

---

## row_id 12 ⚑ — Analytical Scientist I
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytical method development` · `analytical test methods` · `compendial methods` · `experimental procedures` · `formulation development` · `transfer` · `validation` |
| 🟢 only in v32b | `dea` · `epa` · `fda` · `osha` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytical method development` · `analytical test methods` · `api` · `cleaning verification swabbing` · `compendial methods` · `data acquisition` · `data integrity` · `experimental procedures` · `finished product testing` · `formulation development` · `in-process testing` · `material characterization` · `physical testing` · `raw material sampling` · `sample preparation` · `transfer` · `validation` |
| 🟢 only in v32b | `b.s. in chemistry` · `fractions` · `mean` · `percentages` · `proportions` · `ratios` · `relative standard deviation` · `standard deviation` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytical method development` · `analytical test methods` · `api` · `cleaning verification swabbing` · `compendial methods` · `data acquisition` · `data integrity` · `experimental procedures` · `finished product testing` · `formulation development` · `in-process testing` · `material characterization` · `physical testing` · `raw material sampling` · `sample preparation` · `transfer` · `validation` |
| 🟢 only in v32b | `b.s. in chemistry` · `fractions` · `mean` · `percentages` · `proportions` · `ratios` · `relative standard deviation` · `standard deviation` |

---

## row_id 13 — Analytics Manager (Web / Social)
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytics` · `boosting posts` · `budget` · `click tracking` · `competitive analysis` · `conversion rates` · `email metrics` · `mobile` · `organic traffic` · `pii` · `search engine trends` · `search results` · `social analytics` · `social media ad buys` · `targeting` · `ugc` · `website metrics` |
| 🟢 only in v32b | `awario` · `data studio` · `google analytics` · `moz` · `revealbot` · `supermetrics` · `true social metrics` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytics` · `click tracking` · `competitive analysis` · `email metrics` · `mobile` · `organic traffic` · `pii` · `search engine trends` · `search results` · `social analytics` · `social media ad buys` · `ugc` · `website metrics` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytics` · `click tracking` · `competitive analysis` · `email metrics` · `mobile` · `organic traffic` · `pii` · `search engine trends` · `search results` · `social analytics` · `social media ad buys` · `ugc` · `website metrics` |

---

## row_id 14 — VP, Data Scientist
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `adtech` · `analytical tools` · `data acquisition` · `engineering` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `advantage for hands on experience with emerging statistical methods/techniques (e.g. machine learning and/or artificial intelligence)` |
| 🟢 only in v32b | `advantage for hands on experience with emerging statistical methods/techniques (e.g. machine learning and/or artificial intelligence).` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `ad-tech` · `analytical tools` · `data acquisition` · `engineering` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `ad-tech` · `analytical tools` · `data acquisition` · `data science` · `engineering` |

---

## row_id 15 — Data Scientist - Alpha Insights
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `exploratory techniques` · `ranking algorithms` · `recommendation algorithms` · `statistical analysis` · `visualizations` |
| 🟢 only in v32b | `pandas` · `r` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data science` · `exploratory techniques` · `finance` · `imperative programming language` · `software engineering` · `statistical analysis` · `visualizations` |
| 🟢 only in v32b | `data analysis` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `computer science` · `data science` · `exploratory techniques` · `finance` · `imperative programming language` · `software engineering` · `statistical analysis` · `visualizations` |

---

## row_id 16 ⚑ — Data Engineer
*v32 human skills_required_accuracy: 3*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `cloud` · `dashboards` · `data lake` · `data models` · `data warehouse` · `kpis` · `metadata` · `reports` |
| 🟢 only in v32b | `power bi` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data dictionaries` · `kpi` |
| 🟢 only in v32b | `data architect` · `data definitions` · `enterprise data models` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `computer engineering` · `computer science` · `data dictionaries` · `kpi` · `metadata` · `programming courses` · `queries` · `reports` |
| 🟢 only in v32b | `data architect` · `data definitions` · `enterprise data models` · `healthcare` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `healthcare` |

---

## row_id 17 ⚑ — Microsoft Analytics Consultant
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🟢 only in v32b | `business process` · `data` · `intelligence tools` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🟢 only in v32b | `at least 3 years of experience in mdx(ssas)` · `at least 3 years of experience in sql server, ssis, ssrs, ssas` · `microsoft certification in azure based technology` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data mining` · `data modeling` · `erp solutions` · `process modeling` |
| 🟢 only in v32b | `erp` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data mining` · `data modeling` · `mdx` · `process modeling` · `sql server` · `ssas` · `ssis` · `ssrs` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `erp solutions` · `web applications` |
| 🟢 only in v32b | `mdx` · `sql server` · `ssas` · `ssis` · `ssrs` |

---

## row_id 18 — Big Data Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data lake` |

---

## row_id 19 ⚑ — Pre-Clinical Imaging Field Application Scientist
*v32 human skills_required_accuracy: 3*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `experimental design` · `instrumentation` · `multimodal imaging` · `optical imaging` · `r&d` · `tradeshows` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `academic accounts` · `applications` · `commercial accounts` · `dvm` · `experimental design` · `instrumentation` · `lead generation` · `live animal imaging` · `md` · `non-invasive imaging` · `overnight travel` · `phd` · `preclinical imaging` · `vivarium environment` |
| 🟢 only in v32b | `non-invasive live animal imaging` · `vivarium` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `academic accounts` · `applications` · `bioluminescence` · `commercial accounts` · `dvm` · `experimental design` · `fluorescence` · `instrumentation` · `lead generation` · `live animal imaging` · `md` · `non-invasive imaging` · `overnight travel` · `phd` · `preclinical imaging` · `vivarium environment` |
| 🟢 only in v32b | `non-invasive live animal imaging` · `vivarium` |

---

## row_id 20 ⚑ — Python Data Engineer Trading
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `cloud` · `data caching` · `data management` · `data pipeline development` · `data quality` · `data sources` · `distributed data processing` · `fault tolerance` · `hadoop` · `iterative development process` · `linux` · `locality` · `on prem` · `optimization` · `pipelining` · `processing/storage formats` · `production models` · `research pipelines` · `spark` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `cloud` · `data caching` · `data management` · `data pipeline development` · `data quality` · `data sources` · `distributed data processing` · `fault tolerance` · `iterative development process` · `locality` · `on prem` · `optimization` · `pipelining` · `processing/storage formats` · `production models` · `research pipelines` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `cloud` · `data caching` · `data management` · `data pipeline development` · `data quality` · `data sources` · `distributed data processing` · `fault tolerance` · `iterative development process` · `locality` · `on prem` · `optimization` · `pipelining` · `processing/storage formats` · `production models` · `research pipelines` |

---

## row_id 21 — Data Engineer- Customer Data Platform
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data quality` · `data reliability` · `disaster recovery` · `software engineering` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `agile` · `data quality` · `data reliability` · `disaster recovery` · `elasticsearch` · `mapreduce` · `software engineering` |
| 🟢 only in v32b | `database extracts` · `database systems` · `elastic search` · `elt` · `map-reduce` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `agile` · `data quality` · `data reliability` · `disaster recovery` · `elasticsearch` · `mapreduce` · `software engineering` |
| 🟢 only in v32b | `database extracts` · `database systems` · `elastic search` · `elt` · `map-reduce` |

---

## row_id 22 ⚑ — AWS/Big Data Engineer
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data science` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data science` |

---

## row_id 23 ⚑ — Business Intelligence Analyst
*v32 human skills_required_accuracy: 2*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `business processes` · `it` |
| 🟢 only in v32b | `architectures` · `esri` · `it guidelines` · `r` · `sas` · `sql` · `ssrs` · `tableau` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `o 2 - 5 years experience in a healthcare environment` · `o call center reporting experience` · `o clinical analytics experience` · `o experience developing tableau dashboards` · `o experience with geo-spatial analysis tools (e.g. esri)` · `o experience with statistical analysis tools (e.g. sas, r, etc.)` · `o experienced tableau user` · `o healthcare claims reporting experience` |
| 🟢 only in v32b | `2 - 5 years experience in a healthcare environment` · `call center reporting experience` · `clinical analytics experience` · `experience developing tableau dashboards` · `experience with geo-spatial analysis tools (e.g. esri)` · `experience with statistical analysis tools (e.g. sas, r, etc.)` · `experienced tableau user` · `healthcare claims reporting experience` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `geo-spatial analysis` · `healthcare` · `it` · `statistical analysis` |
| 🟢 only in v32b | `application design` · `architectures` · `best-practices` · `business process improvement` · `data analysis` · `design` · `geo-spatial analysis tools` · `healthcare environment` · `it guidelines` · `process flow documentation` · `reporting` · `statistical analysis tools` · `tableau dashboards` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `healthcare` · `it` · `statistical analysis` |
| 🟢 only in v32b | `application design` · `architectures` · `best-practices` · `business process improvement` · `design` · `esri` · `healthcare environment` · `it guidelines` · `process flow documentation` · `r` · `reporting` · `sas` · `statistical analysis tools` · `tableau` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `esri` · `geo-spatial analysis` · `r` · `sas` · `tableau` |
| 🟢 only in v32b | `geo-spatial analysis tools` · `tableau dashboards` |

---

## row_id 24 ⚑ — Senior Data Analyst
*v32 human skills_required_accuracy: 2*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `anomaly detection` · `digital maps` · `global position systems` · `pattern recognition` · `predictive analytics` · `remotely sensed imagery` |
| 🟢 only in v32b | `geospatial analysis` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `anomaly detection` · `arcsde` · `digital maps` · `esri arcgis` · `geographic information systems (gis)` · `global position systems` · `open source gis solutions` · `pattern recognition` · `predictive analytics` · `remotely sensed imagery` · `secret clearance` |
| 🟢 only in v32b | `geographic information systems` · `geospatial analysis` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `anomaly detection` · `arcsde` · `computer engineering` · `data analysis` · `data analytics` · `digital maps` · `esri arcgis` · `geographic information systems (gis)` · `global position systems` · `information technology` · `open source gis solutions` · `pattern recognition` · `predictive analytics` · `remotely sensed imagery` · `secret clearance` |
| 🟢 only in v32b | `geographic information systems` · `geospatial analysis` |

---

## row_id 25 ⚑ — Data Scientist
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytic tools` · `architects` · `behavioral data` · `data analysis` · `extract, transform and standardize data` · `reporting` · `software engineers` · `telemetry data` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytic tools` · `architects` · `behavioral data` · `data analysis` · `extract, transform and standardize data` · `reporting` · `software engineers` · `structured data` · `telemetry data` · `unstructured data` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytic tools` · `architects` · `behavioral data` · `data analysis` · `extract, transform and standardize data` · `reporting` · `software engineers` · `structured data` · `telemetry data` · `unstructured data` |

---

## row_id 26 — Data Analyst
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `computer programs` · `m6a rna rip-seq` · `m6a-seq` · `metabolome` · `rna-clip-seq` · `rna-seq` · `sequencing libraries` · `statistical analysis` |
| 🟢 only in v32b | `excel` · `microsoft word` · `powerpoint` · `python` · `r` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `computer programs` · `sequencing libraries` · `statistical analysis` |
| 🟢 only in v32b | `statistical tools` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `computer programs` · `sequencing libraries` · `statistical analysis` |
| 🟢 only in v32b | `statistical tools` |

---

## row_id 27 ⚑ — Principal Scientist-R&D Analytical-Raw Materials
*v32 human skills_required_accuracy: 4*

### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytical` · `legal` · `quality` · `raw material physical and chemical characterization` · `regulatory` · `technical teams` · `toxicology` |
| 🟢 only in v32b | `material characterization` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytical` · `compressibility` · `elemental impurities` · `flowability` · `legal` · `morphology` · `quality` · `raw material physical and chemical characterization` · `regulatory` · `residual solvents` · `toxicology` |
| 🟢 only in v32b | `analytical characteristics` · `chemical characterization` · `physical characterization` · `raw material functionality` · `raw materials` · `usp elemental impurities` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytical` · `compressibility` · `elemental impurities` · `flowability` · `legal` · `morphology` · `quality` · `raw material physical and chemical characterization` · `regulatory` · `residual solvents` · `toxicology` |
| 🟢 only in v32b | `analytical characteristics` · `chemical characterization` · `physical characterization` · `raw material functionality` · `raw materials` · `usp elemental impurities` |

---

## row_id 28 — Quantitative Researcher/Strategy Developer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `financial market data` · `predictive trading models` · `quantitative finance` · `research tools` · `software` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `financial market data` · `predictive trading models` · `programming` |
| 🟢 only in v32b | `algorithmic trading engine` · `algorithmic trading strategies` · `research platform` · `trading models` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `computer science` · `financial market data` · `predictive trading models` · `programming` |
| 🟢 only in v32b | `algorithmic trading engine` · `algorithmic trading strategies` · `research platform` · `trading models` |

---

## row_id 29 — Video Business Data Scientist, Apple Media Products Data Science
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `dashboards` · `data governance` · `datasets` · `key performance indicators` |
| 🟢 only in v32b | `command line` · `git` · `hadoop` · `python` · `spark` · `sql` · `tableau` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `familiarity with python, command line, git, keynote, and data visualization tools such as tableau for full-stack data analysis, insight synthesis and presentation.` |
| 🟢 only in v32b | `strong proficiency with sql-based languages with experience with large scale analytics technologies such as hadoop and spark.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `dashboards` · `datasets` · `digital media` · `entertainment` · `subscription business` |
| 🟢 only in v32b | `business strategy` · `data democratizing` · `data gathering` · `data visualization` · `est` · `subscription` · `transactional` · `video business` · `vod` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytics` · `dashboards` · `data science` · `datasets` · `digital media` · `entertainment` · `subscription business` |
| 🟢 only in v32b | `business strategy` · `command line` · `data democratizing` · `data gathering` · `data visualization` · `est` · `git` · `python` · `subscription` · `tableau` · `transactional` · `video business` · `vod` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `command line` · `git` · `python` · `tableau` |

---

## row_id 30 — Senior Scientist / Principal Scientist, DMPK
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `drug metabolism` · `human pk` · `ind submissions` · `lead optimization` · `pharmacodynamic endpoints` · `small molecules` · `target engagement` |
| 🟢 only in v32b | `pk` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `animal pk studies` · `biological samples` · `drug metabolism` · `human pk` · `pharmacodynamic endpoints` · `qualitative data` · `quantitative data` · `sample preparation techniques` · `small molecules` · `target engagement` |
| 🟢 only in v32b | `pk` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `animal pk studies` · `biological samples` · `drug metabolism` · `human pk` · `pharmacodynamic endpoints` · `qualitative data` · `quantitative data` · `sample preparation techniques` · `small molecules` · `target engagement` |
| 🟢 only in v32b | `pk` |

---

## row_id 31 — Lead Data Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `apis` · `data lineage` · `data quality` |
| 🟢 only in v32b | `api` · `business intelligence` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `agile` · `apis` · `business intelligence tools` · `data streaming` · `event streaming platforms` · `it processes` · `modern data warehousing` · `real-time data pipelines` · `secure data pipelines` |
| 🟢 only in v32b | `agile development methodologies` · `api` · `best practices` · `business intelligence` · `data analytics` · `data integration` · `data models` · `data pipelines` · `data platform architecture` · `modern data management` · `real time data pipelines` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `agile` · `apis` · `business intelligence tools` · `data streaming` · `event streaming platforms` · `it processes` · `modern data warehousing` · `real-time data pipelines` · `secure data pipelines` |
| 🟢 only in v32b | `api` · `best practices` · `business intelligence` · `data integration` · `data models` · `data platform architecture` · `modern data management` · `real time data pipelines` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🟢 only in v32b | `agile development methodologies` |

---

## row_id 32 — Modeling and Simulation / MBSE Tools Data Scientist
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `c4i` · `combat` · `cybersecurity` · `data models` · `hm&e` · `navigation` · `simulations` |
| 🟢 only in v32b | `capability maturity model integrated` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `computer engineer` · `cybersecurity` · `electrical engineer` · `electronics engineer` · `semantic web technologies` · `software engineer` |
| 🟢 only in v32b | `abet` · `capability maturity model integrated` · `logical data models` · `m&s` · `semantic web` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `computer engineer` · `cybersecurity` · `electrical engineer` · `electronics engineer` · `semantic web technologies` · `software engineer` |
| 🟢 only in v32b | `abet` · `capability maturity model integrated` · `logical data models` · `m&s` · `semantic web` |

---

## row_id 33 — Senior Big Data Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `automation` · `data integration` · `data quality` |
| 🟢 only in v32b | `hadoop` · `hbase` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `application development methodology` · `change data capture` · `cloud data platforms` |
| 🟢 only in v32b | `analytical architecture` · `cloud based data technology` · `compressions` · `data architecture` · `data lake` · `data models` · `data processing pipelines` · `hadoop file format` · `mapr` · `real time data ingestion` · `structured application development methodology` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `application development methodology` · `cloud data platforms` |
| 🟢 only in v32b | `analytical architecture` · `cloud based data technology` · `compressions` · `data architecture` · `data lake` · `data models` · `data processing pipelines` · `hadoop file format` · `real time data ingestion` · `scm` · `structured application development methodology` · `test driven code development` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `change data capture` · `mapr distribution of hadoop` · `scm` · `test driven code development` |
| 🟢 only in v32b | `mapr` |

---

## row_id 34 — Electronics Engineering Scientist
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `calibration` · `characterization` · `data analysis` · `hardware/software development` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `c language` · `calibration` · `characterization` · `custom ipcore development` · `data analysis` · `deployment` · `hardware/software development` · `labview realtime environment` · `project development` · `testing` |
| 🟢 only in v32b | `c` · `ipcore` · `labview realtime` · `master's degree in electrical engineering` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `calibration` · `characterization` · `data analysis` · `deployment` · `embedded hardware design` · `function generators` · `hardware/software development` · `ieee bus standards` · `oscilloscopes` · `project development` · `spectrum analyzers` · `testing` |
| 🟢 only in v32b | `instrumentation equipment` · `master's degree in electrical engineering` · `measurement and instrumentation hardware systems` · `professional software development` · `research oriented software development` · `signal processing` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `c language` · `custom ipcore development` · `labview realtime environment` |
| 🟢 only in v32b | `c` · `function generators` · `ipcore` · `labview realtime` · `oscilloscopes` · `spectrum analyzers` |

---

## row_id 35 — Software Engineer (Data Scientist, C,C++,Linux,Unix) - SISW - MG
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `modeling data` · `modeling suite of tools` · `semiconductor manufacturing` · `software` |
| 🟢 only in v32b | `software engineering` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `mathematical package` · `modeling data` · `software` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `mathematical package` · `modeling data` · `software` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data analysis` · `data science` |

---

## row_id 36 — Data Scientist
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analysis` · `data mining` · `evidence-base` · `health information technology` · `it` · `literature review` · `methodologies` · `program management` · `research` · `study design` |
| 🟢 only in v32b | `microsoft office` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analysis` · `analytics` · `data mining` · `evidence-base` · `hardware` · `health information technology` · `it` · `literature review` · `methodologies` · `program management` · `quantitative field fellowship/training` · `research` · `software` · `study design` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analysis` · `analytics` · `data mining` · `data science` · `evidence-base` · `hardware` · `health information technology` · `it` · `literature review` · `methodologies` · `program management` · `quantitative field fellowship/training` · `research` · `software` · `study design` |

---

## row_id 37 — Principal Scientist, Computational Genomics
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `genomics` · `genotype/phenotype data` · `tidvale` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `genomics` · `tidvale` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `genomics` · `tidvale` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data analytics` |

---

## row_id 38 — Big Data Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `big data` |
| 🟢 only in v32b | `java` · `python` · `scala` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `location:
plano, tx 75024 (preferred)` · `sr. big data engineer with 7+ years of programming experience with 1 or more programming language such as: java (preferred), python or scala is workable` |
| 🟢 only in v32b | `java (preferred), python or scala is workable` |

### Skills required
| Direction | Tokens |
|---|---|
| 🟢 only in v32b | `java` · `python` · `scala` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `java` · `python` · `scala` |

---

## row_id 39 — Business Intelligence Analyst
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `cognos` · `excel` · `microsoft office` · `sql` · `tableau` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `understanding of property casualty insurance principles, laws, regulations, underwriting rules guidelines, policy contract coverage and conditions desired.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `policy contract coverage and conditions` · `underwriting rules` |
| 🟢 only in v32b | `dashboards` · `policy contract coverage` · `programming languages` · `reports` · `scorecards` · `software` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `cognos` · `excel` · `finance` · `microsoft office` · `sql` · `tableau` |
| 🟢 only in v32b | `dashboards` · `policy contract coverage` · `programming languages` · `property casualty insurance` · `scorecards` · `software` · `underwriting guidelines` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `policy contract coverage and conditions` · `property casualty insurance` · `underwriting guidelines` · `underwriting rules` |
| 🟢 only in v32b | `cognos` · `excel` · `microsoft office` · `sql` · `tableau` |

---

## row_id 40 — Research Scientist - Dr. Kapil N. Bhalla's Laboratory
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `2d gels` · `bet proteins` · `biomarker development` · `chromatin immunoprecipitation` · `confocal microscopy` · `crispr` · `demethylases` · `epigenetic mechanisms` · `flow cytometry` · `gene transfection` · `genetically-engineered animal models` · `heat shock proteins` · `histone deacetylases` · `immunoblots` · `leukemia biology` · `methyltransferases` · `microarrays` · `qpcr` · `tissue culture` · `xenograft` · `yeast-two-hybrid system` |
| 🟢 only in v32b | `analytical techniques` · `protocols` · `standard procedures` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `leukemia biology` |
| 🟢 only in v32b | `cancer` · `gene editing` · `leukemia` · `leukemia stem/progenitor cells` · `phd` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `confocal microscopy` · `crispr` · `genetically-engineered animal models` · `leukemia biology` · `xenograft` |
| 🟢 only in v32b | `cancer` · `gene editing` · `leukemia` · `leukemia stem/progenitor cells` · `post-doctoral fellowship` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `post-doctoral fellowship` |
| 🟢 only in v32b | `confocal microscopy` · `crispr` · `genetically-engineered animal models` · `xenograft` |

---

## row_id 41 — Sr. Scientist
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `510k submission` |
| 🟢 only in v32b | `excel` · `fda 510k submission` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `510k submission` · `basic statistical analysis` · `biochemistry assay development` · `ph.d.` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `510k submission` · `basic statistical analysis` · `biochemistry assay development` · `ph.d.` |

---

## row_id 42 — Machine Learning Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data processing pipelines` · `data visualization` · `machine learning` · `machine learning models` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `experience with deep learning techniques` · `experience with sql or other database systems` · `pluses:
undergraduate degree in computer science` |
| 🟢 only in v32b | `pluses:
undergraduate degree in computer science
experience with sql or other database systems
experience with deep learning techniques` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data visualization` · `deep learning techniques` · `jupyterlab` · `machine learning models` · `version control` |
| 🟢 only in v32b | `data science` · `deep learning` · `jupyter lab` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `computer science` · `data visualization` · `jupyterlab` · `machine learning models` · `version control` |
| 🟢 only in v32b | `jupyter lab` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `deep learning techniques` |
| 🟢 only in v32b | `deep learning` |

---

## row_id 43 — Data Analyst - Intelligent Automation
*No differences.*

---

## row_id 44 — Senior Quantitative Researcher, Strategy Developer, Buy-Side
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `financial market data` · `financial markets` · `predictive models` · `quantitative finance` · `trading models` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🟢 only in v32b | `*looking for candidates from top tier universities with a strong gpa. phd in mathematics, statistics, physics or engineering is preferred.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `quantitative finance` |
| 🟢 only in v32b | `buy-side firm` · `engineering` · `machine learning` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `computer science` · `mathematics` · `physics` · `quantitative finance` · `statistics` |
| 🟢 only in v32b | `buy-side firm` · `machine learning` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🟢 only in v32b | `engineering` · `mathematics` · `physics` · `statistics` |

---

## row_id 45 — Data Analyst II
### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data analysis` |

---

## row_id 46 — Data Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data model development` · `etl` · `hadoop` · `informatica` · `model scoring` · `oracle` · `rdbms` · `teradata` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `bachelor's (preferred)` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data model development` · `extract, transform, load` · `informatica` · `model scoring` |
| 🟢 only in v32b | `infa` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data model development` · `extract, transform, load` · `informatica` · `model scoring` |
| 🟢 only in v32b | `infa` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `bachelor's` |

---

## row_id 47 — Data Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `code` · `engineering best practices` · `platforms` · `systems` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `code` · `code reviews` · `computer engineering` · `engineering best practices` · `masters` · `mba` · `platforms` · `project management` · `scripting` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `code` · `code reviews` · `computer engineering` · `engineering best practices` · `masters` · `mba` · `platforms` · `project management` · `scripting` |

---

## row_id 48 — Data Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytics` · `business intelligence` · `cloud data` · `cloud data warehouses` · `data wrangling` |

### Preferred signals found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `* familiarity with implementing analytics solutions with one or more hadoop distributions (cloudera, hortonworks, mapr, hdinsight, emr)* familiarity with streaming data ingestion* proficient in python and/or java* consulting experience* familiarity or strong desire to learn quantitative analysis techniques (e.g., predictive modeling, machine learning, segmentation, optimization, clustering, regression)` |
| 🟢 only in v32b | `familiarity or strong desire to learn quantitative analysis techniques (e.g., predictive modeling, machine learning, segmentation, optimization, clustering, regression).` · `familiarity with implementing analytics solutions with one or more hadoop distributions (cloudera, hortonworks, mapr, hdinsight, emr).` · `familiarity with streaming data ingestion.` · `proficient in python and/or java.` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytics` · `cloud data` · `cloud data warehouse tools` · `cloud data warehouses` · `data engineering` · `data ingestion` · `data profiling` · `data wrangling` · `hadoop distributions` · `quantitative analysis techniques` |
| 🟢 only in v32b | `cloud data warehouse` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `analytics` · `cloud data` · `cloud data warehouse tools` · `cloud data warehouses` · `data engineering` · `data ingestion` · `data profiling` · `data wrangling` · `hadoop` |
| 🟢 only in v32b | `cloud data warehouse` |

### Skills preferred
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `hadoop distributions` · `optimization` · `quantitative analysis techniques` |
| 🟢 only in v32b | `hadoop` |

---

## row_id 49 — Big Data Engineer
### Responsibility skills found
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data engineering` · `data pipelines` |

### All technical skills
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `data engineering` · `data pipelines` |
| 🟢 only in v32b | `data pipeline development` |

### Skills required
| Direction | Tokens |
|---|---|
| 🔴 only in v32  | `computer science` · `data engineering` · `data pipelines` |
| 🟢 only in v32b | `data pipeline development` |

---