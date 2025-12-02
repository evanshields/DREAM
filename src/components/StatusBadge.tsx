type Variant = 'default' | 'success' | 'warning' | 'danger' | 'info';

interface StatusBadgeProps {
  status: string;
  variant?: Variant;
}

const variantStyles = {
  default: 'bg-secondary-gray/10 text-secondary-gray border-secondary-gray/20',
  success: 'bg-success/10 text-success border-success/20',
  warning: 'bg-warning/10 text-warning border-warning/20',
  danger: 'bg-danger/10 text-danger border-danger/20',
  info: 'bg-info/10 text-info border-info/20',
};

export default function StatusBadge({
  status,
  variant = 'default',
}: StatusBadgeProps) {
  return (
    <span
      className={`
        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border
        ${variantStyles[variant]}
      `}
    >
      {status}
    </span>
  );
}
