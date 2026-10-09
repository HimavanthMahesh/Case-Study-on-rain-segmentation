# Results and Interpretation

## Two different recorded metrics

The **MSeg CSV and rain-instance boxplots** compare segmentation predictions across three independently rendered rain variants of the same source image, severity, and derainer. For each variant, the recorded score averages its pairwise mask mIoU with the other two variants. This is *rain-instance agreement*.

The **four-segmentor per-derainer figures** instead compare predictions on derained images with each segmentor's prediction on the corresponding clean image. This is *clean-reference agreement*. The archive preserves the plots and the notebook's displayed aggregate table, but the cleaned repository does not contain a machine-readable summary table for this second metric.

Neither metric is semantic-segmentation accuracy against Cityscapes ground-truth labels. They cannot be substituted for each other. In particular, the CSV below must not be described as mIoU against clean-image predictions. See [metric definitions and provenance](METRICS.md).

## MSeg rain-instance agreement summary

The recorded MSeg table contains 50 image-level measurements for each derainer, severity, and rain realization. The following values average the three rain realizations within each condition:

| Derainer | Light | Medium | Heavy | Overall |
|---|---:|---:|---:|---:|
| DRSformer | 0.753 | 0.688 | 0.626 | 0.689 |
| IDT | 0.844 | 0.763 | 0.685 | 0.764 |
| NeRD-Rain | 0.783 | 0.769 | 0.724 | 0.759 |
| Restormer | 0.758 | 0.718 | 0.673 | 0.716 |
| UDR-S2Former | 0.798 | 0.742 | 0.689 | 0.743 |

The table can be regenerated from the committed CSV with:

```bash
python scripts/summarize_mseg_results.py
```

## Main observations

### Rain severity is the strongest consistent effect

In the MSeg rain-instance table, agreement across the three rain realizations generally falls from light to medium to heavy rain across the five derainers. The separate clean-reference figures show severity-dependent differences for all four segmentors, but the CSV table above does not quantify those figures.

### Rain realization has a smaller effect

Within a fixed derainer and severity, the distributions for versions `v1`, `v2`, and `v3` are usually similar. Individual outliers occur, but the condition means and medians are comparatively stable. This is a descriptive observation about the recorded 50-frame sample, not a statistical significance result.

### No derainer dominates every condition

IDT has the highest overall MSeg **rain-instance agreement** mean and the strongest light-rain mean. NeRD-Rain is strongest on that metric under medium and heavy rain. The table does not establish which model gives the best clean-reference agreement, ground-truth accuracy, or improvement over raw rainy images.

These are downstream consistency results, not general-purpose deraining benchmark rankings. A restoration model optimized for perceptual or reconstruction quality may not preserve exactly the features used by a segmentation network.

### Segmentor choice changes the outcome

The four-segmentor **clean-reference** figures show different levels of sensitivity for MSeg, SegFormer, Mask2Former, and OneFormer. This supports evaluating restoration and perception as a coupled pipeline rather than selecting a derainer solely from image-quality metrics. These figures are a separate analysis from the CSV table above.

## What can be concluded

The current evidence supports the following conclusion:

> On the recorded 50-frame synthetic-rain sample, MSeg predictions become less consistent across independently rendered rain variants as severity rises. The extent of that variation differs by derainer. Separate clean-reference plots show that the choice of segmentor also matters, but the available CSV does not quantify a gain from deraining over direct rainy-image segmentation.

## What remains unresolved

The current package does not provide enough final aggregate data to establish:

- whether any derainer outperforms direct segmentation on the unprocessed rainy image for the same frames and segmentor;
- whether higher agreement with clean predictions corresponds to higher accuracy against ground-truth labels;
- whether the differences between derainers are statistically significant;
- whether the ranking generalizes beyond 50 Aachen images;
- whether the same behavior occurs under real rain rather than synthetic rendering.

## Highest-value follow-up experiments

1. Evaluate clean, rainy, and derained predictions against Cityscapes ground truth.
2. Report the direct rainy-image baseline beside every derainer.
3. Use paired bootstrap confidence intervals or paired significance tests across images.
4. Expand to additional Cityscapes locations and sequences.
5. Add real-rain or physically distinct corruption datasets.
6. Compare downstream segmentation consistency with restoration metrics such as PSNR, SSIM, and perceptual quality to test whether they correlate.
