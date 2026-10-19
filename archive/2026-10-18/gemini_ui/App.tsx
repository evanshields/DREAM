import React, { useState, useEffect } from 'react';
import { ViewState } from './types';
import { Layout } from './components/Layout';
import Dashboard from './pages/Dashboard';
import AnalysisView from './pages/AnalysisView';
import AssumptionDashboard from './pages/AssumptionDashboard';
import PipelineBoard from './pages/PipelineBoard';
import DealIntake from './pages/DealIntake';

const App: React.FC = () => {
  const [view, setView] = useState<ViewState>('analysis'); // Default to analysis as requested by prompt priority

  // Hash router simulation
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);
      if (hash && ['dashboard', 'analysis', 'assumptions', 'pipeline', 'intake'].includes(hash)) {
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

  return (
    <Layout activeView={view} onNavigate={navigate}>
      {view === 'dashboard' && <Dashboard onNavigate={navigate} />}
      {view === 'analysis' && <AnalysisView />}
      {view === 'assumptions' && <AssumptionDashboard />}
      {view === 'pipeline' && <PipelineBoard />}
      {view === 'intake' && <DealIntake onComplete={() => navigate('analysis')} />}
    </Layout>
  );
};

export default App;
