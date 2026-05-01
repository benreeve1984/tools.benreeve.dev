# Benchmarks and Validation

Validation was run on Spark against the gated `pangram/editlens_iclr` test split. The validation script filters out examples shorter than 75 words, leaving 6,080 examples from the 6,115-row test split.

## Completed checks

1. Compared PyTorch FP32 predictions against ONNX FP32 predictions.
2. Compared ONNX INT8 predictions against the PyTorch baseline.
3. Reported binary and macro F1 deltas for INT8 versus PyTorch.
4. Loaded the published ONNX INT8 model from Hugging Face in Chromium through the static `/editlens/` page.
5. Verified paragraph-level scoring and the under-200-word refusal in that browser smoke test.
6. Checked the browser score calculation against Pangram's `scripts/inference.py` expected-value calculation.

## Remaining checks

1. Compare browser and upstream Python outputs on matched emoji-containing inputs.
2. Run real-model browser smoke tests in Firefox and Safari.
3. Verify the production Cloudflare Pages headers after DNS cutover.

## Acceptance target

The INT8 model should be within two binary F1 points of the PyTorch baseline before the demo claims parity.

The measured binary F1 delta is -0.0004, or -0.04 percentage points.

| Runtime | Accuracy | Binary F1 | Ternary or bucket F1 | Notes |
| --- | ---: | ---: | ---: | --- |
| PyTorch FP32 | 0.8280 | 0.9421 | 0.6124 | baseline |
| ONNX FP32 | 0.8280 | 0.9421 | 0.6124 | binary F1 delta +0.0000 |
| ONNX INT8 | 0.8265 | 0.9418 | 0.6148 | binary F1 delta -0.0004 |

Command:

```sh
BATCH_SIZE=64 python 05_validate.py
```

Runtime on Spark was 3,712.70 seconds.

## Browser smoke test

Chromium loaded `https://huggingface.co/benreeve/editlens-roberta-large-onnx-int8` from a local static server and completed a two-paragraph analysis.

- First ONNX download: 41 seconds for 342 MiB reported by the browser
- First model load plus first paragraph analysis: 47 seconds
- Two scored paragraphs: `score 0.382` and `score 0.304`
- Short-text refusal: `Text too short: 4 words. Minimum is 200 words because short text is unreliable.`

The headless browser reported that the large ONNX response could not be added to the browser Cache API in that temporary profile. The file is still served with long-lived HTTP cache headers, but repeated-load caching should be rechecked in normal Chrome after production deployment.
