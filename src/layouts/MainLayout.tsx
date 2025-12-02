import { Outlet, Link, useLocation } from 'react-router-dom';
import { Home, Layers, Settings } from 'lucide-react';

export default function MainLayout() {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/pipeline', icon: Layers, label: 'Pipeline' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="flex h-screen bg-background-primary">
      {/* Sidebar */}
      <aside className="w-64 bg-gradient-to-b from-primary to-primary-teal border-r border-secondary-tan flex flex-col shadow-lg">
        {/* Logo/Brand */}
        <div className="p-8 border-b border-white/10">
          <h1 className="text-2xl font-heading font-semibold text-white">
            DreamVision
          </h1>
          <p className="text-sm text-secondary-blue mt-2">Real Estate Intelligence</p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`flex items-center gap-4 px-4 py-3 rounded-lg transition-all ${
                      isActive
                        ? 'bg-primary-seafoam text-white shadow-md'
                        : 'text-secondary-tan hover:bg-white/10 hover:text-white'
                    }`}
                  >
                    <Icon size={20} />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-white/10">
          <p className="text-xs text-secondary-tan text-center">
            © 2025 Shieldstone
          </p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
