import { type ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';
import { Loader2 } from 'lucide-react';

// Gate: redirect to /login when there's no valid token. Waits for the initial
// token-validation (auth.ready) so a refresh with a good token doesn't flash /login.
export function RequireAuth({ children }: { children: ReactNode }) {
  const { token, ready } = useAuth();
  const location = useLocation();

  if (!ready) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-offwhite">
        <Loader2 className="w-6 h-6 text-teal animate-spin" />
      </div>
    );
  }

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <>{children}</>;
}
