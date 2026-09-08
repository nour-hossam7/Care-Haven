# CareHaven data dictionary

The current structured records are synthetic. Monetary values are stored as decimal numbers in CSV (two decimal places); dates use ISO 8601 `YYYY-MM-DD` format. An external Computer Vision classification dataset is present separately under `external/disaster_images/`. Case evidence remains a schema-only placeholder, while one verified IFRC humanitarian guidance document is present under `raw/documents/rag/`.

## Cases (`raw/cases/cases.csv`)

| Field | Type | Description | Allowed values | Example |
|---|---|---|---|---|
| `case_id` | string | Unique case identifier. | `CASE-` followed by four digits | `CASE-0001` |
| `description` | string | Synthetic humanitarian-assistance narrative. | Non-empty text | `A 6-person family needs temporary shelter after a house fire made their home unsafe.` |
| `assistance_category` | categorical string | Primary support type. | Food, Medical Aid, Emergency Housing, Water, Clothing, Education | `Food` |
| `people_affected` | integer | Number of people affected. | Positive integer | `18` |
| `country` | string | Country of the generated location. | Current generated locations | `Egypt` |
| `governorate` | string | Governorate or comparable regional area. | Current generated locations | `Cairo` |
| `city` | string | City of the generated location. | Current generated locations | `Cairo` |
| `latitude` | decimal | Generated latitude near the case city. | -90 to 90 | `30.046181` |
| `longitude` | decimal | Generated longitude near the case city. | -180 to 180 | `31.223541` |
| `severity` | categorical string | Impact seriousness. | Low, Medium, High, Critical | `High` |
| `urgency` | categorical string | Required response speed. | Low, Medium, High, Critical | `Critical` |
| `required_resources` | string | Semicolon-separated requested resources. | Non-empty text | `food parcels; cooking staples; infant nutrition` |
| `estimated_funding` | decimal | Total estimated funding needed. | Greater than 0 | `10500.00` |
| `current_funding` | decimal | Sum of donations currently received. | 0 through `estimated_funding` | `2300.00` |
| `submission_date` | date | Date the case was submitted. | ISO date | `2026-03-12` |
| `status` | categorical string | Operational/funding state. | Active, Under Review, Funded, Completed | `Active` |
| `priority` | categorical string | Rule-generated synthetic priority label. | Low, Medium, High, Critical | `High` |

### Synthetic priority rule

The generator adds numeric bands for severity, urgency, people affected, and funding-gap ratio, plus one point for Medical Aid or Emergency Housing. Scores of 13 or more are `Critical`, 10–12 are `High`, 7–9 are `Medium`, and lower scores are `Low`. This is a transparent label-generation rule for future experimentation, not an ML model.

## Donors (`raw/donors/donors.csv`)

| Field | Type | Description | Allowed values | Example |
|---|---|---|---|---|
| `donor_id` | string | Unique anonymous synthetic donor identifier. | `DONOR-` followed by three digits | `DONOR-001` |
| `preferred_category` | categorical string | Preferred assistance category. | Food, Medical Aid, Emergency Housing, Water, Clothing, Education | `Medical Aid` |
| `budget` | decimal | Synthetic available donation budget. | Greater than 0 | `25000.00` |
| `preferred_location` | string | Preferred country and governorate. | Current generated locations | `Egypt - Cairo` |
| `urgency_preference` | categorical string | Preferred case urgency. | Low, Medium, High, Critical | `High` |
| `previous_donations` | integer | Synthetic count of donations made before this dataset. | Integer ≥ 0 | `8` |

## Donations (`raw/donations/donations.csv`)

| Field | Type | Description | Allowed values | Example |
|---|---|---|---|---|
| `donation_id` | string | Unique donation identifier. | `DONATION-` followed by four digits | `DONATION-0001` |
| `donor_id` | string | Donor foreign key. | Existing value in donors data | `DONOR-001` |
| `case_id` | string | Case foreign key. | Existing value in cases data | `CASE-0001` |
| `amount` | decimal | Donation amount. | Greater than 0 | `420.50` |
| `date` | date | Donation date. | ISO date on/after the case submission date | `2026-05-16` |

## Non-tabular case data

The following folders define the case-data architecture. Current evidence files are synthetic demos only; future user uploads require an approved secure process.

| Area | Location | Purpose | Important boundary |
|---|---|---|---|
| Case evidence images | `raw/images/` | Synthetic demo images and future approved case uploads. | Image signals support human review only. |
| Case supporting documents | `raw/documents/case_evidence/` | Synthetic demo notes and future approved case-linked documents. | These are not a RAG knowledge base and do not establish legal authenticity automatically. |
| RAG knowledge documents | `raw/documents/rag/` | Trusted guidelines, policies, official reports, and humanitarian reference material. | Kept separate from case evidence. |
| External CV dataset | `external/disaster_images/` | Kaggle Disaster Images Dataset for future evidence-image analysis. | External classification data only; not case data, RAG data, or user-submitted evidence. |

Duplicate/near-duplicate and image-quality evaluation examples may later be derived from selected evidence images using controlled variants. Fraud or anomaly signals should combine multiple sources and route to human review rather than make automatic accusations or eligibility decisions.
