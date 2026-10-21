/* ------------------------------------------------------------------ */
/* Domain types matching the FastAPI backend                          */
/* ------------------------------------------------------------------ */

export interface Signal {
  name: string;
  weight: number;
  triggered: boolean;
  description: string;
}

export interface Evidence {
  commit_hash: string;
  similarity: number;
  summary: string;
}

export interface Review {
  id: number;
  timestamp: string;
  commit_ref: string;
  diff_hash: string;
  score: number;
  signals: Signal[];
  evidence: Evidence | null;
  explanation: string;
  explanation_source: string;
  decision: string | null;
}

export interface Decision {
  id: number;
  timestamp: string;
  decision: string;
  note: string;
  review_id: number;
  commit_ref: string;
  score: number;
  explanation_source: string;
}

export interface Metrics {
  total_reviews: number;
  avg_score: number;
  risk_high: number;
  risk_medium: number;
  risk_low: number;
  decisions: {
    pending: number;
    approve: number;
    request_changes: number;
    escalate: number;
  };
  fallback_explanation_rate: number;
}

export type RiskLevel = 'high' | 'medium' | 'low';
export type DecisionType = 'approve' | 'request_changes' | 'escalate';
export type DecisionFilter = 'pending' | DecisionType;

export function riskLevel(score: number): RiskLevel {
  if (score >= 70) return 'high';
  if (score >= 30) return 'medium';
  return 'low';
}

export function riskColor(level: RiskLevel): string {
  return { high: '#ef4444', medium: '#f59e0b', low: '#22c55e' }[level];
}
