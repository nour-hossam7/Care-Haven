# CareHaven Data Summary

This document consolidates the central CareHaven data documentation. The current internal datasets are synthetic, generated locally, and contain no real personal data. The data architecture supports future humanitarian decision-support experiments while keeping case evidence, trusted knowledge, and external Computer Vision data separate.

## 1. Data Architecture

- `raw/` contains source-form structured data, generated cases, donors, donations, case evidence, and trusted RAG documents.
- `processed/` is reserved for cleaned or derived data, feature engineering, image processing, document processing, and future embeddings.
- `external/` contains selected external Computer Vision data and is kept separate from internal case data.

The central relationship is:

```text
Donor
  ↓
Donation
  ↓
Case
```

Each case may contain:

```text
Case
├── Structured Data
├── Description
├── Evidence Images
└── Supporting Documents
```

Planned decision-support uses include case analysis, priority scoring, NLP, Computer Vision, fraud or anomaly review, recommendations, analytics, and prediction. These capabilities are not implemented by the current data layer.

## 2. Current Data Sources

| Data source | Location | Purpose | Status | Size | Used by |
|---|---|---|---|---:|---|
| Cases | `data/raw/cases/cases.csv` | Synthetic case descriptions, needs, funding, priority, status, and locations | Existing | 500 rows | Case analysis, priority, NLP, geography, prediction |
| Donors | `data/raw/donors/donors.csv` | Anonymous synthetic donor preferences and budgets | Existing | 100 rows | Recommendation and matching |
| Donations | `data/raw/donations/donations.csv` | Synthetic donor-to-case funding events | Existing | 1,000 rows | Funding analysis, anomaly signals, recommendation, prediction |
| External CV dataset | `data/external/disaster_images/` | Future disaster-image inspection and evidence signals | Existing | 13,557 images; 13,556 readable; 1 corrupted | Computer Vision |
| Case evidence | `data/raw/images/synthetic/demo_case_evidence/`, `data/raw/documents/case_evidence/`, and `data/raw/case_evidence_manifest.csv` | Synthetic case-linked images and support notes for verification workflow testing | Downloaded | 40 cases, 40 images, 10 documents, 50 manifest records | Verification signals and human review |
| RAG documents | `data/raw/documents/rag/` | Trusted humanitarian guidance | Downloaded | 1 document | Future grounded humanitarian knowledge |
| Geographic information | Location and coordinate fields in `cases.csv` | Maps and geographic analytics | Existing | 500 rows with locations | Geographic analytics and visualization |
| Derived anomaly signals | Future pipeline outputs | Duplicate, conflict, unusual-pattern, and image-quality signals | Derived later | Not created | Fraud/anomaly review |
| Processed features and embeddings | `data/processed/` | Future transformed artifacts | To be generated later | Not created | Future modeling workflows |

Status values are `EXISTING`, `DOWNLOADED`, `PLACEHOLDER`, `TO BE GENERATED LATER`, and `DERIVED LATER`.

## 3. Cases Dataset

Location: `raw/cases/cases.csv`

Each row represents one synthetic humanitarian-assistance case, including its location, operational needs, funding position, status, and priority label.

| Field | Type | Description |
|---|---|---|
| `case_id` | String | Unique identifier in the format `CASE-0001`. |
| `description` | String | Synthetic humanitarian-assistance narrative. |
| `assistance_category` | Categorical string | Food, Medical Aid, Emergency Housing, Water, Clothing, or Education. |
| `people_affected` | Integer | Number of affected people; positive integer. |
| `country` | String | Generated country. |
| `governorate` | String | Governorate or comparable region. |
| `city` | String | Generated city. |
| `latitude` | Decimal | Generated latitude from -90 to 90. |
| `longitude` | Decimal | Generated longitude from -180 to 180. |
| `severity` | Categorical string | Low, Medium, High, or Critical. |
| `urgency` | Categorical string | Low, Medium, High, or Critical. |
| `required_resources` | String | Semicolon-separated requested resources. |
| `estimated_funding` | Decimal | Total estimated funding needed; greater than zero. |
| `current_funding` | Decimal | Donations received, from zero through estimated funding. |
| `submission_date` | Date | ISO 8601 date in `YYYY-MM-DD` format. |
| `status` | Categorical string | Active, Under Review, Funded, or Completed. |
| `priority` | Categorical string | Synthetic label: Low, Medium, High, or Critical. |

### Synthetic priority rule

Priority is generated from numeric bands for severity, urgency, affected population, and funding-gap ratio, plus one point for Medical Aid or Emergency Housing:

- `13+`: Critical
- `10–12`: High
- `7–9`: Medium
- Below `7`: Low

These are transparent rule-based labels for future experimentation, not Machine Learning predictions.

## 4. Donors and Donations

### Donors

Location: `raw/donors/donors.csv`

Donor records are anonymous synthetic records and contain no names, contact details, or real personal information.

| Field | Type | Description |
|---|---|---|
| `donor_id` | String | Unique identifier in the format `DONOR-001`. |
| `preferred_category` | Categorical string | Preferred assistance category. |
| `budget` | Decimal | Synthetic available donation budget; greater than zero. |
| `preferred_location` | String | Preferred country and governorate. |
| `urgency_preference` | Categorical string | Preferred urgency: Low, Medium, High, or Critical. |
| `previous_donations` | Integer | Number of previous synthetic donations; zero or greater. |

### Donations

Location: `raw/donations/donations.csv`

Each donation links one donor to one case. The sum of donations for each case equals its `current_funding` value.

| Field | Type | Description |
|---|---|---|
| `donation_id` | String | Unique identifier in the format `DONATION-0001`. |
| `donor_id` | String | Foreign key to an existing donor. |
| `case_id` | String | Foreign key to an existing case. |
| `amount` | Decimal | Positive donation amount. |
| `date` | Date | ISO date on or after the case submission date. |

## 5. Case Evidence and Supporting Documents

Current evidence files are synthetic demonstrations only. Future user uploads require an approved secure process.

- Evidence images are associated with cases under `raw/images/`.
- Case-specific supporting documents are stored under `raw/documents/case_evidence/`.
- Supporting documents may include proof documents, damage reports, receipts, invoices, official letters, and PDFs.
- The current demo contains 40 synthetic evidence images and 10 synthetic case-support notes.

Future automated signals may support OCR and text extraction, information extraction, consistency checks, case-information matching, suspicious-pattern detection, image relevance, duplicate detection, and image-quality checks. These signals only support human review. They do not prove legal authenticity, determine aid eligibility, or automatically accuse anyone of fraud.

## 6. RAG Knowledge Documents

Trusted humanitarian knowledge documents are stored separately under `raw/documents/rag/`. They may include humanitarian guidelines, emergency-response guidance, aid-distribution guidance, policies, and official reports.

The initial corpus contains one verified IFRC Emergency Needs Assessment and Planning Guidance PDF. WHO, UNHCR, and additional IFRC candidates remain documented as requiring file and usage-term verification before acquisition.

RAG guidance provides contextual support and does not determine legal eligibility. RAG documents are not case evidence, training labels, or substitutes for human review.

## 7. External Computer Vision Data

The Kaggle Disaster Images Dataset is stored separately under `external/disaster_images/` for future evidence-image research, including visible damage, relevant objects, image relevance, and verification signals.

The image files are Git-ignored. Lightweight metadata and corruption records are tracked separately. The external dataset is not internal case data, user-submitted evidence, or RAG knowledge data. Duplicate, near-duplicate, and image-quality examples may later be derived from selected evidence images using controlled copies and variations.

## 8. Component Requirements and Boundaries

| Component | Data source | Boundary |
|---|---|---|
| Case Analysis | Cases plus RAG documents | RAG grounds context; it does not determine legal eligibility. |
| Priority Scoring | Cases | Existing synthetic labels remain unchanged. |
| Computer Vision | External disaster images plus synthetic demo images | External reference data and synthetic evidence remain separate; demo SVGs are not user submissions. |
| Fraud / Anomaly | Cases, donations, and synthetic demo evidence signals | Signals route concerns to human review; there is no separate fraud dataset. |
| Recommendation | Donors, cases, and donations | Matching features are derived later. |
| RAG | Verified IFRC guidance | Trusted knowledge only; candidate sources are unresolved. |
| Geographic Analytics | Case location, latitude, and longitude | No separate geographic, weather, satellite, or GIS dataset. |
| Predictive Analytics | Cases, donations, and historical case fields | No separate prediction dataset. |
| NLP | Case descriptions, structured fields, and future RAG context | No separate NLP training dataset. |
| Image duplicate / quality checks | Future evidence-image pipeline | Derived later; no separate dataset. |

## 9. Provenance

### Downloaded official knowledge document

- **Document:** IFRC Emergency Needs Assessment and Planning Guidance
- **Organization:** International Federation of Red Cross and Red Crescent Societies (IFRC)
- **Domain:** `ifrc.org`
- **Download date:** 2026-09-09
- **Usage:** Humanitarian needs assessment and emergency planning reference
- **Personal data:** Not intended as personal data; content remains subject to source terms
- **License:** License and usage terms require verification
- **Official source page:** <https://www.ifrc.org/document/emergency-needs-assessment-and-planning-guidance>
- **Official file:** <https://www.ifrc.org/sites/default/files/2025-11/IFRC_Emergency_Needs%20Assessment_and_Planning.pdf>

### Existing external image dataset

The Disaster Images Dataset was extracted from a Kaggle source into `data/external/disaster_images/`. Original publisher and license details were not captured. Terms require verification. Images may depict people or property, but there is no case-identity linkage in this project.

### Official candidates not downloaded

The following candidates were identified but not acquired because a verifiable official downloadable file or usage terms were not available in the acquisition environment:

- WHO, *The HESPER Manual: Version 1.0: Rapid Assessment of Local Environmental Health Needs in Emergencies*
- UNHCR, *Emergency Handbook*
- IFRC, *Emergency Response Framework*

No substitute, guessed URL, third-party copy, or HTML file saved as PDF was added.

### Internal synthetic sources

The cases, donors, donations, 40 synthetic case evidence images, and 10 synthetic case-support notes were created locally. They contain no real personal data and are intended for demo workflow testing only.

## 10. Reproducing and Validating the Data

Run these commands from the repository root:

```powershell
python scripts/data/generate_synthetic_data.py
python scripts/data/validate_data.py
```

Generation uses a fixed seed and produces the same data each time. The validation script checks the generated data relationships and constraints.

## 11. Consolidated Directory Notes

The following directory-level notes were folded into this summary and are no longer kept as standalone files:

- `data/raw/documents/rag/README.md` — documents the trusted humanitarian knowledge corpus. It states that the current corpus is intentionally limited to one verified IFRC document and that future AI outputs must remain human-reviewed decision-support signals rather than eligibility decisions.
- `data/raw/documents/case_evidence/README.md` — describes the synthetic case-evidence workspace. It explains that the folder is reserved for demo or future user-uploaded case evidence, that no real personal data should be placed there, and that the current demo includes 40 synthetic image files and 10 supporting notes across 40 cases.
- `data/external/README.md` — explains the external Kaggle Disaster Images dataset and its purpose as a separate computer-vision reference resource rather than internal case data or RAG knowledge.
- `data/external/disaster_images/README.md` — summarizes the dataset contents, metadata, corruption tracking, and boundaries. It notes the dataset is approximately 659 MB, contains 13,557 PNGs across six classes, and is kept separate from CareHaven case evidence and trusted knowledge.

These directory summaries are intentionally redundant with the main project data architecture and provenance notes already listed above.
