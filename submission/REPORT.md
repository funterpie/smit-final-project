# PR Risk Scorer

## Abstract

PR Risk Scorer is a just-in-time commit triage system. It extracts structured
change features, combines a heuristic risk score with optional trained model
signals, retrieves a similar historical example, and records a human review
decision. Evaluation artifacts report CodeBERT AUC-PR 0.5314 and Recall@20%
0.4245 on a 1,200-commit test split. The score prioritizes review; it does not
decide whether a change is defective.

## Introduction

Software teams have limited review capacity. Just-in-time (JIT) defect
prediction estimates whether a change is likely to introduce a defect while
the change is being reviewed. This project turns that estimate into a local
CLI and dashboard workflow with evidence and an audit trail.

## Problem statement

The system must help a reviewer prioritize a commit using available change
information, interpretable signals, and historical evidence while leaving the
decision to the reviewer. Its score is a triage measure, not a calibrated
probability or an automatic merge decision.

## Literature and background

JIT defect prediction research models change-level properties such as size,
dispersion, and developer history. ApacheJIT supplies commit-level examples.
SZZ-style tracing connects bug-fixing changes to earlier changes that may have
introduced the defect; these labels are useful but heuristic and potentially
noisy. CodeBERT is a pretrained model for programming-language and natural
language representations.

### Just-in-time defect prediction

JIT prediction estimates defect risk near the time a change is made so review
effort can be allocated early. This implementation uses change-level features
and emits an interpretable score for review prioritization.

### SZZ labels

SZZ uses version history to find candidate bug-inducing commits linked to
later fixes. Candidate labels can be incomplete or misattributed; the
evaluation treats them as imperfect historical labels.

### CodeBERT

CodeBERT is pretrained for programming-language and natural-language
representations. In this project, its live input is a text rendering of
structured commit features, not source code or a diff.

## Methodology

The extractor uses PyDriller and produces structured measures including lines
added/deleted, files changed, file dispersion, sensitive-path indicators,
test-file indicators, elapsed time, and an author bug-rate field. The live
author bug-rate value is currently a `0.0` placeholder. The heuristic engine
combines weighted signals into a bounded 0–100 score. Logistic Regression and
Random Forest use structured features. The CodeBERT path encodes the
structured feature values as text; it does not tokenize or classify the raw
diff. Model artifacts and evaluation split details are maintained in the
repository.

## System architecture and implementation

The CLI extracts features from a Git commit, computes risk, optionally queries
FAISS for historical evidence, and emits human-readable or JSON output. The
API exposes review records and decisions to a React dashboard. SQLite stores
scores, signal descriptions, evidence metadata, explanations, and decisions;
raw diffs are not persisted by the CLI audit path. The explanation component
can use Groq with derived risk metadata and retrieved evidence, or a local
fallback. Explanations are not model scores and do not replace review.

## Evaluation

The checked-in test feature file has 1,200 commits and a 26.5% positive rate.
The evaluation report compares a heuristic, Logistic Regression, Random
Forest, and CodeBERT. The stored bootstrap artifacts use 1,000 percentile
resamples with seed 42 for AUC-PR and Recall@20%; no intervals are stored for
AUC-ROC or FPR@0.5. Full values and interpretation are in
[`RESULTS.md`](RESULTS.md).

## Results and discussion

CodeBERT has the highest point estimates for AUC-ROC (0.7604) and AUC-PR
(0.5314). Random Forest has the lowest FPR@0.5 (0.1020). CodeBERT's AUC-PR
advantage over Random Forest is 0.0204 and its Recall@20% advantage is 0.0063.
The marginal intervals overlap; the repository does not report a paired
bootstrap interval for these differences or a hypothesis test. These results
do not establish a statistically meaningful improvement.

## Limitations

The evaluated test split is modest and imbalanced, SZZ-derived labels can be
noisy, and dataset characteristics may not transfer to another repository.
The live author-history feature is a placeholder. The CodeBERT input is a
structured text rendering rather than code diff content. Historical retrieval
depends on index coverage and a configured similarity threshold. Groq
availability and quality depend on external service access. Scores should be
used for prioritization with human oversight.

## Conclusion and future work

The project demonstrates an end-to-end local commit-risk workflow with
auditable human decisions. Useful next steps are repository-specific
calibration, a real privacy-conscious author-history feature, paired
uncertainty estimates, broader external validation, and stronger evaluation
of retrieval and explanation quality.

## References

1. Kamei et al., “A Large-Scale Empirical Study of Just-in-Time Quality
   Assurance,” IEEE Transactions on Software Engineering, 2013.
   [DOI](https://doi.org/10.1109/TSE.2012.70)
2. Sliwerski, Zimmermann, and Zeller, “When Do Changes Induce Fixes?”
   [DOI](https://doi.org/10.1145/1082983.1083147)
3. Hoang et al., “ApacheJIT: A Large Dataset for Just-In-Time Defect
   Prediction,” 2022. [arXiv](https://arxiv.org/abs/2203.00101)
4. Feng et al., “CodeBERT: A Pre-Trained Model for Programming and Natural
   Languages,” Findings of EMNLP 2020.
   [ACL Anthology](https://aclanthology.org/2020.findings-emnlp.139/)
5. Davis and Goadrich, “The Relationship Between Precision-Recall and ROC
   Curves,” ICML 2006. [DOI](https://doi.org/10.1145/1143844.1143874)
