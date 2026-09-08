# Case evidence placeholder

This directory is reserved for synthetic/demo or future user-uploaded evidence belonging to individual cases. Evidence can include images, supporting documents, descriptions, and structured case information.

Case evidence is separate from the external Computer Vision dataset under `data/external/disaster_images/` and from trusted RAG knowledge documents under `data/raw/documents/rag/`.

Do not place real personal documents here. Do not add real IDs, passports, medical records, bank statements, or similar sensitive material. Use synthetic/demo files only until an approved secure storage process exists.

AI-derived outputs are verification signals for human review. They must not claim to prove legal authenticity or make final eligibility decisions. Suspicious or inconsistent evidence must be escalated for human review.

## Synthetic demo coverage

The current demo set contains 40 evidence-bearing synthetic cases (`CASE-0001` through `CASE-0040`), 40 synthetic SVG image files, and 10 synthetic plain-text supporting documents. All 50 manifest records use `source_type=synthetic_demo` and `verification_status=unreviewed`.

Coverage summary:

| Measure | Count |
|---|---:|
| Cases with evidence | 40 |
| Image evidence files | 40 |
| Supporting document files | 10 |
| Total manifest records | 50 |
| `image` evidence records | 40 |
| `supporting_document` evidence records | 10 |
| `synthetic_demo` source records | 50 |
| Evidence records per case | 2 each for CASE-0001 through CASE-0010; 1 each for CASE-0011 through CASE-0040 |

The SVGs are original synthetic illustrations created for workflow testing. They were not copied from the external CV dataset and are not real user submissions. The text files are invented support notes, not IDs, passports, medical records, bank statements, or other private documents.