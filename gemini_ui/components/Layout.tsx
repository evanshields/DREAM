import React, { useState, useEffect } from 'react';
import { ViewState } from '../types';
import { LayoutDashboard, Trello, FileText, SlidersHorizontal, Upload, Bell, Search, Moon, Sun } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  activeView: ViewState;
  onNavigate: (view: ViewState) => void;
}

export const Layout: React.FC<LayoutProps> = ({ children, activeView, onNavigate }) => {
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
    { id: 'assumptions', label: 'Assumptions', icon: SlidersHorizontal },
    { id: 'intake', label: 'Upload Deal', icon: Upload },
  ];

  return (
    <div className="min-h-screen bg-background-secondary flex flex-col transition-colors duration-200">
      {/* Top Navigation Bar - Deep Teal in Light Mode, YinMn Blue in Dark Mode */}
      <header className="bg-[#005253] dark:bg-[#2B52EF] border-b border-white/10 sticky top-0 z-30 transition-colors duration-200 shadow-md">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center cursor-pointer" onClick={() => onNavigate('dashboard')}>
                {/* Logo Box - White with adaptive text color */}
                <div className="h-8 w-8 bg-white rounded flex items-center justify-center mr-2 shadow-sm">
                  <span className="text-[#005253] dark:text-[#2B52EF] font-serif font-bold text-lg">D</span>
                </div>
                <span className="font-serif font-bold text-xl text-white tracking-tight">DREAM.ai</span>
              </div>
              <nav className="hidden sm:ml-10 sm:flex sm:space-x-8">
                {navItems.map((item) => {
                  const isActive = activeView === item.id;
                  const Icon = item.icon;
                  return (
                    <button
                      key={item.id}
                      onClick={() => onNavigate(item.id as ViewState)}
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                        isActive
                          ? 'border-white text-white'
                          : 'border-transparent text-white/70 hover:text-white hover:border-white/50'
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
                  <Search className="h-4 w-4 text-white/60" />
                </div>
                {/* Search Input - Semi-transparent white for contrast on both Teal and Blue */}
                <input
                  type="text"
                  className="block w-64 pl-10 pr-3 py-1.5 border border-white/20 rounded-md leading-5 bg-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-1 focus:ring-white focus:bg-white/20 sm:text-sm transition-colors"
                  placeholder="Search deals, markets..."
                />
              </div>
              
              <button 
                onClick={() => setIsDark(!isDark)}
                className="p-1 rounded-full text-white/80 hover:text-white focus:outline-none hover:bg-white/10 transition-colors"
                title="Toggle Dark Mode"
              >
                {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </button>

              <button className="p-1 rounded-full text-white/80 hover:text-white focus:outline-none hover:bg-white/10 transition-colors">
                <Bell className="h-5 w-5" />
              </button>
              
              <div className="ml-3 relative flex items-center space-x-2 cursor-pointer">
                {/* Avatar - Adaptive text color */}
                <div className="h-8 w-8 rounded-full bg-white text-[#005253] dark:text-[#2B52EF] text-xs font-medium flex items-center justify-center border-2 border-white/20">
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