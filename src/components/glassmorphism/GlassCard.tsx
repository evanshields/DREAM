import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({ children, className = '', hover = true }) => {
  return (
    <div
      className={`
        bg-card/75 backdrop-blur-xl
        border border-border/30
        rounded-3xl
        shadow-lg
        ${hover ? 'hover:bg-card/85 hover:shadow-xl hover:drop-shadow-lg transition-all duration-300' : ''}
        dark:bg-card/75 dark:border-border/15 dark:hover:bg-card/85
        ${className}
      `}
    >
      {children}
    </div>
  );
};
