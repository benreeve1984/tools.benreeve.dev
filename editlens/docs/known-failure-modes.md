# Known Failure Modes

AI detector outputs are not reliable enough to make decisions about people. This demo keeps the failure modes visible because the model output is easy to misuse.

## Short text

Short text has too little evidence for stable scoring. The page refuses documents under 200 words and skips individual paragraphs under 30 words.

## Non-native English writing

AI detectors have documented elevated false-positive rates for non-native English writing. A high score can reflect style, genre, editing conventions, or training-set bias rather than AI authorship.

## Domain mismatch

The model was trained and validated on Pangram's released data. Text from other domains, genres, languages, or time periods may shift the score distribution.

## Heavy editing

The model estimates the extent of AI editing. It is not an authorship oracle. Human-edited, professionally edited, translated, templated, or highly formulaic writing can resemble model-edited text.

## Adversarial robustness

Users can intentionally modify text to change detector scores. The page should not be treated as robust against paraphrasing, style transfer, translation, prompt engineering, or manual edits.

## Long paragraphs

The browser chunks long paragraphs because RoBERTa has a fixed context window. Chunked scores are useful for interaction, but they should be separately validated against the upstream Python pipeline before being used in quantitative analysis.
