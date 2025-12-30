import React, { useState, useEffect } from 'react';
import type { ViewState } from '../../types';
import { LayoutDashboard, Trello, FileText, Upload, Bell, Search, Moon, Sun } from 'lucide-react';
import { ThemeSwitcher } from './ThemeSwitcher';

interface GlassLayoutProps {
  children: React.ReactNode;
  activeView: ViewState;
  onNavigate: (view: ViewState) => void;
}

export const GlassLayout: React.FC<GlassLayoutProps> = ({ children, activeView, onNavigate }) => {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'pipeline', label: 'Pipeline', icon: Trello },
    { id: 'analysis', label: 'Analysis', icon: FileText },
    { id: 'intake', label: 'Upload Deal', icon: Upload },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-muted to-muted/80 dark:from-background dark:to-background/90 flex flex-col transition-colors duration-200">
      {/* Top Navigation Bar - Glassmorphic */}
      <header className="bg-card/70 dark:bg-card/70 backdrop-blur-3xl border-b border-border/30 dark:border-border/15 sticky top-0 z-30 transition-colors duration-200 shadow-md">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center cursor-pointer" onClick={() => onNavigate('dashboard')}>
                {/* Logo Box - Glassmorphic */}
                <div className="h-8 w-8 bg-gradient-to-br from-chart-2 to-chart-2/80 rounded-lg flex items-center justify-center mr-2 shadow-lg backdrop-blur">
                  <span className="text-primary-foreground font-serif font-bold text-lg">D</span>
                </div>
                <span className="font-serif font-bold text-xl bg-gradient-to-r from-chart-2 to-chart-1 bg-clip-text text-transparent">
                  DREAM.ai
                </span>
              </div>
              <nav className="hidden sm:ml-10 sm:flex sm:space-x-8">
                {navItems.map((item) => {
                  const isActive = activeView === item.id;
                  const Icon = item.icon;
                  return (
                    <button
                      key={item.id}
                      onClick={() => onNavigate(item.id as ViewState)}
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-all ${
                        isActive
                          ? 'border-chart-2 text-chart-2'
                          : 'border-transparent text-muted-foreground hover:text-chart-2'
                      }`}
                    >
                      <Icon className="w-4 h-4 mr-2" />
                      {item.label}
                    </button>
                  );
                })}
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <div className="relative hidden md:block">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-4 w-4 text-muted-foreground/60" />
                </div>
                {/* Search Input - Glassmorphic */}
                <input
                  type="text"
                  className="block w-64 pl-10 pr-3 py-1.5 border border-border/30 dark:border-border/15 rounded-lg leading-5 bg-card/50 dark:bg-card/40 backdrop-blur-md text-foreground placeholder-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-chart-2/50 focus:bg-card/70 dark:focus:bg-card/60 sm:text-sm transition-all"
                  placeholder="Search deals, markets..."
                />
              </div>

              <button
                onClick={() => setIsDark(!isDark)}
                className="p-1 rounded-full text-muted-foreground/80 hover:text-chart-2 focus:outline-none hover:bg-card/20 dark:hover:bg-card/10 transition-colors"
                title="Toggle Dark Mode"
              >
                {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </button>

              <button className="p-1 rounded-full text-muted-foreground/80 hover:text-chart-2 focus:outline-none hover:bg-card/20 dark:hover:bg-card/10 transition-colors">
                <Bell className="h-5 w-5" />
              </button>

              <ThemeSwitcher />

              <div className="ml-3 relative flex items-center space-x-2 cursor-pointer">
                {/* Avatar - Glassmorphic */}
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-chart-2 to-chart-2/80 text-primary-foreground text-xs font-medium flex items-center justify-center border-2 border-border/30 dark:border-border/15 backdrop-blur">
                  JD
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </div>
      </main>
    </div>
  );
};
