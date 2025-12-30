import React from 'react';

interface GlassInputProps {
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: string;
  disabled?: boolean;
  className?: string;
  label?: string;
}

export const GlassInput: React.FC<GlassInputProps> = ({
  placeholder,
  value,
  onChange,
  type = 'text',
  disabled = false,
  className = '',
  label,
}) => {
  return (
    <div className={className}>
      {label && (
        <label className="block text-sm font-medium text-foreground mb-2">
          {label}
        </label>
      )}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        className={`
          w-full
          bg-card/60 hover:bg-card/70 focus:bg-card/80
          border border-border/40 focus:border-chart-2
          backdrop-blur-md
          rounded-lg
          px-4 py-3
          text-foreground placeholder-muted-foreground
          focus:ring-4 focus:ring-chart-2/10 focus:outline-none
          transition-all duration-300
          dark:bg-card/60 dark:hover:bg-card/70 dark:focus:bg-card/80
          dark:border-border/30 dark:focus:border-chart-2
          dark:focus:ring-chart-2/10
          disabled:opacity-50 disabled:cursor-not-allowed
        `}
      />
    </div>
  );
};
