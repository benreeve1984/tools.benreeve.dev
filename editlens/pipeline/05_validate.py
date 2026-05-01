"""Validate PyTorch, ONNX FP32, and ONNX INT8 parity on the EditLens test split."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch
from datasets import load_dataset
from scipy.special import softmax
from sklearn.metrics import accuracy_score, f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from common import (
    DATASET_ID,
    MERGED_DIR,
    ONNX_DIR,
    SCORE_COLUMN,
    WEB_REPO_DIR,
    ensure_hf_token,
    infer_n_buckets,
)

MAX_LENGTH = int(os.environ.get("MAX_LENGTH", "512"))
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "8"))
MAX_EVAL_SAMPLES = int(os.environ.get("MAX_EVAL_SAMPLES", "0"))
LO_THRESHOLD = float(os.environ.get("LO_THRESHOLD", "0.03"))
HI_THRESHOLD = float(os.environ.get("HI_THRESHOLD", "0.15"))


def count_words(text: str) -> int:
    return len(text.split())


def score_to_bucket(score: float, n_buckets: int) -> int:
    if n_buckets == 2:
        return 0 if score <= (LO_THRESHOLD + HI_THRESHOLD) / 2 else 1
    if score <= LO_THRESHOLD:
        return 0
    if score >= HI_THRESHOLD:
        return n_buckets - 1
    normalized = (score - LO_THRESHOLD) / (HI_THRESHOLD - LO_THRESHOLD)
    return 1 + int(normalized * (n_buckets - 2))


def scores_from_logits(logits: np.ndarray, n_buckets: int) -> tuple[np.ndarray, np.ndarray]:
    probs = softmax(logits, axis=1)
    buckets = np.arange(n_buckets)
    scores = (probs @ buckets) / (n_buckets - 1)
    preds = np.argmax(probs, axis=1)
    return scores, preds


def batched(items: list[str], size: int):
    for index in range(0, len(items), size):
        yield items[index : index + size]


def run_torch(texts: list[str], tokenizer, n_buckets: int) -> tuple[np.ndarray, np.ndarray]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForSequenceClassification.from_pretrained(MERGED_DIR)
    model.to(device)
    model.eval()
    logits = []
    with torch.no_grad():
        for batch in batched(texts, BATCH_SIZE):
            encoded = tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=MAX_LENGTH,
                return_tensors="pt",
            )
            encoded = {key: value.to(device) for key, value in encoded.items()}
            output = model(**encoded)
            logits.append(output.logits.cpu().numpy())
    return scores_from_logits(np.concatenate(logits, axis=0), n_buckets)


def run_onnx(model_path: Path, texts: list[str], tokenizer, n_buckets: int) -> tuple[np.ndarray, np.ndarray]:
    session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    input_names = {item.name for item in session.get_inputs()}
    logits = []
    for batch in batched(texts, BATCH_SIZE):
        encoded = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors="np",
        )
        ort_inputs = {name: value for name, value in encoded.items() if name in input_names}
        logits.append(session.run(None, ort_inputs)[0])
    return scores_from_logits(np.concatenate(logits, axis=0), n_buckets)


def report(name: str, y_true_bucket: np.ndarray, y_pred_bucket: np.ndarray, baseline_f1: float | None = None) -> float:
    y_true_binary = y_true_bucket > 0
    y_pred_binary = y_pred_bucket > 0
    acc = accuracy_score(y_true_bucket, y_pred_bucket)
    binary_f1 = f1_score(y_true_binary, y_pred_binary)
    macro_f1 = f1_score(y_true_bucket, y_pred_bucket, average="macro")
    suffix = ""
    if baseline_f1 is not None:
        suffix = f" delta_vs_torch={binary_f1 - baseline_f1:+.4f}"
    print(f"{name}: accuracy={acc:.4f} binary_f1={binary_f1:.4f} macro_f1={macro_f1:.4f}{suffix}")
    return binary_f1


def main() -> None:
    token = ensure_hf_token()
    n_buckets = infer_n_buckets(MERGED_DIR)
    tokenizer = AutoTokenizer.from_pretrained(MERGED_DIR)

    ds = load_dataset(DATASET_ID, split="test", token=token)
    ds = ds.filter(lambda row: row.get("text") is not None and row.get(SCORE_COLUMN) is not None)
    ds = ds.filter(lambda row: count_words(row["text"]) >= 75)
    if MAX_EVAL_SAMPLES > 0:
        ds = ds.select(range(min(MAX_EVAL_SAMPLES, len(ds))))

    texts = list(ds["text"])
    y_true_bucket = np.array([score_to_bucket(float(score), n_buckets) for score in ds[SCORE_COLUMN]])

    print(f"Validating {len(texts)} examples with n_buckets={n_buckets}")

    _, torch_bucket = run_torch(texts, tokenizer, n_buckets)
    torch_f1 = report("PyTorch FP32", y_true_bucket, torch_bucket)

    _, onnx_bucket = run_onnx(ONNX_DIR / "model.onnx", texts, tokenizer, n_buckets)
    report("ONNX FP32", y_true_bucket, onnx_bucket, torch_f1)

    int8_path = WEB_REPO_DIR / "onnx" / "model_quantized.onnx"
    _, int8_bucket = run_onnx(int8_path, texts, tokenizer, n_buckets)
    int8_f1 = report("ONNX INT8", y_true_bucket, int8_bucket, torch_f1)

    if torch_f1 - int8_f1 > 0.02:
        raise SystemExit("INT8 binary F1 dropped by more than 0.02 versus PyTorch.")


if __name__ == "__main__":
    main()
