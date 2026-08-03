# Methodology

## Aim

The project asks whether the ordinal education code in the supplied
questionnaire is associated with conservative Spanish-English code-switching
frequency.

## Data boundary

The public repository contains no Bangor Miami transcripts, questionnaire
responses or token exports. The `data/sample` directory is synthetic and exists
only to demonstrate the pipeline.

## Speaker alignment

CHAT/TSV speaker codes and questionnaire IDs are different identifier systems.
A mapping is confirmed only when one questionnaire row uniquely matches:

1. normalised recording filename;
2. age at the recording date;
3. normalised sex.

Ambiguous, incomplete and filename-only candidates remain unresolved. They are
reported in `mapping_audit.csv` but excluded from education analysis.

## Conservative switch definition

Tokens are ordered within each recording, speaker and utterance. A switch is
counted only for adjacent `eng -> spa` or `spa -> eng` tokens. Any other label,
including `999`, mixed labels and transcription artefacts, resets the sequence.
The rule-based identifier never bridges an utterance boundary. It operates on
the corpus-provided token-level language annotations; it is not an automatic
language-identification classifier.

The preferred exposure is the number of eligible adjacent pairs: consecutive
`eng`/`spa` tokens within the same recording, speaker and utterance, with no
intervening reset label. For participant `i`:

```text
pair_rate_i = switch_count_i / eligible_adjacent_pairs_i * 1000
```

The earlier valid-token rate is retained as a backward-compatible descriptive
field. Eligible pairs are the more direct denominator because each pair is one
opportunity under the implemented transition rule. This operational definition
is intentionally narrower than the full linguistic concept of code-switching.

## Statistical model

The primary participant-level model treats `intra_switch_count` as a count and
uses `log(eligible_adjacent_pairs)` as an offset. Education level enters as an
ordinal predictor in a Poisson log-link model. An NB2 quasi-likelihood model,
with a moment-estimated dispersion parameter, checks sensitivity to
overdispersion. Both report HC3-style sandwich standard errors and education
incidence-rate ratios (IRRs). Rate-based group tests and HC3 linear regression
on the eligible-pair rate are retained as exploratory sensitivity analyses
rather than the primary count model.

## Education recoding

The five original codes are retained and additionally grouped as:

- Low: 1-2
- Middle: 3
- High: 4-5

This is an ordinal, researcher-defined grouping for statistical comparison. It
does not assign unsupported real-world degree labels to the corpus codes.

## Verified private run

The full local run produced 73 strictly matched participants, 195,864 valid
English/Spanish tokens and 2,980 conservative switch events. Group means were
13.63, 14.81 and 15.74 switches per 1,000 valid tokens for Low, Middle and High.
Welch's test (`p = .8976`) and Kruskal-Wallis (`p = .8434`) did not support a
group difference.

These verified figures use the backward-compatible valid-token rate. The
eligible-pair rates and count-model estimates are not reported until the
upgraded pipeline is rerun locally on the licensed source data.

## Interpretation

The result is a null finding under this operational definition and strict
mapping policy. It does not show that education can never be associated with
code-switching. The small Low group, excluded unresolved mappings and narrow
switch definition limit generalisation.
