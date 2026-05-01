from __future__ import annotations

import os
from pathlib import Path

import torch
from safetensors import safe_open
from transformers import AutoConfig


BASE_MODEL_ID = os.environ.get("BASE_MODEL_ID", "FacebookAI/roberta-large")
UPSTREAM_MODEL_ID = os.environ.get("UPSTREAM_MODEL_ID", "pangram/editlens_roberta-large")
DATASET_ID = os.environ.get("DATASET_ID", "pangram/editlens_iclr")
SCORE_COLUMN = os.environ.get("SCORE_COLUMN", "cosine_score")

ARTIFACTS = Path("artifacts")
DOWNLOAD_DIR = ARTIFACTS / "01_download"
BASE_DIR = DOWNLOAD_DIR / "base"
ADAPTER_DIR = DOWNLOAD_DIR / "adapter"
MERGED_DIR = ARTIFACTS / "02_merged"
ONNX_DIR = ARTIFACTS / "03_onnx"
WEB_REPO_DIR = ARTIFACTS / "04_web_repo"


def ensure_hf_token() -> str:
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit(
            "HF_TOKEN is required. Use a Hugging Face token whose account has "
            "accepted the Pangram model gate."
        )
    return token


def infer_n_buckets(checkpoint: str | Path) -> int:
    override = os.environ.get("N_BUCKETS")
    if override:
        return int(override)

    checkpoint = Path(checkpoint)
    config_path = checkpoint / "config.json"
    if config_path.exists():
        try:
            return int(AutoConfig.from_pretrained(checkpoint).num_labels)
        except Exception:
            pass

    candidates: list[Path] = list(checkpoint.glob("*.safetensors"))
    for path in candidates:
        with safe_open(path, framework="pt") as handle:
            for key in handle.keys():
                lowered = key.lower()
                if not any(name in lowered for name in ("classifier", "score", "out_proj")):
                    continue
                tensor = handle.get_tensor(key)
                if tensor.ndim == 2 and 1 < tensor.shape[0] <= 64:
                    return int(tensor.shape[0])

    bin_path = checkpoint / "adapter_model.bin"
    if bin_path.exists():
        state_dict = torch.load(bin_path, map_location="cpu", weights_only=True)
        for key, tensor in state_dict.items():
            lowered = key.lower()
            if not any(name in lowered for name in ("classifier", "score", "out_proj")):
                continue
            if tensor.ndim == 2 and 1 < tensor.shape[0] <= 64:
                return int(tensor.shape[0])

    print(
        f"Could not infer bucket count from {checkpoint}; defaulting to 4, "
        "which matches Pangram's published RoBERTa config. Set N_BUCKETS to override."
    )
    return 4


def label_maps(n_buckets: int) -> tuple[dict[int, str], dict[str, int]]:
    id2label = {index: f"bucket_{index}" for index in range(n_buckets)}
    label2id = {label: index for index, label in id2label.items()}
    return id2label, label2id
