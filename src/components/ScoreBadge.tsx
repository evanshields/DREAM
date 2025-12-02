type Size = 'sm' | 'md' | 'lg';

interface ScoreBadgeProps {
  score: number; // 0-100
  size?: Size;
}

const sizeConfig = {
  sm: {
    containerSize: 'w-16 h-16',
    textSize: 'text-lg',
    subtextSize: 'text-[10px]',
    strokeWidth: 3,
    radius: 28,
  },
  md: {
    containerSize: 'w-24 h-24',
    textSize: 'text-2xl',
    subtextSize: 'text-xs',
    strokeWidth: 4,
    radius: 42,
  },
  lg: {
    containerSize: 'w-32 h-32',
    textSize: 'text-4xl',
    subtextSize: 'text-sm',
    strokeWidth: 5,
    radius: 58,
  },
};

function getScoreColor(score: number): string {
  if (score >= 70) return '#58ABA8'; // seafoam (success)
  if (score >= 50) return '#F3B8A7'; // coral (warning)
  return '#C94A3E'; // red (danger)
}

export default function ScoreBadge({ score, size = 'md' }: ScoreBadgeProps) {
  const config = sizeConfig[size];
  const normalizedScore = Math.min(Math.max(score, 0), 100);
  const color = getScoreColor(normalizedScore);

  const circumference = 2 * Math.PI * config.radius;
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  return (
    <div className="inline-flex items-center justify-center">
      <div className={`relative ${config.containerSize}`}>
        {/* Background circle */}
        <svg className="transform -rotate-90 w-full h-full">
          <circle
            cx="50%"
            cy="50%"
            r={config.radius}
            stroke="#e5e7eb"
            strokeWidth={config.strokeWidth}
            fill="none"
          />
          {/* Progress circle */}
          <circle
            cx="50%"
            cy="50%"
            r={config.radius}
            stroke={color}
            strokeWidth={config.strokeWidth}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-500 ease-out"
          />
        </svg>

        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="flex items-baseline">
            <span className={`font-heading font-bold ${config.textSize}`} style={{ color }}>
              {normalizedScore}
            </span>
            <span className={`font-medium text-muted ml-0.5 ${config.subtextSize}`}>
              /100
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
