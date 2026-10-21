import type { Metrics } from '../types';

interface Props {
  metrics: Metrics | null;
}

/**
 * Pure-CSS donut & bar charts — no external charting library required.
 * Falls back gracefully if metrics not loaded yet.
 */
export default function RiskChart({ metrics }: Props) {
  if (!metrics || metrics.total_reviews === 0) {
    return (
      <div className="glass-card p-6 flex items-center justify-center h-52">
        <p className="text-surface-500 text-sm">No data to chart yet.</p>
      </div>
    );
  }

  const total = metrics.total_reviews;
  const data = [
    { label: 'High', count: metrics.risk_high, color: '#ef4444' },
    { label: 'Medium', count: metrics.risk_medium, color: '#f59e0b' },
    { label: 'Low', count: metrics.risk_low, color: '#22c55e' },
  ];

  // CSS conic gradient for donut
  let cumPct = 0;
  const stops = data.flatMap((d) => {
    const pct = (d.count / total) * 100;
    const start = cumPct;
    cumPct += pct;
    return [`${d.color} ${start}% ${cumPct}%`];
  });

  const decisionData = [
    { label: 'Approved', count: metrics.decisions.approve, color: '#22c55e' },
    { label: 'Changes', count: metrics.decisions.request_changes, color: '#f59e0b' },
    { label: 'Escalated', count: metrics.decisions.escalate, color: '#ef4444' },
    { label: 'Pending', count: metrics.decisions.pending, color: '#818cf8' },
  ];

  const maxDec = Math.max(...decisionData.map((d) => d.count), 1);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* Donut chart */}
      <div className="glass-card p-6 animate-fade-in">
        <h3 className="text-xs uppercase tracking-widest text-surface-400 mb-4">
          Risk Distribution
        </h3>
        <div className="flex items-center gap-6">
          <div
            className="w-32 h-32 rounded-full relative flex-shrink-0"
            style={{
              background: `conic-gradient(${stops.join(', ')})`,
            }}
          >
            {/* Inner hole for donut */}
            <div className="absolute inset-3 rounded-full bg-surface-900/90 flex items-center justify-center">
              <span className="text-2xl font-bold font-mono text-white">{total}</span>
            </div>
          </div>
          <div className="space-y-2">
            {data.map((d) => (
              <div key={d.label} className="flex items-center gap-2">
                <span
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: d.color }}
                />
                <span className="text-sm text-surface-300">{d.label}</span>
                <span className="text-sm font-mono text-surface-400 ml-auto">
                  {d.count}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Decision bar chart */}
      <div className="glass-card p-6 animate-fade-in" style={{ animationDelay: '100ms' }}>
        <h3 className="text-xs uppercase tracking-widest text-surface-400 mb-4">
          Decision Breakdown
        </h3>
        <div className="space-y-3">
          {decisionData.map((d) => (
            <div key={d.label}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-surface-300">{d.label}</span>
                <span className="text-sm font-mono text-surface-400">{d.count}</span>
              </div>
              <div className="h-2 rounded-full bg-white/[0.06] overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{
                    width: `${(d.count / maxDec) * 100}%`,
                    backgroundColor: d.color,
                    boxShadow: `0 0 8px ${d.color}40`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
