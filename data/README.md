# CareHaven data

This folder contains the minimal CareHaven data architecture. The current CSV files are entirely synthetic, generated locally, and contain no real people or external data.

## Folder layout

- `raw/` holds source-form structured data, including the generated cases, donors, and donations CSV files. `images/` and `documents/` are reserved for future submitted assets.
- `processed/` is reserved for cleaned or derived data used by future experiments, feature engineering, image processing, and document processing.
- `external/` holds the selected external Computer Vision dataset separately from internal case data.

## Internal / synthetic data

`raw/cases/cases.csv` is the central humanitarian assistance dataset. Each row represents one case, its location, operational needs, funding position, status, and a synthetic priority label.

`raw/donors/donors.csv` represents anonymous synthetic donor preferences and budgets. It deliberately contains no names, contact details, or real personal information.

`raw/donations/donations.csv` records synthetic donations. Each donation links one donor to one case, and the sum of a case's donations equals its `current_funding` value.

## Case evidence and supporting documents

A future case combines structured information with uploaded evidence:

```text
Case
├── Structured Data
├── Description
├── Evidence Images
└── Supporting Documents
```

Evidence images will be associated with individual cases under `raw/images/`. Supporting documents are case-specific uploads stored under `raw/documents/case_evidence/`, such as proof documents, damage reports, receipts, invoices, official letters, and supporting PDFs.

Future automated signals may support OCR/text extraction, information extraction, consistency checks, case-information matching, and suspicious-pattern detection. They are decision-support signals for human review; they do not prove legal authenticity, decide aid eligibility, or automatically accuse a person of fraud.

## RAG knowledge documents

`raw/documents/rag/` is reserved for trusted humanitarian knowledge documents, such as humanitarian or emergency-response guidelines, aid-distribution guidelines, policies, and official reports. These documents are not case evidence and must remain separate from `case_evidence/`.

The initial RAG corpus contains one verified IFRC emergency needs assessment and planning guidance PDF. Candidate WHO and UNHCR sources remain documented as requiring file and usage-term verification before acquisition.

## Future external Computer Vision data

The Kaggle Disaster Images Dataset is integrated under `external/disaster_images/` for future evidence-image analysis, including visible damage, relevant objects, image relevance, and verification signals. It remains separate from internal cases, user-submitted evidence, and RAG documents. See [external/README.md](external/README.md).

Duplicate and near-duplicate examples, as well as image-quality examples, can later be derived from selected evidence images using controlled copies and variations. Fraud or anomaly signals should be derived from multiple sources and should always lead to human review.

## Relationships

```text
Donor
  ↓
Donation
  ↓
Case
```

```text
Case
 ├── NLP
 ├── Priority
 ├── Fraud Detection
 ├── Recommendation
 ├── Analytics
 └── Prediction
```

The diagram shows planned decision-support uses only. This data setup does not implement Computer Vision, RAG, OCR, fraud detection, or other AI models.

## Reproducing and checking the data

From the repository root:

```powershell
python scripts/data/generate_synthetic_data.py
python scripts/data/validate_data.py
```

Generation uses a fixed seed, so it produces the same data each time. The priority labels use documented rule-based synthetic scoring and are not model predictions.
