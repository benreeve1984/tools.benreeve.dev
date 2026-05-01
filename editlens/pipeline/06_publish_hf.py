"""Publish the prepared Transformers.js model repo to Hugging Face."""

import os

from huggingface_hub import HfApi

from common import WEB_REPO_DIR, ensure_hf_token


def main() -> None:
    token = ensure_hf_token()
    repo_id = os.environ.get("HF_MODEL_REPO", "benreeve/editlens-roberta-large-onnx-int8")
    if not WEB_REPO_DIR.exists():
        raise SystemExit(f"Missing {WEB_REPO_DIR}. Run 04_quantize.py first.")

    api = HfApi(token=token)
    api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, private=False)
    api.upload_folder(
        repo_id=repo_id,
        repo_type="model",
        folder_path=str(WEB_REPO_DIR),
        commit_message="Add EditLens ONNX INT8 browser artifacts",
    )
    print(f"Published {WEB_REPO_DIR} to https://huggingface.co/{repo_id}")


if __name__ == "__main__":
    main()
