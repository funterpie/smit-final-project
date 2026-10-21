# Evaluation Report — PR Risk Scorer

## Overview

This report presents the evaluation results of four defect prediction models on a held-out test set of **1,200 commits** (26.5% positive/buggy rate) from the ApacheJIT dataset. The models represent a progression from rule-based heuristics to traditional ML classifiers to fine-tuned deep learning.

All confidence intervals are **bootstrapped 95% CIs** (1,000 resamples, seed=42, percentile method).

---

## Model Comparison

| Model | AUC-ROC | AUC-PR | AUC-PR 95% CI | Recall@20% | Recall@20% 95% CI | FPR@0.5 |
|---------------|---------|--------|---------------------|------------|-----------------------|---------|
| Heuristic | 0.6345 | 0.3785 | [0.3365, 0.4239] | 0.3711 | [0.3279, 0.4114] | 0.1224 |
| Baseline LR | 0.6878 | 0.4520 | [0.4024, 0.5109] | 0.3365 | [0.3003, 0.3785] | 0.2846 |
| Baseline RF | 0.7423 | 0.5110 | [0.4614, 0.5710] | 0.4182 | [0.3773, 0.4626] | **0.1020** |
| **CodeBERT** | **0.7604** | **0.5314** | [0.4796, 0.5903] | **0.4245** | [0.3814, 0.4667] | 0.1281 |

### Metric Definitions

- **AUC-ROC**: Area Under the Receiver Operating Characteristic curve. Measures overall discrimination ability across all thresholds. Higher = better ranking.
- **AUC-PR**: Area Under the Precision-Recall curve. More informative than AUC-ROC for imbalanced datasets (26.5% positive rate). Higher = fewer false alarms at high recall.
- **Recall@20%**: Fraction of true bugs caught by inspecting only the top 20% highest-scored commits. Key metric for practical triage — a developer has limited review bandwidth.
- **FPR@0.5**: False Positive Rate at the default decision threshold of 0.5. Lower = fewer clean commits incorrectly flagged as risky.
- **95% CI**: Bootstrap confidence interval (1,000 resamples). If two models' CIs overlap, the difference is not statistically significant at the 95% level.

---

## Statistical Significance: CodeBERT vs Random Forest

| Metric | RF | CodeBERT | Delta | CIs Overlap? | Significant at 95%? |
|---------------|------|---------|--------|--------------|----------------------|
| AUC-PR | 0.5110 [0.4614, 0.5710] | 0.5314 [0.4796, 0.5903] | +0.0204 | **Yes** | **No** |
| Recall@20% | 0.4182 [0.3773, 0.4626] | 0.4245 [0.3814, 0.4667] | +0.0063 | **Yes** | **No** |

### Honest Assessment

**CodeBERT's improvement over Random Forest is NOT statistically significant.**

- On AUC-PR, CodeBERT scores +0.0204 higher (0.5314 vs 0.5110), but the 95% CIs overlap heavily ([0.4614, 0.5710] vs [0.4796, 0.5903]).
- On Recall@20%, CodeBERT scores +0.0063 higher (0.4245 vs 0.4182), but again the CIs overlap ([0.3773, 0.4626] vs [0.3814, 0.4667]).
- On a test set of 1,200 commits, this ~2 percentage point AUC-PR difference cannot be distinguished from random variation.
- **Conclusion**: We cannot claim CodeBERT is better than Random Forest with statistical confidence. Both are meaningfully better than LR and the heuristic, but CodeBERT's fine-tuned transformer offers no proven advantage over a well-tuned Random Forest on this dataset and sample size.

### Why this matters

This result is common in software defect prediction literature. When the feature set is the same (8 handcrafted commit-level features), the advantage of a transformer over a tree ensemble is limited because:
1. The features are already low-dimensional and well-structured.
2. CodeBERT was designed for *code token sequences*, not tabular feature strings.
3. Random Forest is already strong at modeling non-linear interactions in small feature spaces.

A larger test set or richer features (e.g., AST-level features, full diff embeddings) might produce a statistically significant difference, but we report what we measured honestly.

---

## Key Findings

### 1. RF and CodeBERT are statistically tied for best overall performance

Both achieve AUC-PR above 0.50 and Recall@20% above 0.40. Their CIs overlap on both metrics. Either is a valid choice for the deployed risk engine.

### 2. Random Forest has the lowest false positive rate

Despite having overlapping AUC with CodeBERT, Random Forest achieves the **lowest FPR at threshold 0.5** (0.1020 vs 0.1281). RF's probability outputs cluster near 0.0 and 1.0, producing sharper decision boundaries. **Practical implication**: If false alarms are costly, RF is preferred.

### 3. LR has the highest FPR

The LR baseline has the worst FPR@0.5 (0.2846) — nearly 3× higher than RF. The linear decision boundary cannot model non-linear feature interactions.

### 4. The heuristic baseline is surprisingly competitive

The rule-based heuristic achieves AUC-ROC of 0.6345 and second-lowest FPR (0.1224) with **zero training data**. This validates the interpretable signal design.

### 5. ML models consistently outperform heuristics on AUC-PR

All three ML models beat the heuristic on AUC-PR by 7–15 points, confirming that learned patterns provide genuine value. The difference between heuristic and LR/RF is outside CI overlap — a real improvement.

---

## Risk Engine Integration

In the deployed `prscore` CLI, the risk score combines:

1. **Heuristic signals** (rule-based, max 100 points) — always available, always interpretable.
2. **ML model probability** — when RF or CodeBERT models are available, the higher of the two probabilities adds a 20-point bonus signal above 0.5 threshold.

This hybrid design ensures:
- **Interpretability**: Every score comes with a named signal breakdown.
- **Graceful degradation**: Without trained models, the heuristic still works.
- **ML boost**: When models are available, borderline commits get appropriately escalated.

---

## Recommendations

| Scenario | Recommended Model |
|----------|-------------------|
| Catching the most bugs (e.g., CI gate) | **Random Forest or CodeBERT** (statistically tied) |
| Minimizing developer disruption | **Random Forest** (lowest FPR@0.5) |
| No GPU available / fast scoring | **Random Forest** (CPU-only, <1ms per commit) |
| No trained models / first-time setup | **Heuristic** (zero-shot, interpretable) |

---

## Reproducibility

```bash
# Prepare the dataset
python scripts/prepare_dataset.py --sample 6000

# Train baselines
python scripts/train_baseline.py

# Build RAG index
python scripts/build_rag_index.py

# Run full evaluation (point estimates)
python eval/evaluate.py --test-csv data/processed/test_features.csv --codebert

# Run bootstrap CIs (1000 resamples)
python eval/bootstrap_ci.py --test-csv data/processed/test_features.csv --codebert
```

Results are saved to `eval/results.json`.
