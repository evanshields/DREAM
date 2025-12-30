import React from 'react';
import { useTheme } from '../../context/ThemeContext';

export const ThemeSwitcher: React.FC = () => {
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex items-center gap-2 bg-card/70 dark:bg-card/70 backdrop-blur-lg border border-border/30 dark:border-border/20 rounded-full p-1 ml-auto">
      <button
        onClick={() => setTheme('minimal-pro')}
        className={`
          px-4 py-1.5 rounded-full text-sm font-medium transition-all
          ${
            theme === 'minimal-pro'
              ? 'bg-card shadow-md text-foreground'
              : 'text-muted-foreground hover:text-foreground'
          }
        `}
      >
        Minimal Pro
      </button>
      <button
        onClick={() => setTheme('glassmorphism')}
        className={`
          px-4 py-1.5 rounded-full text-sm font-medium transition-all
          ${
            theme === 'glassmorphism'
              ? 'bg-gradient-to-r from-chart-2 to-chart-2/80 shadow-lg text-primary-foreground'
              : 'text-muted-foreground hover:text-foreground'
          }
        `}
      >
        Glassmorphism
      </button>
    </div>
  );
};
