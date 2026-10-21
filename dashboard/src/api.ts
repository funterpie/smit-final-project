/* ------------------------------------------------------------------ */
/* API client for the FastAPI backend                                 */
/* Requests are proxied through Vite: /api/* → localhost:8000/*       */
/* ------------------------------------------------------------------ */

import type { Review, Decision, Metrics, RiskLevel, DecisionFilter, DecisionType } from './types';

const BASE = '/api';

async function json<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json() as Promise<T>;
}

/* ---- Reviews ---------------------------------------------------- */
export async function fetchReviews(
  risk?: RiskLevel | null,
  decision?: DecisionFilter | null,
): Promise<Review[]> {
  const params = new URLSearchParams();
  if (risk) params.set('risk', risk);
  if (decision) params.set('decision', decision);
  const qs = params.toString();
  return json<Review[]>(`${BASE}/reviews${qs ? '?' + qs : ''}`);
}

export async function submitReview(
  commitHash: string,
  repoPath: string = '.',
): Promise<Review> {
  return json<Review>(`${BASE}/review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ commit_hash: commitHash, repo_path: repoPath }),
  });
}

/* ---- Decisions -------------------------------------------------- */
export async function postDecision(
  reviewId: number,
  decision: DecisionType,
  note: string = '',
): Promise<{ id: number; status: string }> {
  return json(`${BASE}/decisions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ review_id: reviewId, decision, note }),
  });
}

/* ---- Audit ------------------------------------------------------ */
export async function fetchAudit(): Promise<Decision[]> {
  return json<Decision[]>(`${BASE}/audit`);
}

/* ---- Metrics ---------------------------------------------------- */
export async function fetchMetrics(): Promise<Metrics> {
  return json<Metrics>(`${BASE}/metrics`);
}

/* ---- Health ----------------------------------------------------- */
export async function checkHealth(): Promise<boolean> {
  try {
    await json<{ status: string }>(`${BASE}/health`);
    return true;
  } catch {
    return false;
  }
}
