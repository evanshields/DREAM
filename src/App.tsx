import React, { useState, useEffect } from 'react';
import type { ViewState } from './types';
import { useTheme } from './context/ThemeContext';
import { Layout } from './components/Layout';
import { GlassLayout } from './components/glassmorphism';
import Dashboard from './pages/Dashboard';
import AnalysisView from './pages/AnalysisView';
import PipelineBoard from './pages/PipelineBoard';
import DealIntake from './pages/DealIntake';

const App: React.FC = () => {
  const [view, setView] = useState<ViewState>('analysis'); // Default to analysis as requested by prompt priority
  const { theme } = useTheme();

  // Hash router simulation
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);
      if (hash && ['dashboard', 'analysis', 'pipeline', 'intake'].includes(hash)) {
        setView(hash as ViewState);
      }
    };

    // Set initial hash if empty
    if (!window.location.hash) {
      window.location.hash = 'analysis';
    }

    window.addEventListener('hashchange', handleHashChange);
    handleHashChange(); // Initial check

    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const navigate = (newView: ViewState) => {
    window.location.hash = newView;
    setView(newView);
  };

  // Choose layout based on theme
  const LayoutComponent = theme === 'glassmorphism' ? GlassLayout : Layout;

  return (
    <LayoutComponent activeView={view} onNavigate={navigate}>
      {view === 'dashboard' && <Dashboard onNavigate={navigate} />}
      {view === 'analysis' && <AnalysisView />}
      {view === 'pipeline' && <PipelineBoard />}
      {view === 'intake' && <DealIntake onComplete={() => navigate('analysis')} />}
    </LayoutComponent>
  );
};

export default App;
