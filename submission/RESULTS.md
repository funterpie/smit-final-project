# Evaluation Results

## Source and scope

Values below are copied from [`eval/results.json`](../eval/results.json) and
cross-checked against the processed test CSV. The CSV contains 1,200 commits,
with a 26.5% positive (`buggy`) rate. These are existing evaluation artifacts;
this document does not claim that model training or the full evaluation was
rerun during the current dashboard verification.

The point estimates were computed by `eval/evaluate.py`. AUC-PR is scikit-learn
average precision, Recall@20% is the fraction of positive commits among the
highest-scored 20% of the test set, and FPR@0.5 is the false-positive rate at a
probability threshold of 0.5. The stored 95% intervals come from 1,000
percentile bootstrap resamples with seed 42 for AUC-PR and Recall@20%.

## Results

| Model | AUC-ROC | AUC-PR | AUC-PR 95% CI | Recall@20% | Recall@20% 95% CI | FPR@0.5 |
|---|---:|---:|---:|---:|---:|---:|
| Heuristic | 0.6345 | 0.3785 | [0.3365, 0.4239] | 0.3711 | [0.3279, 0.4114] | 0.1224 |
| Logistic Regression | 0.6878 | 0.4520 | [0.4024, 0.5109] | 0.3365 | [0.3003, 0.3785] | 0.2846 |
| Random Forest | 0.7423 | 0.5110 | [0.4614, 0.5710] | 0.4182 | [0.3773, 0.4626] | 0.1020 |
| CodeBERT | 0.7604 | 0.5314 | [0.4796, 0.5903] | 0.4245 | [0.3814, 0.4667] | 0.1281 |

The JSON contains no confidence intervals for AUC-ROC or FPR@0.5; those values
are therefore reported without intervals. See
[`charts/model_metrics.png`](charts/model_metrics.png) for the four point
metrics and the available intervals.

## CodeBERT compared with Random Forest

CodeBERT's point estimate is +0.0204 in AUC-PR (0.5314 versus 0.5110) and
+0.0063 in Recall@20% (0.4245 versus 0.4182). Their marginal bootstrap
intervals overlap for both reported metrics. The available analysis does not
bootstrap the paired difference between models and does not report a separate
hypothesis test. The evidence therefore does **not establish** that CodeBERT's
improvement is statistically meaningful; overlap of marginal intervals alone
is not a formal significance test.

Random Forest has the lowest reported FPR@0.5 (0.1020), while CodeBERT has the
highest AUC-ROC and AUC-PR point estimates. These are descriptive results on
this split, not a claim that one model is universally preferable.

## Reproduction commands

```bash
python eval/evaluate.py --test-csv data/processed/test_features.csv --codebert
python eval/bootstrap_ci.py --test-csv data/processed/test_features.csv --codebert
```

The evaluation scripts write `eval/results.json`; preserve a copy before
rerunning if the current submitted artifact must remain unchanged.
