import { useState } from 'react';
import type { Review, DecisionType } from '../types';
import { riskLevel, riskColor } from '../types';
import { postDecision } from '../api';
import ScoreRing from './ScoreRing';

interface Props {
  review: Review;
  onDecisionMade: () => void;
}

export default function ReviewDetail({ review, onDecisionMade }: Props) {
  const [note, setNote] = useState('');
  const [submitting, setSubmitting] = useState<DecisionType | null>(null);
  const [error, setError] = useState('');

  const level = riskLevel(review.score);
  const color = riskColor(level);
  const signalDescription = (name: string, triggered: boolean, description: string) => {
    if (name !== 'ml_model_flag') return description;
    return triggered
      ? 'The model probability crossed its configured threshold.'
      : 'No model probability crossed its configured threshold.';
  };

  async function handleDecision(decision: DecisionType) {
    setSubmitting(decision);
    setError('');
    try {
      await postDecision(review.id, decision, note);
      setNote('');
      onDecisionMade();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSubmitting(null);
    }
  }

  return (
    <div className="glass-card p-6 space-y-6 animate-fade-in" id="review-detail">
      {/* Header */}
      <div className="flex items-start gap-5">
        <ScoreRing score={review.score} size={90} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-lg font-semibold text-white truncate">
              {review.commit_ref}
            </h2>
            <span className={`badge-${level}`}>{level} risk</span>
          </div>
          <p className="text-xs text-surface-400 font-mono">
            Reviewed {new Date(review.timestamp).toLocaleString()}
          </p>
          {review.explanation_source && (
            <p className="text-xs text-surface-500 mt-1">
              Explanation: <span className="text-surface-300">{review.explanation_source}</span>
            </p>
          )}
        </div>
      </div>

      {/* Signals */}
      <div>
        <h3 className="text-xs uppercase tracking-widest text-surface-400 mb-3">
          Risk Signals
        </h3>
        <div className="space-y-2">
          {review.signals.map((sig) => (
            <div key={sig.name} className="flex items-center gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-surface-200 capitalize">
                    {sig.name.replace(/_/g, ' ')}
                  </span>
                  <span className="text-xs font-mono text-surface-400">
                    {sig.triggered ? sig.weight : 0} / {sig.weight} pts
                  </span>
                </div>
                <div className="h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{
                      width: sig.triggered ? '100%' : '0%',
                      background: `linear-gradient(90deg, ${color}80, ${color})`,
                    }}
                  />
                </div>
                <p className="text-xs text-surface-500 mt-1">
                  {signalDescription(sig.name, sig.triggered, sig.description)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Evidence */}
      <div className="glass-panel p-4 rounded-xl">
        <h3 className="text-xs uppercase tracking-widest text-surface-400 mb-2">
          RAG Evidence
        </h3>
        {review.evidence ? (
          <>
            <p className="text-sm text-surface-200 font-mono mb-1">
              {review.evidence.commit_hash.slice(0, 10)}
              <span className="text-surface-500 ml-2">
                sim: {(review.evidence.similarity * 100).toFixed(1)}%
              </span>
            </p>
            <p className="text-xs text-surface-400">{review.evidence.summary}</p>
          </>
        ) : (
          <p className="text-sm text-surface-400">
            No close historical match was found in the available RAG index.
          </p>
        )}
      </div>

      {/* Explanation */}
      {review.explanation && (
        <div className="glass-panel p-4 rounded-xl">
          <h3 className="text-xs uppercase tracking-widest text-surface-400 mb-2">
            Explanation · {review.explanation_source.replace(/_/g, ' ')}
          </h3>
          <p className="text-sm text-surface-200 leading-relaxed whitespace-pre-wrap">
            {review.explanation}
          </p>
        </div>
      )}

      {/* Decision */}
      <div className="border-t border-white/[0.06] pt-5">
        <h3 className="text-xs uppercase tracking-widest text-surface-400 mb-3">
          Decision
        </h3>

        {review.decision ? (
          <div className="flex items-center gap-2">
            <span className={`badge-${review.decision}`}>
              {review.decision === 'request_changes' ? 'Changes Requested' : review.decision}
            </span>
            <span className="text-xs text-surface-500">Decision logged</span>
          </div>
        ) : (
          <div className="space-y-3">
            <textarea
              id="decision-note"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Optional note…"
              rows={2}
              className="w-full px-3 py-2 rounded-xl bg-white/[0.04] border border-white/[0.08]
                text-sm text-surface-200 placeholder:text-surface-500
                focus:outline-none focus:border-brand-500/50 focus:ring-1 focus:ring-brand-500/30
                resize-none transition-colors"
            />
            <div className="flex gap-2">
              <button
                id="btn-approve"
                onClick={() => handleDecision('approve')}
                disabled={submitting !== null}
                className="btn-success flex-1"
              >
                {submitting === 'approve' ? '…' : '✓ Approve'}
              </button>
              <button
                id="btn-request-changes"
                onClick={() => handleDecision('request_changes')}
                disabled={submitting !== null}
                className="btn-warning flex-1"
              >
                {submitting === 'request_changes' ? '…' : '↻ Changes'}
              </button>
              <button
                id="btn-escalate"
                onClick={() => handleDecision('escalate')}
                disabled={submitting !== null}
                className="btn-danger flex-1"
              >
                {submitting === 'escalate' ? '…' : '⚠ Escalate'}
              </button>
            </div>
          </div>
        )}

        {error && (
          <p className="text-xs text-red-400 mt-2">{error}</p>
        )}
      </div>
    </div>
  );
}
