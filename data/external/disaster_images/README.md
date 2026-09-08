# Disaster Images Dataset

## Source and purpose

This external Computer Vision classification dataset was downloaded from the Kaggle **Disaster Images Dataset** source. Its original extracted top-level folder is `Comprehensive Disaster Dataset(CDD)` and has been preserved unchanged.

CareHaven may later use this dataset for humanitarian evidence-image analysis, including visible damage, disaster-relevance, and object/context signals. It is not being used for model training in this repository at this stage.

## Dataset contents

The extracted dataset is approximately 659 MB and contains 13,557 PNG image files in these original top-level classes:

- `Damaged_Infrastructure` — 1,454 images
- `Fire_Disaster` — 933 images
- `Human_Damage` — 241 image files (240 readable; one recorded separately)
- `Land_Disaster` — 657 images
- `Non_Damage` — 9,237 images
- `Water_Disaster` — 1,035 images

`metadata.csv` contains one row for each readable image with its path relative to this dataset directory, class, extension, width, and height. `corrupted_images.csv` records the one unreadable image without deleting or changing it.

## CareHaven data boundaries

This dataset is an external CV classification dataset only.

- It is **not** a CareHaven case dataset.
- It is **not** RAG knowledge data.
- It is **not** supporting evidence submitted by CareHaven users.
- It must remain separate from `data/raw/cases/`, `data/raw/images/`, and `data/raw/documents/`.
- Any future model output is a decision-support or verification signal for human review. It must not make final aid-eligibility decisions or automatic fraud accusations.

## Git handling

The extracted image directory is ignored by Git because it is large. This README, `metadata.csv`, and `corrupted_images.csv` are explicitly retained for tracking.
