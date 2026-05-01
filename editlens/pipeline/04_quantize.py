"""Quantize ONNX to INT8 and prepare a Transformers.js-compatible model repo."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from onnxruntime.quantization import QuantType, quantize_dynamic

from common import ONNX_DIR, UPSTREAM_MODEL_ID, WEB_REPO_DIR


MODEL_CARD = f"""---
library_name: transformers.js
license: cc-by-nc-sa-4.0
base_model: {UPSTREAM_MODEL_ID}
tags:
- transformers.js
- onnx
- text-classification
- roberta
- ai-detection
---

# EditLens RoBERTa-large ONNX INT8

This repository contains derivative ONNX artifacts for Pangram's gated
`{UPSTREAM_MODEL_ID}` model, prepared for local browser inference with
Transformers.js.

The upstream model is licensed CC BY-NC-SA 4.0. These derivative artifacts
inherit that license and are for non-commercial research use.

Upstream model card: https://huggingface.co/{UPSTREAM_MODEL_ID}
Paper: https://arxiv.org/abs/2510.03154
Upstream code: https://github.com/pangramlabs/EditLens
"""


def copy_if_exists(src_dir: Path, dst_dir: Path, name: str) -> None:
    src = src_dir / name
    if src.exists():
        shutil.copy2(src, dst_dir / name)


def main() -> None:
    src_model = ONNX_DIR / "model.onnx"
    if not src_model.exists():
        raise SystemExit(f"Missing ONNX model: {src_model}. Run 03_export_onnx.py first.")

    if WEB_REPO_DIR.exists():
        shutil.rmtree(WEB_REPO_DIR)
    onnx_out = WEB_REPO_DIR / "onnx"
    onnx_out.mkdir(parents=True, exist_ok=True)

    quantized = onnx_out / "model_quantized.onnx"
    quantize_dynamic(
        model_input=str(src_model),
        model_output=str(quantized),
        weight_type=QuantType.QInt8,
        per_channel=True,
        reduce_range=False,
    )

    for name in [
        "config.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "vocab.json",
        "merges.txt",
    ]:
        copy_if_exists(ONNX_DIR, WEB_REPO_DIR, name)

    (WEB_REPO_DIR / "README.md").write_text(MODEL_CARD, encoding="utf-8")
    size_mb = os.path.getsize(quantized) / 1_000_000
    print(f"Prepared browser model repo at {WEB_REPO_DIR}")
    print(f"Quantized ONNX size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
