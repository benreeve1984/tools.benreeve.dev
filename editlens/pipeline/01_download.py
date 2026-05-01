"""Download the gated EditLens checkpoint and, if needed, RoBERTa base model."""

from huggingface_hub import snapshot_download

from common import ADAPTER_DIR, BASE_DIR, BASE_MODEL_ID, UPSTREAM_MODEL_ID, ensure_hf_token


def main() -> None:
    token = ensure_hf_token()
    ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    snapshot_download(
        repo_id=UPSTREAM_MODEL_ID,
        local_dir=ADAPTER_DIR,
        token=token,
        allow_patterns=[
            ".gitattributes",
            "README.md",
            "config.json",
            "model.safetensors",
            "tokenizer.json",
            "tokenizer_config.json",
            "special_tokens_map.json",
            "vocab.json",
            "merges.txt",
            "adapter_config.json",
            "adapter_model.safetensors",
            "adapter_model.bin",
        ],
    )
    if (ADAPTER_DIR / "adapter_config.json").exists():
        snapshot_download(
            repo_id=BASE_MODEL_ID,
            local_dir=BASE_DIR,
            allow_patterns=[
                ".gitattributes",
                "README.md",
                "config.json",
                "model.safetensors",
                "pytorch_model.bin",
                "tokenizer.json",
                "tokenizer_config.json",
                "special_tokens_map.json",
                "vocab.json",
                "merges.txt",
            ],
        )
        print(f"Downloaded {BASE_MODEL_ID} to {BASE_DIR}")
    else:
        print("Upstream checkpoint is a full model; base model download is not needed.")
    print(f"Downloaded {UPSTREAM_MODEL_ID} to {ADAPTER_DIR}")


if __name__ == "__main__":
    main()
