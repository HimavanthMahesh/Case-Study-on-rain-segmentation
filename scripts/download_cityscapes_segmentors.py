import os
from pathlib import Path

os.environ.setdefault("HF_HOME", str(Path.home() / ".cache" / "huggingface"))
Path(os.environ["HF_HOME"]).mkdir(parents=True, exist_ok=True)

from transformers import (
    AutoImageProcessor,
    SegformerForSemanticSegmentation,
    Mask2FormerForUniversalSegmentation,
    OneFormerProcessor,
    OneFormerForUniversalSegmentation,
)

models = [
    {
        "name": "SegFormer",
        "model_id": "nvidia/segformer-b5-finetuned-cityscapes-1024-1024",
        "processor_cls": AutoImageProcessor,
        "model_cls": SegformerForSemanticSegmentation,
    },
    {
        "name": "Mask2Former",
        "model_id": "facebook/mask2former-swin-large-cityscapes-semantic",
        "processor_cls": AutoImageProcessor,
        "model_cls": Mask2FormerForUniversalSegmentation,
    },
    {
        "name": "OneFormer",
        "model_id": "shi-labs/oneformer_cityscapes_swin_large",
        "processor_cls": OneFormerProcessor,
        "model_cls": OneFormerForUniversalSegmentation,
    },
]

for item in models:
    print("=" * 80)
    print(f"Downloading/checking {item['name']}: {item['model_id']}")

    processor = item["processor_cls"].from_pretrained(item["model_id"])
    model = item["model_cls"].from_pretrained(item["model_id"])

    print(f"{item['name']} OK")

print("=" * 80)
print("All three segmentors downloaded/cached.")
print("HF cache:", os.environ["HF_HOME"])
