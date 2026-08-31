import argparse
import os
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from tqdm import tqdm
from transformers import (
    AutoImageProcessor,
    SegformerForSemanticSegmentation,
    Mask2FormerForUniversalSegmentation,
    OneFormerProcessor,
    OneFormerForUniversalSegmentation,
)


os.environ.setdefault("HF_HOME", str(Path.home() / ".cache" / "huggingface"))


MODEL_CONFIGS = {
    "segformer": {
        "model_id": "nvidia/segformer-b5-finetuned-cityscapes-1024-1024",
        "processor_cls": AutoImageProcessor,
        "model_cls": SegformerForSemanticSegmentation,
    },
    "mask2former": {
        "model_id": "facebook/mask2former-swin-large-cityscapes-semantic",
        "processor_cls": AutoImageProcessor,
        "model_cls": Mask2FormerForUniversalSegmentation,
    },
    "oneformer": {
        "model_id": "shi-labs/oneformer_cityscapes_swin_large",
        "processor_cls": OneFormerProcessor,
        "model_cls": OneFormerForUniversalSegmentation,
    },
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_type", required=True, choices=list(MODEL_CONFIGS.keys()))
    parser.add_argument("--input_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    return parser.parse_args()


def list_images(input_dir):
    exts = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
    input_dir = Path(input_dir)
    return sorted([p for p in input_dir.iterdir() if p.suffix.lower() in exts])


def main():
    args = parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cfg = MODEL_CONFIGS[args.model_type]
    model_id = cfg["model_id"]

    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("=" * 80)
    print("Model type:", args.model_type)
    print("Model ID:", model_id)
    print("Input dir:", input_dir)
    print("Output dir:", output_dir)
    print("Device:", device)

    processor = cfg["processor_cls"].from_pretrained(model_id)
    model = cfg["model_cls"].from_pretrained(model_id)
    model.to(device)
    model.eval()

    image_paths = list_images(input_dir)
    print("Found images:", len(image_paths))

    for img_path in tqdm(image_paths):
        image = Image.open(img_path).convert("RGB")
        width, height = image.size

        if args.model_type == "oneformer":
            inputs = processor(
                images=image,
                task_inputs=["semantic"],
                return_tensors="pt",
            )
        else:
            inputs = processor(images=image, return_tensors="pt")

        inputs = {k: v.to(device) if hasattr(v, "to") else v for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)

        if args.model_type == "segformer":
            logits = outputs.logits
            upsampled_logits = torch.nn.functional.interpolate(
                logits,
                size=(height, width),
                mode="bilinear",
                align_corners=False,
            )
            pred = upsampled_logits.argmax(dim=1)[0].cpu().numpy().astype(np.uint8)

        else:
            semantic_maps = processor.post_process_semantic_segmentation(
                outputs,
                target_sizes=[(height, width)],
            )
            pred = semantic_maps[0].cpu().numpy().astype(np.uint8)

        out_path = output_dir / f"{img_path.stem}.png"
        Image.fromarray(pred).save(out_path)

    print("Done.")
    print("Saved masks to:", output_dir)


if __name__ == "__main__":
    main()
