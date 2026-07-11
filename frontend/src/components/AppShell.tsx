import { type ReactNode } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutGrid, FilePlus2, Landmark, LogOut } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';
import { Wordmark } from './Wordmark';

// The authenticated chrome: top bar (wordmark · nav · user/logout) + content slot.
export function AppShell({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const navClass = ({ isActive }: { isActive: boolean }) =>
    [
      'inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-label font-semibold transition-colors',
      isActive ? 'bg-teal-panel text-teal' : 'text-slate/70 hover:text-teal hover:bg-teal-panel/60',
    ].join(' ');

  return (
    <div className="min-h-screen bg-offwhite flex flex-col">
      <header className="sticky top-0 z-20 bg-white/90 backdrop-blur border-b border-slate/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
          <div className="flex items-center gap-6">
            <NavLink to="/pipeline" aria-label="DREAM home">
              <Wordmark className="h-7" />
            </NavLink>
            <nav className="hidden sm:flex items-center gap-1">
              <NavLink to="/pipeline" className={navClass}>
                <LayoutGrid className="w-4 h-4" /> Pipeline
              </NavLink>
              <NavLink to="/underwrite" className={navClass}>
                <FilePlus2 className="w-4 h-4" /> New Underwrite
              </NavLink>
              <NavLink to="/bond-screen" className={navClass}>
                <Landmark className="w-4 h-4" /> Bond Screen
              </NavLink>
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden md:inline text-sm text-slate/70 tnum">
              {user?.email ?? 'signed in'}
            </span>
            {user?.picture && (
              <img
                src={user.picture}
                alt=""
                className="w-8 h-8 rounded-full border border-slate/15"
                referrerPolicy="no-referrer"
              />
            )}
            <button
              onClick={handleLogout}
              className="btn-ghost"
              aria-label="Log out"
              title="Log out"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
        {/* mobile nav */}
        <nav className="sm:hidden flex items-center gap-1 px-4 pb-2">
          <NavLink to="/pipeline" className={navClass}>
            <LayoutGrid className="w-4 h-4" /> Pipeline
          </NavLink>
          <NavLink to="/underwrite" className={navClass}>
            <FilePlus2 className="w-4 h-4" /> New Underwrite
          </NavLink>
          <NavLink to="/bond-screen" className={navClass}>
            <Landmark className="w-4 h-4" /> Bond Screen
          </NavLink>
        </nav>
      </header>

      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 py-8 animate-fade">{children}</main>

      <footer className="border-t border-slate/10 py-4 text-center text-xs text-slate/50">
        DREAM · Shieldstone Dev / Real-Estate / Asset-Management underwriting
      </footer>
    </div>
  );
}
