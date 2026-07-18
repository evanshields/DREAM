import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import { RequireAuth } from './auth/RequireAuth';
import { AppShell } from './components/AppShell';
import { Login } from './pages/Login';
import { Pipeline } from './pages/Pipeline';
import { Underwrite } from './pages/Underwrite';
import { DealDetail } from './pages/DealDetail';
import { BondScreen } from './pages/BondScreen';

// Routes: /login (public) · /pipeline · /underwrite · /bond-screen · /deal/:id (all gated).
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            path="/pipeline"
            element={
              <RequireAuth>
                <AppShell>
                  <Pipeline />
                </AppShell>
              </RequireAuth>
            }
          />
          <Route
            path="/underwrite"
            element={
              <RequireAuth>
                <AppShell>
                  <Underwrite />
                </AppShell>
              </RequireAuth>
            }
          />
          <Route
            path="/bond-screen"
            element={
              <RequireAuth>
                <AppShell>
                  <BondScreen />
                </AppShell>
              </RequireAuth>
            }
          />
          <Route
            path="/deal/:id"
            element={
              <RequireAuth>
                <AppShell>
                  <DealDetail />
                </AppShell>
              </RequireAuth>
            }
          />

          {/* default + catch-all -> pipeline (RequireAuth bounces to /login if unauthed) */}
          <Route path="/" element={<Navigate to="/pipeline" replace />} />
          <Route path="*" element={<Navigate to="/pipeline" replace />} />
        </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
