import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { RequireAuth } from './auth/RequireAuth';
import { AppShell } from './components/AppShell';
import { Login } from './pages/Login';
import { Pipeline } from './pages/Pipeline';
import { Underwrite } from './pages/Underwrite';
import { DealDetail } from './pages/DealDetail';

// Routes: /login (public) · /pipeline · /underwrite · /deal/:id (all gated).
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
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
      </AuthProvider>
    </BrowserRouter>
  );
}
