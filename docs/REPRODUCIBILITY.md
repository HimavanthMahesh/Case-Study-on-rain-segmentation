# Reproducibility Guide

## What is included

- Six cleaned notebooks preserving the experimental code and markdown
- Reusable inference scripts for SegFormer, Mask2Former, and OneFormer
- The MSeg image-level summary table
- Analysis figures and a small qualitative sample
- A manifest describing the completed segmentation runs

## What is excluded

- Cityscapes and other source datasets
- Conda environments and package caches
- Pretrained model weights
- Full generated rain, deraining, segmentation, and overlay outputs
- Copies of third-party repositories
- Cluster build logs and Jupyter checkpoint files

## Environment

The original work was performed on a Linux GPU environment with multiple task-specific Conda environments. The top-level `requirements.txt` is a practical starting point for the reusable segmentation scripts, not a lockfile for every upstream model.

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

GPU reproduction also requires a PyTorch build compatible with the local CUDA version. Follow the official PyTorch installation guidance for the target machine.

## Paths in the notebooks

The notebooks are a cleaned historical record. Original cluster paths were anonymized to `/path/to/project`; replace that placeholder with a project-specific data directory or refactor the cells to use a configuration variable before running them.

Recommended local layout:

```text
project-root/
├── external/       # cloned upstream repositories
├── data/           # source and generated datasets; ignored by Git
├── models/         # pretrained weights; ignored by Git
├── outputs/        # full experimental outputs; ignored by Git
├── notebooks/
├── scripts/
└── results/
```

## Suggested execution order

1. Obtain Cityscapes under its official terms and select the intended images.
2. Clone and configure the weather-particle simulator.
3. Generate the three variants for light, medium, and heavy rain.
4. Install each derainer from its original repository and obtain its pretrained weights.
5. Run each derainer over all rain variants.
6. Cache or install the four segmentors.
7. Run segmentation on clean, rainy, and derained images.
8. Compute image-level mIoU against the clean-image reference used by the study.
9. Aggregate results by segmentor, derainer, severity, and variant.
10. Generate the comparison figures.

## Reusable segmentation command

```bash
python scripts/run_cityscapes_segmentor.py \
  --model_type mask2former \
  --input_dir data/processed/example_condition \
  --output_dir outputs/masks/mask2former/example_condition
```

Set `HF_HOME` if the Hugging Face cache should live somewhere other than the default user cache:

```bash
export HF_HOME=/path/to/huggingface-cache
```

## Validation record

The cleaned repository intentionally strips notebook output while preserving code and markdown. JSON validity, absence of saved execution output, file-size limits, and searches for common credential filenames should be checked before every public release.
