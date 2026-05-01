"""Prepare a self-contained EditLens checkpoint for ONNX export.

The initial project spec assumed Pangram released a PEFT adapter. The gated
`editlens_roberta-large` repo currently contains a full RoBERTa sequence
classification checkpoint. If a future release switches to PEFT, this script
still handles the merge path.
"""

import shutil
import torch
from peft import PeftModel
from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer

from common import ADAPTER_DIR, BASE_DIR, MERGED_DIR, infer_n_buckets, label_maps


def main() -> None:
    if not (ADAPTER_DIR / "adapter_config.json").exists():
        if MERGED_DIR.exists():
            shutil.rmtree(MERGED_DIR)
        shutil.copytree(ADAPTER_DIR, MERGED_DIR)
        n_buckets = infer_n_buckets(MERGED_DIR)
        print(f"Full checkpoint copied to {MERGED_DIR} with n_buckets={n_buckets}")
        return

    n_buckets = infer_n_buckets(ADAPTER_DIR)
    id2label, label2id = label_maps(n_buckets)
    print(f"Inferred n_buckets={n_buckets}")

    config = AutoConfig.from_pretrained(BASE_DIR)
    config.num_labels = n_buckets
    config.id2label = id2label
    config.label2id = label2id
    config.problem_type = "single_label_classification"

    tokenizer = AutoTokenizer.from_pretrained(BASE_DIR)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    base = AutoModelForSequenceClassification.from_pretrained(
        BASE_DIR,
        config=config,
        torch_dtype=torch.float32,
    )
    base.config.pad_token_id = tokenizer.pad_token_id

    peft_model = PeftModel.from_pretrained(base, ADAPTER_DIR)
    merged = peft_model.merge_and_unload()
    MERGED_DIR.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(MERGED_DIR, safe_serialization=True)
    tokenizer.save_pretrained(MERGED_DIR)

    print(f"Merged model saved to {MERGED_DIR}")


if __name__ == "__main__":
    main()
