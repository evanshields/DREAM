import React, { useState, useEffect } from 'react';
import type { ViewState } from './types';
import { Layout } from './components/Layout';
import Dashboard from './pages/Dashboard';
import AnalysisView from './pages/AnalysisView';
import PipelineBoard from './pages/PipelineBoard';
import DealIntake from './pages/DealIntake';
import SalesFunnel from './pages/SalesFunnel';

const App: React.FC = () => {
  const [view, setView] = useState<ViewState>('landing'); // Default to landing page

  // Hash router simulation
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);
      if (hash && ['dashboard', 'analysis', 'pipeline', 'intake', 'landing'].includes(hash)) {
        setView(hash as ViewState);
      }
    };
    
    // Set initial hash if empty - default to landing
    if (!window.location.hash) {
      window.location.hash = 'landing';
    }

    window.addEventListener('hashchange', handleHashChange);
    handleHashChange(); // Initial check

    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const navigate = (newView: ViewState) => {
    window.location.hash = newView;
    setView(newView);
  };

  // Landing page renders without the Layout wrapper for full-width design
  if (view === 'landing') {
    return <SalesFunnel onGetStarted={() => navigate('dashboard')} />;
  }

  return (
    <Layout activeView={view} onNavigate={navigate}>
      {view === 'dashboard' && <Dashboard onNavigate={navigate} />}
      {view === 'analysis' && <AnalysisView />}
      {view === 'pipeline' && <PipelineBoard />}
      {view === 'intake' && <DealIntake onComplete={() => navigate('analysis')} />}
    </Layout>
  );
};

export default App;
