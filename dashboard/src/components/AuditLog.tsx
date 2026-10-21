import type { Decision } from '../types';

interface Props {
  decisions: Decision[];
  loading: boolean;
}

function decisionIcon(d: string) {
  switch (d) {
    case 'approve': return '✓';
    case 'request_changes': return '↻';
    case 'escalate': return '⚠';
    default: return '?';
  }
}

export default function AuditLog({ decisions, loading }: Props) {
  if (loading) {
    return (
      <div className="glass-card p-5 space-y-3">
        <div className="skeleton h-4 w-32 mb-4" />
        {[...Array(4)].map((_, i) => (
          <div key={i} className="skeleton h-12 w-full" />
        ))}
      </div>
    );
  }

  if (decisions.length === 0) {
    return (
      <div className="glass-card p-8 text-center">
        <p className="text-surface-400 text-sm">No decisions logged yet.</p>
        <p className="text-surface-500 text-xs mt-1">Use the review panel to approve, request changes, or escalate.</p>
      </div>
    );
  }

  return (
    <div className="glass-card overflow-hidden">
      <div className="px-5 py-4 border-b border-white/[0.06]">
        <h3 className="text-xs uppercase tracking-widest text-surface-400">
          Audit Trail
        </h3>
      </div>
      <div className="divide-y divide-white/[0.04]">
        {decisions.map((d) => (
          <div
            key={d.id}
            className="px-5 py-3 flex items-center gap-3 hover:bg-white/[0.02] transition-colors"
          >
            <span
              className={`
                w-8 h-8 rounded-lg flex items-center justify-center text-sm
                ${d.decision === 'approve'
                  ? 'bg-green-500/15 text-green-400'
                  : d.decision === 'request_changes'
                    ? 'bg-amber-500/15 text-amber-400'
                    : 'bg-red-500/15 text-red-400'
                }
              `}
            >
              {decisionIcon(d.decision)}
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-surface-200">
                <span className="font-mono text-xs">{d.commit_ref.slice(0, 10)}</span>
                <span className="mx-2 text-surface-600">→</span>
                <span className={`badge-${d.decision}`}>
                  {d.decision === 'request_changes' ? 'Changes' : d.decision}
                </span>
              </p>
              {d.note && (
                <p className="text-xs text-surface-500 mt-0.5 truncate">{d.note}</p>
              )}
            </div>
            <div className="text-right">
              <p className="text-xs text-surface-500">
                {new Date(d.timestamp).toLocaleDateString()}
              </p>
              <p className="text-[10px] text-surface-600">
                Score {d.score}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
