# Methodology

## Objective

The study examines whether image deraining improves semantic segmentation on urban scenes degraded by synthetic rain. It also compares sensitivity to rain severity and random rain realization.

## Data

The recorded experiment uses 50 images from the Aachen sequence of Cityscapes. The public repository excludes the source images because Cityscapes has its own access and licensing terms.

## Weather generation

Synthetic rain is organized into three nominal severity levels:

| Severity | Recorded rain-rate label | Variants |
|---|---:|---:|
| Light | 25 mm | 3 |
| Medium | 75 mm | 3 |
| Heavy | 140 mm | 3 |

The notebooks use the weather-particle simulator derived from *A Physics-Based Rendering for Realistic Rain and Fog* to generate the degraded scenes. Each severity has three variants so that conclusions are not based on one random rain realization.

## Restoration models

Five image-deraining approaches were evaluated:

- DRSformer
- IDT
- NeRD-Rain
- Restormer
- UDR-S2Former

Pretrained weights and copied upstream repositories are not included in this cleaned repository. The original sources are listed in `THIRD_PARTY.md`.

## Segmentation models

The experimental notebooks reference four semantic-segmentation systems:

- MSeg
- SegFormer B5 fine-tuned on Cityscapes
- Mask2Former with a Swin-L backbone fine-tuned on Cityscapes semantic segmentation
- OneFormer with a Swin-L backbone trained for Cityscapes

The reusable inference script supports the three Hugging Face models. MSeg follows its upstream installation and inference process.

## Evaluation

The supplied MSeg CSV records **rain-instance agreement**: pairwise mask mIoU across the three independently rendered rain variants for the same source frame, derainer, and severity. For each variant, the score is the mean of its two pairwise agreements with the other variants. For each derainer-severity-variant combination:

- `n = 50` image-level measurements
- mean, median, standard deviation, minimum, and maximum are reported
- distributions are visualized with boxplots

Additional figures compare each of the four segmentors against clean-image behavior for each derainer. Those figures use a **different metric**, clean-reference agreement. The repository contains those figures, but the archive did not include a machine-readable aggregate table for all four segmentors. Accordingly, numerical claims in the main README are limited to the supplied MSeg rain-instance table. See [metric definitions and provenance](METRICS.md).

The `segmentation_outputs_manifest.csv` was generated before the MSeg outputs were normalized into the later analysis locations. It reports zero masks for MSeg under its earlier expected paths, while the separate MSeg analysis CSV and sample masks show that MSeg predictions were subsequently analyzed. Do not interpret the manifest's MSeg zeroes as a final result or silently change them without regenerating the manifest from the definitive paths.

## Interpretation limits

- The sample contains 50 images from one Cityscapes sequence and is not a full-dataset benchmark.
- Results depend on the selected pretrained weights and preprocessing implementations.
- Synthetic rain does not cover all real-world weather effects.
- mIoU values in the supplied table measure agreement across synthetic rain realizations, not accuracy or agreement with clean predictions; they should not be treated as universal model rankings.
- Full reproducibility requires upstream code versions, model weights, and source data that are not redistributed here.
