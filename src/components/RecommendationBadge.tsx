type Recommendation = 'STRONG_BUY' | 'BUY' | 'HOLD' | 'PASS';
type Size = 'sm' | 'md' | 'lg';

interface RecommendationBadgeProps {
  recommendation: Recommendation;
  size?: Size;
}

const recommendationConfig = {
  STRONG_BUY: {
    label: 'Strong Buy',
    bgColor: 'bg-primary-seafoam',
    textColor: 'text-white',
  },
  BUY: {
    label: 'Buy',
    bgColor: 'bg-primary-seafoam',
    textColor: 'text-white',
  },
  HOLD: {
    label: 'Hold',
    bgColor: 'bg-warning',
    textColor: 'text-white',
  },
  PASS: {
    label: 'Pass',
    bgColor: 'bg-danger',
    textColor: 'text-white',
  },
};

const sizeClasses = {
  sm: 'px-3 py-1 text-xs',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-xl font-semibold',
};

export default function RecommendationBadge({
  recommendation,
  size = 'md',
}: RecommendationBadgeProps) {
  const config = recommendationConfig[recommendation];

  return (
    <div
      className={`
        inline-flex items-center justify-center rounded-lg font-heading
        ${config.bgColor} ${config.textColor} ${sizeClasses[size]}
        ${size === 'lg' ? 'shadow-lg' : 'shadow-sm'}
        transition-all hover:scale-105
      `}
    >
      {config.label}
    </div>
  );
}
