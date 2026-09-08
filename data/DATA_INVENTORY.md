# CareHaven data inventory

Status values used here are `EXISTING`, `DOWNLOADED`, `PLACEHOLDER`, `TO BE GENERATED LATER`, and `DERIVED LATER`.

| Data Source | Location | Purpose | Source Type | Status | Rows/Images/Documents | Used By | Notes |
|---|---|---|---|---|---:|---|---|
| Cases | `data/raw/cases/cases.csv` | Synthetic case descriptions, structured needs, funding, priority, and locations | Synthetic demo data | EXISTING | 500 rows | Case analysis, priority scoring, NLP, geography, prediction | Preserve schema and labels exactly; no real personal data |
| Donors | `data/raw/donors/donors.csv` | Synthetic donor preferences and budgets | Synthetic demo data | EXISTING | 100 rows | Recommendation and matching | Anonymous synthetic records |
| Donations | `data/raw/donations/donations.csv` | Synthetic donor-to-case funding events | Synthetic demo data | EXISTING | 1,000 rows | Funding analysis, anomaly signals, recommendation, prediction | Foreign keys and totals validated by existing script |
| External CV Dataset | `data/external/disaster_images/` | Future disaster-image inspection and evidence signals | External Kaggle dataset | EXISTING | 13,557 images; 13,556 readable; 1 corrupted | Computer vision | Preserved separately; images remain Git-ignored |
| Case Evidence | `data/raw/images/synthetic/demo_case_evidence/`, `data/raw/documents/case_evidence/`, `data/raw/case_evidence_manifest.csv` | Synthetic case-linked images and supporting documents for verification workflow testing | Synthetic demo data | DOWNLOADED | 40 cases; 40 images; 10 documents; 50 manifest records | Verification signals and human review | Original synthetic illustrations and invented notes; no real personal documents |
| RAG Documents | `data/raw/documents/rag/` | Trusted humanitarian guidance | Official IFRC document | DOWNLOADED | 1 document | Future grounded humanitarian knowledge | Not case evidence, labels, or legal eligibility data; additional official candidates remain unresolved |
| Geographic information | Location and coordinate fields in `data/raw/cases/cases.csv` | Maps and geographic analytics | Synthetic case fields | EXISTING | 500 rows with location fields | Geographic analytics and visualization | No separate GIS, weather, or satellite dataset |
| Derived anomaly signals | Future pipeline outputs | Duplicate, conflict, unusual-pattern, and image-quality signals | Derived from existing sources | DERIVED LATER | Not created | Fraud/anomaly review | No separate fraud or image-quality dataset |
| Processed features and embeddings | `data/processed/` | Future transformed artifacts | Derived data | TO BE GENERATED LATER | Not created | Future modeling workflows | Explicitly out of scope for this raw-data phase |