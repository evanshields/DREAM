import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { LogIn, Loader2, ShieldCheck } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';
import { login as apiLogin, ApiError } from '../lib/api';
import { Button, Input } from '../components/ui';
import { Wordmark } from '../components/Wordmark';

const GOOGLE_CLIENT_ID =
  '954847212741-g00fssf9sa9mvglus6b61cc61pt3f7hj.apps.googleusercontent.com';

// Minimal typing for the GSI global we consume.
interface GoogleCredentialResponse {
  credential: string;
}
interface GoogleId {
  initialize: (cfg: {
    client_id: string;
    callback: (r: GoogleCredentialResponse) => void;
  }) => void;
  renderButton: (el: HTMLElement, opts: Record<string, unknown>) => void;
}
declare global {
  interface Window {
    google?: { accounts?: { id?: GoogleId } };
  }
}

export function Login() {
  const { token, ready, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from ?? '/pipeline';

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const googleBtnRef = useRef<HTMLDivElement>(null);

  // Already signed in → skip the gate.
  useEffect(() => {
    if (ready && token) navigate(from, { replace: true });
  }, [ready, token, from, navigate]);

  const finishLogin = useCallback(
    async (jwt: string, email?: string) => {
      await login(jwt, email);
      navigate(from, { replace: true });
    },
    [login, navigate, from],
  );

  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const res = await apiLogin(username.trim(), password);
      await finishLogin(res.access_token, res.email);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setError("Your account isn't authorized.");
      } else if (err instanceof ApiError && err.status === 401) {
        setError('Invalid username or password.');
      } else {
        setError(err instanceof Error ? err.message : 'Login failed. Please try again.');
      }
    } finally {
      setBusy(false);
    }
  };

  // --- Google Identity Services button ---
  const handleGoogleCredential = useCallback(
    async (resp: GoogleCredentialResponse) => {
      setError(null);
      setBusy(true);
      try {
        // The Google ID token IS the bearer (the backend's require_auth verifies it).
        await finishLogin(resp.credential);
      } catch (err) {
        if (err instanceof ApiError && err.status === 403) {
          setError("Your account isn't authorized.");
        } else {
          setError('Google sign-in failed. Use username + password.');
        }
      } finally {
        setBusy(false);
      }
    },
    [finishLogin],
  );

  useEffect(() => {
    // Poll briefly for the async GSI script, then render the official button.
    let tries = 0;
    const id = window.setInterval(() => {
      tries += 1;
      const gid = window.google?.accounts?.id;
      if (gid && googleBtnRef.current) {
        window.clearInterval(id);
        try {
          gid.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleGoogleCredential,
          });
          gid.renderButton(googleBtnRef.current, {
            theme: 'outline',
            size: 'large',
            width: 320,
            text: 'signin_with',
            shape: 'rectangular',
          });
        } catch {
          /* GSI render failed — username/password path still works */
        }
      } else if (tries > 40) {
        window.clearInterval(id); // ~10s; give up silently
      }
    }, 250);
    return () => window.clearInterval(id);
  }, [handleGoogleCredential]);

  return (
    <div className="min-h-screen bg-offwhite flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <Wordmark className="h-9 mb-3" />
          <p className="text-sm text-slate/60 font-label tracking-wide flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-teal" /> Shieldstone underwriting workspace
          </p>
        </div>

        <div className="card p-8 animate-fade">
          <h1 className="text-2xl font-head font-bold text-slate-near mb-1">Sign in</h1>
          <p className="text-sm text-slate/60 mb-6">Authorized Shieldstone access only.</p>

          <form onSubmit={handlePasswordLogin} className="space-y-4">
            <div>
              <label htmlFor="username" className="label">
                Username
              </label>
              <Input
                id="username"
                type="text"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="evan"
                required
                autoFocus
              />
            </div>
            <div>
              <label htmlFor="password" className="label">
                Password
              </label>
              <Input
                id="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            {error && (
              <div
                role="alert"
                className="text-sm text-danger bg-danger/5 border border-danger/20 rounded-lg px-3 py-2"
              >
                {error}
              </div>
            )}

            <Button type="submit" icon={busy ? undefined : LogIn} disabled={busy} className="w-full">
              {busy ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Signing in…
                </>
              ) : (
                'Sign in'
              )}
            </Button>
          </form>

          <div className="flex items-center gap-3 my-6">
            <div className="h-px bg-slate/10 flex-1" />
            <span className="text-xs text-slate/40 font-label uppercase tracking-wider">or</span>
            <div className="h-px bg-slate/10 flex-1" />
          </div>

          {/* Google Identity Services renders its button here */}
          <div className="flex justify-center">
            <div ref={googleBtnRef} />
          </div>
        </div>

        <p className="text-center text-xs text-slate/40 mt-6">
          DREAM · Dev / Real-Estate / Asset-Management
        </p>
      </div>
    </div>
  );
}
