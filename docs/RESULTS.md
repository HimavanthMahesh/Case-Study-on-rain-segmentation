# Results and Interpretation

## What the recorded metric represents

The final figures compare predictions on rainy or derained images with each segmentor's prediction on the corresponding clean image. The mIoU values therefore measure prediction consistency under image degradation and restoration.

This is not the same as semantic-segmentation accuracy against Cityscapes ground-truth labels. Clean predictions can contain errors, and a changed prediction is not automatically a less accurate prediction. The current results support claims about robustness and consistency, not definitive claims about ground-truth accuracy.

## MSeg summary

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

Agreement with clean predictions generally falls from light to medium to heavy rain. This pattern appears across derainers and segmentors, indicating that the result is not limited to one model combination.

### Rain realization has a smaller effect

Within a fixed derainer and severity, the distributions for versions `v1`, `v2`, and `v3` are usually similar. Individual outliers occur, but the condition means and medians are comparatively stable. In this sample, rain severity appears more influential than the particular random rendering.

### No derainer dominates every condition

IDT has the highest overall MSeg mean and the strongest light-rain mean. NeRD-Rain is strongest for MSeg under medium and heavy rain. UDR-S2Former remains competitive across severities, while Restormer and DRSformer retain less clean-prediction agreement in this recorded MSeg evaluation.

These are downstream consistency results, not general-purpose deraining benchmark rankings. A restoration model optimized for perceptual or reconstruction quality may not preserve exactly the features used by a segmentation network.

### Segmentor choice changes the outcome

The four-segmentor figures show different levels of sensitivity for MSeg, SegFormer, Mask2Former, and OneFormer. This supports evaluating restoration and perception as a coupled pipeline rather than selecting a derainer solely from image-quality metrics.

## What can be concluded

The current evidence supports the following conclusion:

> Synthetic rain progressively changes semantic-segmentation predictions, and image restoration preserves clean-image behavior to different degrees depending on rain severity, derainer, and downstream segmentor. The similarity across rain realizations suggests that the main trends are systematic within the recorded sample.

## What remains unresolved

The current package does not provide enough final aggregate data to establish:

- whether every derainer outperforms direct segmentation on the unprocessed rainy image;
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
