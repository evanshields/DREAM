import React from 'react';

interface GlassMetricProps {
  label: string;
  value: string | number;
  subtext?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

export const GlassMetric: React.FC<GlassMetricProps> = ({
  label,
  value,
  subtext,
  trend,
  trendValue,
  variant = 'default',
  className = '',
}) => {
  const variantGradient = {
    default: 'from-chart-2 to-chart-1',
    success: 'from-chart-5 to-chart-1',
    warning: 'from-chart-4 to-chart-4/80',
    danger: 'from-destructive to-destructive/80',
    info: 'from-chart-2 to-chart-1',
  };

  const trendColor = {
    up: 'text-chart-5',
    down: 'text-destructive',
    neutral: 'text-muted-foreground',
  };

  return (
    <div
      className={`
        bg-card/70 hover:bg-card/80
        backdrop-blur-lg
        border border-border/40
        rounded-3xl
        p-6
        transition-all duration-300
        hover:shadow-xl hover:-translate-y-1
        dark:bg-card/70 dark:hover:bg-card/80
        dark:border-border/20 dark:hover:border-border/30
        ${className}
      `}
    >
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-medium text-muted-foreground">
          {label}
        </p>
        {trend && trendValue && (
          <span className={`text-xs font-semibold ${trendColor[trend]}`}>
            {trend === 'up' && '↑'} {trend === 'down' && '↓'} {trendValue}
          </span>
        )}
      </div>

      <p
        className={`
          text-5xl font-display font-bold
          bg-gradient-to-r ${variantGradient[variant]}
          bg-clip-text text-transparent
          mb-1 font-tabular-nums
        `}
      >
        {value}
      </p>

      {subtext && (
        <p className="text-sm text-muted-foreground">
          {subtext}
        </p>
      )}
    </div>
  );
};
