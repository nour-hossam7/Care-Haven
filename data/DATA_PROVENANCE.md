# CareHaven data provenance

This file records external sources and the intended boundary of each raw data source. No license is inferred where the source terms were not verified.

## Downloaded official knowledge document

| Dataset/document name | Source organization | Source website/domain | Download date | License/usage information | Intended use | Personal data | Data role |
|---|---|---|---|---|---|---|---|
| IFRC Emergency Needs Assessment and Planning Guidance | International Federation of Red Cross and Red Crescent Societies (IFRC) | `ifrc.org` | 2026-09-09 | License/usage terms require verification. IFRC source page and website terms are authoritative. | Focused humanitarian needs assessment and emergency planning reference | Not intended as personal data; document content must still be handled under source terms | Knowledge data |

Official source page: https://www.ifrc.org/document/emergency-needs-assessment-and-planning-guidance
Official file: https://www.ifrc.org/sites/default/files/2025-11/IFRC_Emergency_Needs%20Assessment_and_Planning.pdf

## Existing external image dataset

| Dataset/document name | Source organization | Source website/domain | Download date | License/usage information | Intended use | Personal data | Data role |
|---|---|---|---|---|---|---|---|
| Disaster Images Dataset, extracted as `data/external/disaster_images/` | Kaggle source attribution in repository documentation; original publisher/license details not captured | `kaggle.com` | Existing before this task; exact date unknown | License/usage terms require verification. | Future disaster-image inspection and research signals | May depict people or property; no case identity linkage is present in this project | External CV data |

The image files are intentionally not committed to Git. Lightweight metadata and corruption records are tracked separately.

## Official candidates not downloaded

| Dataset/document name | Source organization | Source website/domain | Download date | License/usage information | Intended use | Personal data | Data role |
|---|---|---|---|---|---|---|---|
| The HESPER Manual: Version 1.0: Rapid Assessment of Local Environmental Health Needs in Emergencies | WHO | `who.int`, `iris.who.int` | Not downloaded | License/usage terms require verification. | Emergency needs assessment reference | Unknown; not acquired | Candidate knowledge data |
| UNHCR Emergency Handbook | UNHCR | `emergency.unhcr.org` | Not downloaded | License/usage terms require verification. | Protection and responsible emergency response reference | Unknown; not acquired | Candidate knowledge data |
| IFRC Emergency Response Framework | IFRC | `ifrc.org` | Not downloaded | License/usage terms require verification. | Emergency response planning reference | Unknown; not acquired | Candidate knowledge data |

The WHO, UNHCR, and IFRC candidate pages or names were identifiable, but a verifiable official downloadable file was not available for safe acquisition in this environment. No substitute, guessed URL, third-party copy, or HTML file saved as PDF was added.

## Internal synthetic and placeholder sources

`data/raw/cases/cases.csv`, `data/raw/donors/donors.csv`, and `data/raw/donations/donations.csv` are locally generated synthetic operational data. The 40 synthetic case evidence images and 10 synthetic case-support notes under `data/raw/images/synthetic/` and `data/raw/documents/case_evidence/` were created locally for demo workflow testing; they are not real user submissions and contain no real personal data.