# Trusted humanitarian knowledge corpus

This directory contains a small set of authoritative humanitarian guidance documents acquired from official organization domains. These documents are intended for a future grounded knowledge workflow covering needs assessment, emergency response planning, prioritization, protection, and responsible humanitarian decision support.

The corpus is not case evidence, is not a set of training labels, and is not used to decide whether a beneficiary is legally eligible. It provides reference knowledge and guidance only. Any future AI output must remain a verification or decision-support signal with human review.

## Final selected corpus

- `ifrc_emergency_needs_assessment_and_planning_2025.pdf` is the verified IFRC guidance document listed in `metadata.csv`.

The corpus remains intentionally focused at one verified document. The attempted IFRC Emergency Response Framework candidate was not safely downloadable from a verified official file endpoint during this step, and WHO HESPER and UNHCR handbook candidates remain unresolved. They are recorded in `data/DATA_PROVENANCE.md` rather than being replaced with third-party copies or HTML files saved as PDFs.