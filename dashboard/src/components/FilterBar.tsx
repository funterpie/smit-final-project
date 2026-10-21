import type { RiskLevel, DecisionFilter } from '../types';

interface Props {
  riskFilter: RiskLevel | null;
  decisionFilter: DecisionFilter | null;
  onRiskChange: (v: RiskLevel | null) => void;
  onDecisionChange: (v: DecisionFilter | null) => void;
}

function FilterBtn({
  active,
  onClick,
  children,
  color,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
  color?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`
        px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200
        ${active
          ? 'text-white shadow-sm'
          : 'text-surface-400 hover:text-surface-200 hover:bg-white/[0.04]'
        }
      `}
      style={active ? { background: color || 'rgba(99,102,241,0.3)', borderColor: color } : {}}
    >
      {children}
    </button>
  );
}

export default function FilterBar({
  riskFilter,
  decisionFilter,
  onRiskChange,
  onDecisionChange,
}: Props) {
  return (
    <div className="flex flex-wrap items-center gap-2 py-3">
      <span className="text-[10px] uppercase tracking-widest text-surface-500 mr-1">Risk</span>
      <FilterBtn active={riskFilter === null} onClick={() => onRiskChange(null)}>
        All
      </FilterBtn>
      <FilterBtn active={riskFilter === 'high'} onClick={() => onRiskChange('high')} color="rgba(239,68,68,0.3)">
        High
      </FilterBtn>
      <FilterBtn active={riskFilter === 'medium'} onClick={() => onRiskChange('medium')} color="rgba(245,158,11,0.3)">
        Medium
      </FilterBtn>
      <FilterBtn active={riskFilter === 'low'} onClick={() => onRiskChange('low')} color="rgba(34,197,94,0.3)">
        Low
      </FilterBtn>

      <span className="w-px h-5 bg-white/[0.08] mx-2" />

      <span className="text-[10px] uppercase tracking-widest text-surface-500 mr-1">Status</span>
      <FilterBtn active={decisionFilter === null} onClick={() => onDecisionChange(null)}>
        All
      </FilterBtn>
      <FilterBtn active={decisionFilter === 'pending'} onClick={() => onDecisionChange('pending')} color="rgba(99,102,241,0.3)">
        Pending
      </FilterBtn>
      <FilterBtn active={decisionFilter === 'approve'} onClick={() => onDecisionChange('approve')} color="rgba(34,197,94,0.3)">
        Approved
      </FilterBtn>
      <FilterBtn active={decisionFilter === 'request_changes'} onClick={() => onDecisionChange('request_changes')} color="rgba(245,158,11,0.3)">
        Changes
      </FilterBtn>
      <FilterBtn active={decisionFilter === 'escalate'} onClick={() => onDecisionChange('escalate')} color="rgba(239,68,68,0.3)">
        Escalated
      </FilterBtn>
    </div>
  );
}
