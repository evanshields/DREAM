import React from 'react';
import { LucideIcon } from 'lucide-react';

// --- Button ---
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  icon?: LucideIcon;
}

export const Button: React.FC<ButtonProps> = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  className = '', 
  icon: Icon,
  ...props 
}) => {
  const baseStyles = "inline-flex items-center justify-center font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variants = {
    // Primary uses fixed Deep Teal (#005253) to maintain brand strength in dark mode
    primary: "bg-[#005253] hover:bg-[#003f3f] text-white focus:ring-[#005253] shadow-sm",
    secondary: "bg-background-primary border border-border text-secondary hover:bg-background-tertiary focus:ring-secondary",
    outline: "bg-transparent border border-border text-secondary hover:bg-background-tertiary focus:ring-secondary",
    ghost: "bg-transparent text-secondary hover:bg-background-tertiary focus:ring-gray-500",
    danger: "bg-brand-danger text-white hover:opacity-90 focus:ring-brand-danger",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base",
  };

  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`} 
      {...props}
    >
      {Icon && <Icon className="w-4 h-4 mr-2" />}
      {children}
    </button>
  );
};

// --- Badge ---
interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'outline';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'default', className = '' }) => {
  const variants = {
    default: "bg-background-tertiary text-secondary",
    success: "bg-brand-bg-success text-brand-success border border-brand-success/20",
    warning: "bg-brand-bg-warning text-brand-warning border border-brand-warning/20",
    danger: "bg-brand-bg-danger text-brand-danger border border-brand-danger/20",
    info: "bg-brand-bg-info text-brand-info border border-brand-info/20",
    outline: "bg-transparent border border-border text-secondary-muted"
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
};

// --- Card ---
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ children, className = '', ...props }) => (
  <div 
    className={`bg-background-primary rounded-lg border border-border shadow-sm ${props.onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''} ${className}`}
    {...props}
  >
    {children}
  </div>
);

// --- Inputs ---
export const Input: React.FC<React.InputHTMLAttributes<HTMLInputElement>> = (props) => (
  <input 
    className="flex h-10 w-full rounded-md border border-border bg-background-primary px-3 py-2 text-sm text-secondary placeholder:text-secondary-muted focus:outline-none focus:ring-2 focus:ring-[#005253] focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50"
    {...props} 
  />
);

// --- Circular Progress ---
export const CircularProgress: React.FC<{ value: number; size?: number; strokeWidth?: number }> = ({ 
  value, 
  size = 80, 
  strokeWidth = 8 
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (value / 100) * circumference;
  
  // Color based on value
  let colorClass = "text-brand-success";
  if (value < 60) colorClass = "text-brand-danger";
  else if (value < 80) colorClass = "text-brand-warning";

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg className="transform -rotate-90" width={size} height={size}>
        <circle
          className="text-gray-200 dark:text-gray-700"
          strokeWidth={strokeWidth}
          stroke="currentColor"
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
        <circle
          className={`${colorClass} transition-all duration-1000 ease-out`}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          stroke="currentColor"
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center text-secondary">
        <span className="text-2xl font-bold font-heading">{value}</span>
      </div>
    </div>
  );
};