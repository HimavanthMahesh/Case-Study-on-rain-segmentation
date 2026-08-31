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

The primary recorded metric is mIoU. For each derainer-severity-variant combination in the supplied MSeg summary:

- `n = 50` image-level measurements
- mean, median, standard deviation, minimum, and maximum are reported
- distributions are visualized with boxplots

Additional figures compare each of the four segmentors against clean-image behavior for each derainer. The repository contains those figures, but the archive did not include the complete underlying aggregate tables for all four segmentors. Accordingly, numerical claims in the main README are limited to the supplied MSeg summary table.

## Interpretation limits

- The sample contains 50 images from one Cityscapes sequence and is not a full-dataset benchmark.
- Results depend on the selected pretrained weights and preprocessing implementations.
- Synthetic rain does not cover all real-world weather effects.
- mIoU values in the supplied table characterize the recorded pipeline and should not be treated as universal model rankings.
- Full reproducibility requires upstream code versions, model weights, and source data that are not redistributed here.
