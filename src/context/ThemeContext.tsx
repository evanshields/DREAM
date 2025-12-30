import React, { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

type Theme = 'minimal-pro' | 'glassmorphism';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>(() => {
    // Get theme from localStorage or default to minimal-pro
    const saved = localStorage.getItem('dream-theme');
    return (saved as Theme) || 'minimal-pro';
  });

  const handleSetTheme = (newTheme: Theme) => {
    setTheme(newTheme);
    localStorage.setItem('dream-theme', newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme: handleSetTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
