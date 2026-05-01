# EditLens in the Browser

A local-first browser reproduction of Pangram's `editlens_roberta-large` model. The user pastes text into the page; the page downloads static ONNX model files and runs paragraph-level scoring in the browser with Transformers.js. Pasted text is not sent to an API.

This is a research reproduction, not a product for enforcing AI-use policies.

## Current status

- Browser UI: archived at `index.draft.html.txt`, not currently published
- Model loader: configured for `benreeve/editlens-roberta-large-onnx-int8`
- Conversion scripts: included in `pipeline/`
- Validation: complete on the filtered `pangram/editlens_iclr` test split
- Publishing: complete at <https://huggingface.co/benreeve/editlens-roberta-large-onnx-int8>
- Browser smoke: Chromium loaded the real Hugging Face model and completed paragraph scoring locally

The public demo is intentionally disabled for now because the model output is not reliable enough for a public tool. See `RESTORE.md` for the short path to re-enable it later.

## Runtime architecture

1. The static page loads Transformers.js from jsDelivr.
2. Transformers.js downloads tokenizer/config/ONNX files from Hugging Face.
3. The browser caches those static files when possible.
4. Text is split into paragraphs locally.
5. Each eligible paragraph is scored locally by ONNX Runtime Web.

No text is uploaded. The only network traffic during analysis should be static library/model downloads.

## Hosting notes

The app is designed to be served by GitHub Pages with Cloudflare in front of it. Multi-threaded ONNX Runtime Web needs cross-origin isolation headers, and GitHub Pages cannot set those headers directly.

Cloudflare should add a Response Header Transform Rule for `/editlens` and `/editlens/*`:

```text
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
Cross-Origin-Resource-Policy: cross-origin
```

The helper script at `scripts/apply-editlens-cloudflare-headers.sh` upserts this rule when given a Cloudflare token with Transform Rules edit permission. See `docs/hosting.md` for the exact expression and verification steps.

## Model and license

- Base model: `FacebookAI/roberta-large`
- Fine-tune: `pangram/editlens_roberta-large`
- Upstream license: CC BY-NC-SA 4.0
- Paper: <https://arxiv.org/abs/2510.03154>
- Upstream code: <https://github.com/pangramlabs/EditLens>
- Model card: <https://huggingface.co/pangram/editlens_roberta-large>

Merged and quantized ONNX files are derivative artifacts and should be published under CC BY-NC-SA 4.0 with attribution to Pangram.

## Conversion flow

Run on a Python/CUDA box with `HF_TOKEN` set and the Pangram gate accepted:

```sh
cd editlens/pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python 01_download.py
python 02_merge.py
python 03_export_onnx.py
python 04_quantize.py
python 05_validate.py
```

`04_quantize.py` writes a Transformers.js-compatible repo folder to `artifacts/04_web_repo/`. Upload that folder to the Hugging Face model repo named in `editlens/index.draft.html.txt`.

The original planning spec assumed the Pangram release was a PEFT adapter that had to be merged into `FacebookAI/roberta-large`. The gated repo currently contains a full RoBERTa sequence-classification checkpoint with four labels, so `02_merge.py` copies it through directly. If Pangram ships a PEFT-only checkpoint later, the script still has a merge path.

## Responsible defaults

- Refuses to score documents under 200 words.
- Skips individual paragraphs under 30 words.
- Shows paragraph-level model output only.
- Does not produce a document-level score.
- Does not include export or share buttons.
- Uses neutral score language and neutral score colors.
- Links to known failure modes above the input field.
