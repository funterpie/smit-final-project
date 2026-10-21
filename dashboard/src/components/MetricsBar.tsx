import type { Metrics } from '../types';

interface Props {
  metrics: Metrics | null;
  loading: boolean;
}

interface StatProps {
  label: string;
  value: string | number;
  sub?: string;
  color?: string;
  delay?: string;
}

function Stat({ label, value, sub, color, delay = '0ms' }: StatProps) {
  return (
    <div
      className="glass-card p-5 animate-slide-up"
      style={{ animationDelay: delay }}
    >
      <p className="text-xs uppercase tracking-widest text-surface-400 mb-1">{label}</p>
      <p className="text-3xl font-bold font-mono" style={{ color: color || '#e2e8f0' }}>
        {value}
      </p>
      {sub && <p className="text-xs text-surface-500 mt-1">{sub}</p>}
    </div>
  );
}

export default function MetricsBar({ metrics, loading }: Props) {
  if (loading || !metrics) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="glass-card p-5">
            <div className="skeleton h-3 w-20 mb-3" />
            <div className="skeleton h-8 w-16" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
      <Stat label="Total Reviews" value={metrics.total_reviews} delay="0ms" />
      <Stat
        label="Avg Score"
        value={metrics.avg_score}
        color={metrics.avg_score >= 70 ? '#ef4444' : metrics.avg_score >= 30 ? '#f59e0b' : '#22c55e'}
        delay="60ms"
      />
      <Stat
        label="High Risk"
        value={metrics.risk_high}
        color="#ef4444"
        sub={`${metrics.risk_medium} medium · ${metrics.risk_low} low`}
        delay="120ms"
      />
      <Stat
        label="Pending"
        value={metrics.decisions.pending}
        color="#818cf8"
        sub={`${metrics.decisions.approve} approved`}
        delay="180ms"
      />
      <Stat
        label="LLM Fallback"
        value={`${(metrics.fallback_explanation_rate * 100).toFixed(0)}%`}
        sub="local explanations"
        delay="240ms"
      />
    </div>
  );
}
