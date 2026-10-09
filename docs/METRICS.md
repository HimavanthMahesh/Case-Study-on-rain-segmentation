# Metric Definitions and Artifact Provenance

The study recorded more than one mask-agreement analysis. All use mean intersection over union (mIoU), but **the reference masks differ**. A number from one analysis cannot be described as a result from another.

| Analysis | Masks compared | Committed artifact | Supports | Does not support |
|---|---|---|---|---|
| Rain-instance agreement | For one source frame, derainer, and severity: predictions from rain variants `v1`, `v2`, and `v3` are compared pairwise | [`mseg_rain_instance_miou_summary.csv`](../results/tables/mseg_rain_instance_miou_summary.csv) and [`mseg_rain_instance_boxplots`](../results/figures/mseg_rain_instance_boxplots) | Descriptive stability across synthetic rain realizations for MSeg | Clean-image agreement, raw-rain improvement, or ground-truth accuracy |
| Clean-reference agreement | A rainy or derained prediction is compared with the **same segmentor's** prediction on the corresponding clean source image | [`all4_segmentors_by_derainer`](../results/figures/all4_segmentors_by_derainer) plots; the original analysis notebook also displayed aggregates | Descriptive change from clean-image model behavior | Ground-truth accuracy; the rain-instance CSV is not its data table |
| Ground-truth segmentation accuracy | Prediction compared with Cityscapes annotation masks | Not present as a final study table here | Would assess accuracy if computed with verified label mapping and splits | No such result can currently be claimed |

## How the MSeg CSV was made

For each source image and fixed derainer/severity, the analysis notebook calculates three pairwise mask mIoUs: `v1` versus `v2`, `v1` versus `v3`, and `v2` versus `v3`. It assigns each variant the mean of its two comparisons. The committed CSV then groups those image-level scores by segmentor, derainer, severity, and version, recording `n`, mean, median, standard deviation, minimum, and maximum. The table has 45 groups (five derainers × three severities × three variants), each with `n = 50` source images. The overall values in the README average the nine equally sized group means per derainer.

This calculation is visible in the source cells of [`04_evaluation_and_analysis.ipynb`](../notebooks/04_evaluation_and_analysis.ipynb). The MSeg CSV is **not** produced by comparing to clean masks, despite earlier descriptions in this repository that said so.

## Limits that matter in a résumé or presentation

- The sample is 50 Aachen Cityscapes source frames. The 2,250 figure describes 50 frames × nine rain conditions × five derainers: **processed image variants**, not independent scenes.
- Similarity to a clean-image **prediction** is not the same as accuracy against a clean-image **annotation**. A clean prediction can itself be wrong.
- The rain-instance table contains no direct raw-rain baseline. It cannot prove that deraining improves segmentation over processing rainy images without restoration.
- The historical [`segmentation_outputs_manifest.csv`](../results/tables/segmentation_outputs_manifest.csv) records zero MSeg masks in its then-expected paths. The later notebook and MSeg analysis use separate output locations. Preserve that provenance instead of silently treating the manifest as a complete final inventory.
- The current data supports descriptive differences in this sample, not statistical significance or generalization to other cities or real rain.

Before making an improvement claim, publish a matched per-image table for clean, raw-rain, and derained predictions against the same ground-truth labels, then report paired uncertainty across independent source frames.
