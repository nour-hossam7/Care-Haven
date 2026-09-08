# External data

One external Computer Vision dataset has been integrated: the Kaggle Disaster Images Dataset. Its extracted files are stored in `disaster_images/`; the archive remains outside the repository in the user's Downloads folder.

## Planned External Computer Vision Dataset

CareHaven uses one small, practical external dataset for an academic graduation project. It supports evidence analysis for humanitarian cases rather than satellite-disaster mapping.

The selected dataset should preferably:

- contain images of damaged houses or buildings, fire damage, flood damage, infrastructure damage, disaster evidence, or relevant objects;
- be small enough to download, inspect, and use within the project scope;
- be available through an accessible public source such as Kaggle or another reputable provider;
- have an academic/project-compatible license; and
- include labels suitable for image classification or object detection where possible.

The Kaggle Disaster Images Dataset is the selected dataset. It has been integrated for inspection and manifesting only; no training, preprocessing, or conversion has been performed.

## Derived evaluation data

CareHaven does not need separate large datasets for image duplicates or image quality. Later, controlled evaluation examples can be derived from selected case-evidence or external-CV images:

- duplicate and near-duplicate examples: exact copies, resized copies, compressed copies, crops, and slight modifications;
- quality examples: good, blurred, dark, overexposed, and low-resolution variants.

These derived examples are evaluation aids. A similarity score or quality signal must flag cases for human review, not make an eligibility decision or accuse anyone of fraud.
