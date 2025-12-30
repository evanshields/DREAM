import React from 'react';

interface GlassButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
}

export const GlassButton: React.FC<GlassButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  onClick,
  className = '',
  disabled = false,
  type = 'button',
}) => {
  const sizeClasses = {
    sm: 'px-4 py-1.5 text-xs',
    md: 'px-6 py-2 text-sm',
    lg: 'px-8 py-3 text-base',
  };

  const variantClasses = {
    primary: `
      bg-gradient-to-br from-chart-2 to-chart-2/80
      hover:from-chart-2/90 hover:to-chart-2/70
      text-primary-foreground
      border border-primary-foreground/30
      shadow-lg hover:shadow-xl
    `,
    secondary: `
      bg-card/70 hover:bg-card/85
      border-2 border-chart-2/40 hover:border-chart-2/60
      text-chart-2
      backdrop-blur-md
      dark:bg-card/70 dark:hover:bg-card/85
    `,
    outline: `
      bg-transparent hover:bg-card/10
      border-2 border-chart-2
      text-chart-2
      dark:hover:bg-card/5
    `,
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        rounded-full
        font-medium
        transition-all duration-300
        hover:translate-y-[-2px]
        disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0
        ${className}
      `}
    >
      {children}
    </button>
  );
};
