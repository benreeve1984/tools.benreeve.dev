# Methodology

EditLens is a model released by Pangram for estimating the extent of AI editing in text. The browser demo is intended to reproduce the public inference path for `pangram/editlens_roberta-large` after converting the model to ONNX.

## Preprocessing

The browser follows the upstream preprocessing as closely as possible without adding another dependency:

- remove text up to and including a closing `</think>` marker
- remove some common assistant boilerplate first paragraphs
- lowercase text
- normalize whitespace

The upstream Python code also demojizes emoji before scoring. The browser demo does not yet reproduce that exact emoji normalization because the page avoids another runtime dependency. Validation should include emoji-containing cases before making strict parity claims.

## Paragraph scoring

The page splits text on blank lines and scores only paragraph-level units. Paragraphs under 30 words are skipped because short text is unstable for detector-style models.

RoBERTa has a 512-token context window. The browser uses local word chunks for long paragraphs, then returns a word-weighted average across chunk scores. This avoids silently scoring only the first part of a long paragraph, but it means long-paragraph browser scores are not identical to the upstream single-pass script.

## Score calculation

Pangram's inference script treats EditLens as bucketed regression. The model returns a probability distribution over score buckets, and the scalar score is the expected bucket value normalized to `[0, 1]`.

The gated RoBERTa checkpoint exposes four labels, matching the public RoBERTa training config. The browser therefore computes:

```text
score = (p0 * 0 + p1 * 1 + p2 * 2 + p3 * 3) / 3
```

If the gated checkpoint reveals a different bucket count, update `N_BUCKETS` in `index.html` and rerun validation.

## Model artifact

The published browser artifact is an INT8 dynamic-quantized ONNX file. The quantized model is 358.2 MB. This is larger than the initial estimate in the planning notes, but it is consistent with quantizing a RoBERTa-large checkpoint from roughly 1.4 GB FP32 weights.

## Scope

This is not a general-purpose authorship tool. It is a reproduction interface for researchers who want to inspect the model locally in a browser. Scores should not be used to judge students, employees, applicants, reviewers, or any other person.
