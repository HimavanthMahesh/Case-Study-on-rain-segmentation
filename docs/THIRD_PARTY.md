# Third-Party Projects and Data

This independent study builds on the following external research projects. Their code, model weights, datasets, names, and papers remain subject to their original licenses and terms. Complete copies of these repositories were removed from the cleaned project to avoid obscuring authorship and duplicating upstream source code.

## Weather simulation

- [Weather Particle Simulator](https://github.com/cv-rits/weather-particle-simulator), associated with *A Physics-Based Rendering for Realistic Rain and Fog* ([arXiv:2009.03683](https://arxiv.org/abs/2009.03683))

## Deraining models

- [DRSformer](https://github.com/cschenxiang/DRSformer), associated with *Learning a Sparse Transformer Network for Effective Image Deraining*
- [IDT](https://github.com/jiexiaou/IDT), the official implementation of *Image De-raining Transformer*
- [NeRD-Rain](https://github.com/cschenxiang/NeRD-Rain), the official implementation of *Bidirectional Multi-Scale Implicit Neural Representations for Image Deraining*
- [Restormer](https://github.com/swz30/Restormer), associated with *Restormer: Efficient Transformer for High-Resolution Image Restoration* ([arXiv:2111.09881](https://arxiv.org/abs/2111.09881))
- [UDR-S2Former](https://github.com/Ephemeral182/UDR-S2Former_deraining), the official implementation of *Sparse Sampling Transformer with Uncertainty-Driven Ranking for Unified Removal of Raindrops and Rain Streaks*

The exact upstream URL for an archived local copy should be verified against the model paper before attempting a fully pinned reproduction. This document avoids claiming that an ambiguous local folder is an authoritative upstream source.

## Semantic segmentation

- [MSeg API](https://github.com/mseg-dataset/mseg-api)
- [MSeg Semantic](https://github.com/mseg-dataset/mseg-semantic)
- [SegFormer B5 Cityscapes model](https://huggingface.co/nvidia/segformer-b5-finetuned-cityscapes-1024-1024)
- [Mask2Former Swin-L Cityscapes semantic model](https://huggingface.co/facebook/mask2former-swin-large-cityscapes-semantic)
- [OneFormer Swin-L Cityscapes model](https://huggingface.co/shi-labs/oneformer_cityscapes_swin_large)

## Dataset

- [Cityscapes](https://www.cityscapes-dataset.com/)

Cityscapes source images are not included in this repository. Users must obtain and use the dataset under its official terms.

## License boundary

The repository's top-level MIT License covers only original project code and documentation. It does not relicense external code, pretrained weights, datasets, papers, or model artifacts.
