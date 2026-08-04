import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
  type ReactNode,
} from 'react';
import {
  getAuthToken,
  setAuthToken,
  setUnauthorizedHandler,
  me as fetchMe,
  type MeResponse,
} from '../lib/api';

interface AuthState {
  token: string | null;
  user: MeResponse | null;
  ready: boolean; // initial token-validation finished
  login: (token: string, email?: string) => Promise<void>;
  logout: () => void;
}

const AuthCtx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getAuthToken());
  const [user, setUser] = useState<MeResponse | null>(null);
  const [ready, setReady] = useState(false);
  const loggingOut = useRef(false);

  const logout = useCallback(() => {
    loggingOut.current = true;
    setAuthToken(null);
    setToken(null);
    setUser(null);
    // RequireAuth observes token===null and redirects to /login.
    loggingOut.current = false;
  }, []);

  const login = useCallback(async (newToken: string, email?: string) => {
    setAuthToken(newToken);
    setToken(newToken);
    // Confirm + enrich identity from /api/me; tolerate a stub email fallback.
    try {
      const profile = await fetchMe();
      setUser(profile);
    } catch {
      setUser({ email: email ?? null, name: null, picture: null });
    }
  }, []);

  // Register the global 401 -> logout hook once.
  useEffect(() => {
    setUnauthorizedHandler(() => logout());
    return () => setUnauthorizedHandler(null);
  }, [logout]);

  // On app load: if a stored token still validates (GET /api/me 200), stay signed in.
  useEffect(() => {
    let cancelled = false;
    const stored = getAuthToken();
    if (!stored) {
      setReady(true);
      return;
    }
    fetchMe()
      .then((profile) => {
        if (cancelled) return;
        setUser(profile);
        setReady(true);
      })
      .catch(() => {
        if (cancelled) return;
        // invalid/expired stored token — clear it silently (401 handler also fires).
        setAuthToken(null);
        setToken(null);
        setUser(null);
        setReady(true);
      });
    return () => {
      cancelled = true;
    };
    // run once on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <AuthCtx.Provider value={{ token, user, ready, login, logout }}>{children}</AuthCtx.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthCtx);
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>');
  return ctx;
}
