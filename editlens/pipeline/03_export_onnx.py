"""Export the merged EditLens model to ONNX."""

from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer

from common import MERGED_DIR, ONNX_DIR


def main() -> None:
    ONNX_DIR.mkdir(parents=True, exist_ok=True)
    model = ORTModelForSequenceClassification.from_pretrained(MERGED_DIR, export=True)
    tokenizer = AutoTokenizer.from_pretrained(MERGED_DIR)
    model.save_pretrained(ONNX_DIR)
    tokenizer.save_pretrained(ONNX_DIR)
    print(f"ONNX export saved to {ONNX_DIR}")


if __name__ == "__main__":
    main()
