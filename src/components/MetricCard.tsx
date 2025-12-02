import { ArrowUp, ArrowDown, Minus } from 'lucide-react';

type Trend = 'up' | 'down' | 'neutral';
type Status = 'success' | 'warning' | 'danger' | 'neutral';

interface MetricCardProps {
  label: string;
  value: string;
  subtext?: string;
  trend?: Trend;
  status?: Status;
}

const statusColors: Record<Status, string> = {
  success: 'text-success',
  warning: 'text-warning',
  danger: 'text-danger',
  neutral: 'text-primary',
};

const trendIcons = {
  up: ArrowUp,
  down: ArrowDown,
  neutral: Minus,
};

const trendColors = {
  up: 'text-success',
  down: 'text-danger',
  neutral: 'text-muted',
};

export default function MetricCard({
  label,
  value,
  subtext,
  trend,
  status = 'neutral',
}: MetricCardProps) {
  const TrendIcon = trend ? trendIcons[trend] : null;

  return (
    <div className="bg-white rounded-lg border border-border p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <p className="text-sm text-muted font-medium">{label}</p>
        {TrendIcon && (
          <TrendIcon size={16} className={trendColors[trend!]} />
        )}
      </div>
      <p className={`text-3xl font-heading font-semibold mt-2 ${statusColors[status]}`}>
        {value}
      </p>
      {subtext && (
        <p className="text-sm text-muted mt-1">{subtext}</p>
      )}
    </div>
  );
}
