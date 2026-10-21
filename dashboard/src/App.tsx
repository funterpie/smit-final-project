import { useState, useEffect, useCallback } from 'react';
import type { Review, Decision, Metrics, RiskLevel, DecisionFilter } from './types';
import { fetchReviews, fetchMetrics, fetchAudit, checkHealth } from './api';

import Header from './components/Header';
import MetricsBar from './components/MetricsBar';
import FilterBar from './components/FilterBar';
import ReviewRow from './components/ReviewRow';
import ReviewDetail from './components/ReviewDetail';
import AuditLog from './components/AuditLog';
import RiskChart from './components/RiskChart';

type Tab = 'reviews' | 'audit' | 'charts';

export default function App() {
  /* ---- state ---------------------------------------------------- */
  const [connected, setConnected] = useState(false);
  const [tab, setTab] = useState<Tab>('reviews');

  const [reviews, setReviews] = useState<Review[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [decisions, setDecisions] = useState<Decision[]>([]);

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [riskFilter, setRiskFilter] = useState<RiskLevel | null>(null);
  const [decisionFilter, setDecisionFilter] = useState<DecisionFilter | null>(null);

  const [loading, setLoading] = useState(true);

  /* ---- data fetching -------------------------------------------- */
  const load = useCallback(async () => {
    setLoading(true);
    try {
      const ok = await checkHealth();
      setConnected(ok);
      if (!ok) { setLoading(false); return; }

      const [revs, met, aud] = await Promise.all([
        fetchReviews(riskFilter, decisionFilter),
        fetchMetrics(),
        fetchAudit(),
      ]);
      setReviews(revs);
      setMetrics(met);
      setDecisions(aud);
    } catch {
      setConnected(false);
    }
    setLoading(false);
  }, [riskFilter, decisionFilter]);

  useEffect(() => { load(); }, [load]);

  // Auto-refresh every 15 seconds
  useEffect(() => {
    const id = setInterval(load, 15_000);
    return () => clearInterval(id);
  }, [load]);

  const selectedReview = reviews.find((r) => r.id === selectedId) ?? null;

  /* ---- tabs ----------------------------------------------------- */
  const tabs: { key: Tab; label: string }[] = [
    { key: 'reviews', label: 'Reviews' },
    { key: 'charts', label: 'Analytics' },
    { key: 'audit', label: 'Audit Log' },
  ];

  /* ---- disconnected state --------------------------------------- */
  if (!loading && !connected) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header connected={false} />
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="glass-card p-10 max-w-md text-center space-y-4 animate-scale-in">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-red-500/10 flex items-center justify-center">
              <span className="text-3xl">⚡</span>
            </div>
            <h2 className="text-xl font-bold text-white">API Unreachable</h2>
            <p className="text-sm text-surface-400 leading-relaxed">
              Start the FastAPI backend first:
            </p>
            <code className="block text-xs bg-white/[0.04] rounded-xl p-3 font-mono text-brand-300">
              uvicorn api.main:app --reload --port 8000
            </code>
            <button onClick={load} className="btn-primary mt-4">
              Retry Connection
            </button>
          </div>
        </div>
      </div>
    );
  }

  /* ---- main layout ---------------------------------------------- */
  return (
    <div className="min-h-screen flex flex-col max-w-[1600px] mx-auto">
      <Header connected={connected} />

      <main className="flex-1 px-6 lg:px-8 pb-8 space-y-6">
        {/* Metrics */}
        <MetricsBar metrics={metrics} loading={loading} />

        {/* Tab bar */}
        <div className="flex items-center gap-1 border-b border-white/[0.06] pb-0">
          {tabs.map((t) => (
            <button
              key={t.key}
              id={`tab-${t.key}`}
              onClick={() => setTab(t.key)}
              className={`
                px-4 py-2.5 text-sm font-medium rounded-t-lg transition-all duration-200
                ${tab === t.key
                  ? 'text-white bg-white/[0.06] border-b-2 border-brand-500'
                  : 'text-surface-400 hover:text-surface-200 hover:bg-white/[0.02] border-b-2 border-transparent'
                }
              `}
            >
              {t.label}
            </button>
          ))}

          <div className="ml-auto">
            <button onClick={load} className="btn-ghost text-xs" id="btn-refresh">
              ↻ Refresh
            </button>
          </div>
        </div>

        {/* Tab content */}
        {tab === 'reviews' && (
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 animate-fade-in">
            {/* Review list */}
            <div className="lg:col-span-2 space-y-2">
              <FilterBar
                riskFilter={riskFilter}
                decisionFilter={decisionFilter}
                onRiskChange={setRiskFilter}
                onDecisionChange={setDecisionFilter}
              />
              <div className="space-y-1 max-h-[calc(100vh-360px)] overflow-y-auto pr-1">
                {loading && reviews.length === 0 ? (
                  [...Array(5)].map((_, i) => (
                    <div key={i} className="skeleton h-20 w-full rounded-xl" />
                  ))
                ) : reviews.length === 0 ? (
                  <div className="glass-card p-8 text-center">
                    <p className="text-surface-400 text-sm">No reviews match filters.</p>
                    <p className="text-surface-500 text-xs mt-1">
                      Run <code className="text-brand-300">prscore review HEAD</code> to score a commit.
                    </p>
                  </div>
                ) : (
                  reviews.map((r) => (
                    <ReviewRow
                      key={r.id}
                      review={r}
                      selected={selectedId === r.id}
                      onClick={() => setSelectedId(r.id)}
                    />
                  ))
                )}
              </div>
            </div>

            {/* Detail panel */}
            <div className="lg:col-span-3">
              {selectedReview ? (
                <ReviewDetail review={selectedReview} onDecisionMade={load} />
              ) : (
                <div className="glass-card p-12 flex flex-col items-center justify-center text-center h-full min-h-[300px]">
                  <div className="w-14 h-14 rounded-2xl bg-brand-500/10 flex items-center justify-center mb-4">
                    <span className="text-2xl">🔍</span>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-1">Select a Review</h3>
                  <p className="text-sm text-surface-400 max-w-xs">
                    Click on a review in the list to see the full risk breakdown, RAG evidence, and approve or escalate.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {tab === 'charts' && (
          <div className="animate-fade-in">
            <RiskChart metrics={metrics} />
          </div>
        )}

        {tab === 'audit' && (
          <div className="animate-fade-in">
            <AuditLog decisions={decisions} loading={loading} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center py-4 text-[11px] text-surface-600 border-t border-white/[0.04]">
        PR Risk Scorer · JIT Defect Prediction · Built with React + FastAPI + CodeBERT
      </footer>
    </div>
  );
}
