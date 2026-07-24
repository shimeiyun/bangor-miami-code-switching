# Verified full-corpus results

The figures below are aggregate outputs from the private licensed corpus run.
No transcript text, questionnaire responses or participant-level rows are
redistributed.

![Mean conservative switch rate by education group](../assets/education-group-rates.svg)

| Education group | Participants | Mean rate | SD | Median |
|---|---:|---:|---:|---:|
| Low (levels 1-2) | 5 | 13.63 | 11.05 | 9.51 |
| Middle (level 3) | 31 | 14.81 | 11.63 | 12.76 |
| High (levels 4-5) | 37 | 15.74 | 10.47 | 14.14 |

Rates are conservative within-utterance `eng -> spa` or `spa -> eng`
transitions per 1,000 valid English/Spanish tokens.

## Inferential checks

| Test | Statistic | p-value |
|---|---:|---:|
| Welch one-way ANOVA | 0.109 | .8976 |
| Kruskal-Wallis | 0.341 | .8434 |
| Ordinary one-way ANOVA | 0.114 | .8927 |
| Welch ANOVA excluding IQR outliers | 1.771 | .2180 |

None of the planned or sensitivity analyses provides reliable evidence of an
education-group difference. The slight increase in the descriptive means
should not be interpreted as a statistically supported trend.

## Responsible conclusion

Under the strict mapping policy and conservative switch definition, education
group did not reliably explain participant-level switching rates. This is a
valid null result, not a failed project: the primary contribution is the
transparent computational workflow and its explicit uncertainty handling.
