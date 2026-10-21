interface Props {
  connected: boolean;
}

export default function Header({ connected }: Props) {
  return (
    <header className="flex items-center justify-between py-5 px-6 lg:px-8 animate-fade-in">
      <div className="flex items-center gap-3">
        {/* Logo mark */}
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-glow">
          <span className="text-lg font-bold text-white">PR</span>
        </div>
        <div>
          <h1 className="text-lg font-bold text-white tracking-tight">
            PR Risk Scorer
          </h1>
          <p className="text-[11px] text-surface-400 -mt-0.5">
            Just-in-time defect prediction
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium
          ${connected
            ? 'bg-green-500/10 text-green-400 border border-green-500/20'
            : 'bg-red-500/10 text-red-400 border border-red-500/20'
          }`}
        >
          <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-green-400 animate-pulse-soft' : 'bg-red-400'}`} />
          {connected ? 'API Connected' : 'Disconnected'}
        </div>
      </div>
    </header>
  );
}
