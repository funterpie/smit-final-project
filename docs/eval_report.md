# Evaluation Report — PR Risk Scorer

## Overview

This report presents the evaluation results of four defect prediction models on a held-out test set of **1,200 commits** (26.5% positive/buggy rate) from the ApacheJIT dataset. The models represent a progression from rule-based heuristics to traditional ML classifiers to fine-tuned deep learning.

---

## Model Comparison

| Model | AUC-ROC | AUC-PR | Recall@20% | FPR@0.5 |
|---------------|---------|--------|------------|---------|
| Heuristic | 0.6345 | 0.3785 | 0.3711 | 0.1224 |
| Baseline LR | 0.6878 | 0.4520 | 0.3365 | 0.2846 |
| Baseline RF | 0.7423 | 0.5110 | 0.4182 | **0.1020** |
| **CodeBERT** | **0.7604** | **0.5314** | **0.4245** | 0.1281 |

### Metric Definitions

- **AUC-ROC**: Area Under the Receiver Operating Characteristic curve. Measures overall discrimination ability across all thresholds. Higher = better ranking.
- **AUC-PR**: Area Under the Precision-Recall curve. More informative than AUC-ROC for imbalanced datasets (26.5% positive rate). Higher = fewer false alarms at high recall.
- **Recall@20%**: Fraction of true bugs caught by inspecting only the top 20% highest-scored commits. Key metric for practical triage — a developer has limited review bandwidth.
- **FPR@0.5**: False Positive Rate at the default decision threshold of 0.5. Lower = fewer clean commits incorrectly flagged as risky.

---

## Key Findings

### 1. CodeBERT achieves the best overall ranking accuracy

CodeBERT leads on AUC-ROC (0.7604), AUC-PR (0.5314), and Recall@20% (0.4245). The fine-tuned transformer captures non-linear interactions between features that the logistic regression baseline misses, confirming the hypothesis stated in IDEA.md.

### 2. Random Forest has the lowest false positive rate

Despite having lower AUC-ROC than CodeBERT (0.7423 vs 0.7604), Random Forest achieves the **lowest FPR at threshold 0.5** (0.1020 vs 0.1281). This happens because:

- RF produces well-calibrated probability outputs that cluster near 0.0 and 1.0, producing sharper decision boundaries at 0.5.
- CodeBERT's softmax probabilities tend to spread more uniformly, pushing borderline cases above 0.5 more often.
- **Practical implication**: If false alarms are costly (developer time wasted reviewing clean commits), RF may be preferred despite lower AUC. If catching more bugs is the priority, CodeBERT is the better choice.

### 3. Logistic Regression has the highest FPR

The LR baseline has the worst FPR@0.5 (0.2846) — nearly 3× higher than RF. This is because LR fits a linear decision boundary that cannot model the non-linear feature interactions in the data, forcing overcompensation via a high intercept that tilts probabilities upward.

### 4. The heuristic baseline is surprisingly competitive

The rule-based heuristic (weighted signal combiner) achieves a solid AUC-ROC of 0.6345 and the second-lowest FPR (0.1224) with **zero training data required**. This validates the interpretable signal design: even without ML, the weighted signals provide useful risk stratification.

### 5. ML models consistently outperform heuristics on AUC-PR

All three ML models beat the heuristic on AUC-PR by 7–15 points, confirming that learning from historical bug patterns provides genuine value beyond hand-crafted rules.

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
| Catching the most bugs (e.g., CI gate) | **CodeBERT** (best AUC-PR and Recall@20%) |
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

# Run full evaluation
python eval/evaluate.py --test-csv data/processed/test_features.csv --codebert
```

Results are saved to `eval/results.json`.
