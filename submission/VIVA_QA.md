# Viva Questions and Evidence-Based Answers

## 1. Why not ask an LLM to review every diff?

The system uses learned commit-risk scores and named, repeatable signals for
triage. The LLM has a narrow role: it explains derived risk metadata and
retrieved evidence. It never receives the raw diff, and a human makes the final
decision.

## 2. What does the score mean?

It is a 0–100 weighted sum of triggered heuristic signals plus an optional
20-point model flag, capped at 100. It is a prioritization score, not a
calibrated probability of a defect.

## 3. Which models were compared?

The stored evaluation compares a rule-based heuristic, Logistic Regression,
Random Forest, and CodeBERT. The requested baseline comparison is retained.

## 4. Did CodeBERT significantly beat Random Forest?

That is not established. CodeBERT's AUC-PR point estimate is 0.5314 and RF's is
0.5110; Recall@20% is 0.4245 versus 0.4182. The marginal intervals overlap,
and the available artifacts contain no paired bootstrap difference interval or
formal hypothesis test.

## 5. Why might CodeBERT's gain be small?

In this implementation, CodeBERT receives a short text encoding of eight
structured features rather than source tokens or a raw diff. A transformer may
have limited advantage over RF on this low-dimensional tabular representation.
That is a plausible explanation, not a separately tested causal finding.

## 6. What is ApacheJIT?

It is a public dataset for just-in-time defect prediction, with commits labelled
as buggy or clean. The project uses a processed test split of 1,200 commits
with a 26.5% positive rate; it does not evaluate on the full published dataset
in this report.

## 7. What is SZZ?

SZZ traces lines changed by bug-fix commits back through version history to
identify candidate bug-inducing commits. The method is useful for historical
labels but can misattribute or miss changes; labels should not be treated as
perfect ground truth.

## 8. What does Recall@20% say?

It measures the share of all positive test commits found among the highest
scoring 20% of commits. It models a limited review budget; it is not the
precision of that selected group.

## 9. Why report AUC-PR as well as AUC-ROC?

With a 26.5% positive rate, AUC-PR focuses attention on precision among
predicted positives and is more informative for imbalanced ranking. AUC-ROC
remains useful as a complementary discrimination measure.

## 10. How does retrieval decide whether to show evidence?

The query embedding is searched against the FAISS inner-product index using
normalized vectors. A result is returned only when its cosine similarity meets
the configured threshold; otherwise the UI says no close historical match was
found.

## 11. What happens when there is no RAG match?

The review still has a score and signals. The explanation explicitly states
that no matching historical evidence was available; no nearest result is
forced into the review.

## 12. How is privacy handled?

The explanation function receives the computed score, triggered signal names,
and an evidence summary. The CLI CodeBERT path also receives a structured
feature string. Neither path sends the raw code diff to Groq.

## 13. Is the whole system offline?

Scoring and local explanation can run without a Groq key. The RAG index and its
embedding model must be available locally for retrieval; without them the
system continues and reports no match. A live Groq explanation requires
network access.

## 14. What is the most important live feature limitation?

The current CLI feature extractor sets `author_bug_rate` to 0.0 because it does
not yet build a repository-specific author history. That signal exists in the
weighted model and dataset mapping but is not personalized by live extraction.

## 15. What would you improve next?

Compute author history from repository data, validate thresholds on more
projects and time-based splits, test paired model differences, broaden the RAG
curation, and measure explanation faithfulness with a documented human-rated
protocol.
