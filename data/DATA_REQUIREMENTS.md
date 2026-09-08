# CareHaven data requirements matrix

The raw layer is intentionally minimal. No component below requires a new dataset at this stage.

| CareHaven component | Actual data source | Boundary |
|---|---|---|
| Case Analysis | `data/raw/cases/cases.csv` + `data/raw/documents/rag/` | RAG guidance grounds context; it does not determine legal eligibility |
| Priority Scoring | `data/raw/cases/cases.csv` | Existing synthetic priority labels remain unchanged |
| Computer Vision | `data/external/disaster_images/` + synthetic demo images in `data/raw/images/synthetic/demo_case_evidence/` | External CV reference data and synthetic case evidence remain separate; demo SVGs are not user submissions |
| Fraud / Anomaly | Cases + donations + synthetic demo evidence signals | Derived signals route concerns to human review; no separate fraud dataset |
| Recommendation | Donors + cases + donations | Matching features are derived later |
| RAG | Verified IFRC guidance in `data/raw/documents/rag/` | Trusted knowledge only; not case evidence or training labels; unresolved official candidates are not substituted |
| Geographic Analytics | Case location, latitude, and longitude fields | No separate geographic, weather, satellite, or GIS dataset |
| Predictive Analytics | Cases + donations + historical case fields | No separate prediction dataset |
| NLP | Case descriptions and structured case fields + future RAG context | No separate NLP training dataset |
| Image duplicate / quality checks | Future evidence-image pipeline | Derived later; no separate dataset |