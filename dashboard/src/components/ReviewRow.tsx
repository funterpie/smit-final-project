import { riskLevel } from '../types';
import type { Review } from '../types';
import ScoreRing from './ScoreRing';

interface Props {
  review: Review;
  selected: boolean;
  onClick: () => void;
}

function decisionBadge(d: string | null) {
  if (!d) return <span className="badge-pending">Pending</span>;
  const label = d === 'request_changes' ? 'Changes' : d.charAt(0).toUpperCase() + d.slice(1);
  const cls = `badge-${d}`;
  return <span className={cls}>{label}</span>;
}

export default function ReviewRow({ review, selected, onClick }: Props) {
  const level = riskLevel(review.score);

  return (
    <button
      id={`review-row-${review.id}`}
      onClick={onClick}
      className={`
        w-full text-left p-4 rounded-xl transition-all duration-200
        flex items-center gap-4 group
        ${selected
          ? 'bg-brand-600/20 border border-brand-500/30 shadow-glow'
          : 'hover:bg-white/[0.04] border border-transparent'
        }
      `}
    >
      <ScoreRing score={review.score} size={52} />

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-mono text-sm text-surface-200 truncate">
            {review.commit_ref.slice(0, 10)}
          </span>
          <span className={`badge-${level}`}>{level}</span>
        </div>
        <p className="text-xs text-surface-400 truncate">
          {review.explanation
            ? review.explanation.slice(0, 90) + (review.explanation.length > 90 ? '…' : '')
            : 'No explanation available'}
        </p>
      </div>

      <div className="flex flex-col items-end gap-1.5">
        {decisionBadge(review.decision)}
        <span className="text-[10px] text-surface-500">
          {new Date(review.timestamp).toLocaleDateString()}
        </span>
      </div>
    </button>
  );
}
