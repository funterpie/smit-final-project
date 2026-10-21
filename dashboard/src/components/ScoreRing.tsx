import { riskLevel, riskColor } from '../types';

interface Props {
  score: number;
  size?: number;
}

/** Animated SVG ring showing risk score 0-100. */
export default function ScoreRing({ score, size = 80 }: Props) {
  const level = riskLevel(score);
  const color = riskColor(level);
  const r = (size - 8) / 2;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - score / 100);

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        {/* background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth={6}
        />
        {/* progress arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={6}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{
            transition: 'stroke-dashoffset 0.8s ease-out',
            filter: `drop-shadow(0 0 6px ${color}60)`,
          }}
        />
      </svg>
      <span
        className="absolute text-lg font-bold font-mono"
        style={{ color }}
      >
        {score}
      </span>
    </div>
  );
}
