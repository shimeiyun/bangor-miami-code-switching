# Data dictionary

## Mapping audit

| Field | Meaning |
|---|---|
| `chat_file` | Recording/transcript stem |
| `chat_speaker_id` | Pseudonymised CHAT speaker code |
| `chat_age_years` | Whole-year age parsed from CHAT `@ID` |
| `chat_gender_normalized` | Normalised CHAT gender |
| `same_file_candidate_count` | Questionnaire rows sharing the soundfile |
| `exact_candidate_count` | Rows matching soundfile, age and sex |
| `mapping_status` | Confirmed, ambiguous or unresolved status |
| `questionnaire_id` | Added only for a unique exact match |
| `education_level` | Original ordinal code, not an interpreted school stage |
| `education_group` | Researcher-defined 1–2 / 3 / 4–5 recoding |

## Token data

| Field | Meaning |
|---|---|
| `filename` | Recording identifier |
| `speaker` | CHAT speaker code |
| `word_id` | Corpus word-row identifier |
| `utterance_id` | Utterance boundary used by conservative transition identification |
| `location` | Token position within the utterance |
| `surface` | Transcribed surface form |
| `langid` | Corpus language label |
| `clause`, `clauseno` | Clause annotations when supplied |

## Switch events

| Field | Meaning |
|---|---|
| `direction` | `eng_to_spa` or `spa_to_eng` |
| `previous_surface` | First token in the transition |
| `current_surface` | Second token in the transition |
| `utterance_id` | Shared utterance; transitions never cross this boundary |

## Participant rates

`switch_rate_per_1000_valid_tokens` is:

```text
intra_switch_count / valid_eng_spa_tokens × 1,000
```

Only `eng` and `spa` contribute to the denominator.

## Statistical outputs

### `inferential_tests.csv`

| Column | Meaning |
|---|---|
| `test` | Name of the omnibus or sensitivity test |
| `statistic` | Test statistic |
| `df1`, `df2` | Degrees of freedom where applicable |
| `p_value` | Computed tail probability |
| `role` | Pre-declared analytical purpose |

### `education_level_regression.csv`

Long-format output containing the ordinal education-level slope, HC3 robust
standard error, t statistic, p-value, normal-approximation confidence interval,
R-squared and sample size.

### `statistical_summary.json`

Structured combined output containing all inferential tests, ordinary-ANOVA
effect size, HC3 regression and the IQR outlier sensitivity audit.
