import React from 'react';
import { NavLink, Outlet, Link, useLocation } from 'react-router-dom';

const navItems = [
  { name: 'Overview', path: '/admin/overview', screenId: 'A01' },
  { name: 'Collectors', path: '/admin/collectors', screenId: 'A02' },
  { name: 'Facilities', path: '/admin/facilities', screenId: 'A03' },
  { name: 'Catalog & Prices', path: '/admin/catalog', screenId: 'A04' },
  { name: 'Traceability', path: '/admin/traceability', screenId: 'A05' },
  { name: 'Quality Review', path: '/admin/quality', screenId: 'A06' },
  { name: 'Research & Evidence', path: '/admin/evidence', screenId: 'A07' },
];

export default function AdminLayout() {
  const location = useLocation();

  return (
    <div className="bg-surface font-body-md text-on-surface min-h-screen flex flex-col">
      {/* Top Fixed Header from Stitch A01-A07 */}
      <header className="fixed top-0 w-full z-50 bg-surface/90 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)] border-b border-surface-container-high">
        <div className="h-20 max-w-7xl mx-auto px-gutter flex items-center justify-between">
          <div className="flex items-center gap-space-lg">
            <Link to="/" className="flex items-center gap-2 group">
              <span className="material-symbols-outlined text-primary text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>
                shield_person
              </span>
              <span className="text-headline-md font-headline-md text-primary tracking-tight">SahiTol</span>
              <span className="ml-1 px-2 py-0.5 text-[11px] font-bold bg-primary-fixed text-on-primary-fixed rounded uppercase">
                Admin
              </span>
            </Link>

            <nav className="hidden lg:flex items-center gap-space-sm">
              {navItems.map((item) => {
                const isActive =
                  location.pathname === item.path ||
                  (item.path === '/admin/overview' && location.pathname === '/admin');

                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={`px-3 py-2 text-label-md transition-colors rounded-xl flex items-center gap-1.5 ${
                      isActive
                        ? 'bg-primary text-on-primary font-bold shadow-sm'
                        : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
                    }`}
                  >
                    <span>{item.name}</span>
                    <span className={`text-[10px] px-1 py-0.2 rounded font-mono ${isActive ? 'bg-white/20 text-white' : 'bg-surface-container text-on-surface-variant'}`}>
                      {item.screenId}
                    </span>
                  </NavLink>
                );
              })}
            </nav>
          </div>

          <div className="flex items-center gap-space-md">
            <Link
              to="/"
              className="text-body-sm text-on-surface-variant hover:text-primary transition-colors flex items-center gap-1"
            >
              <span className="material-symbols-outlined text-[18px]">home</span>
              <span className="hidden sm:inline">Portal</span>
            </Link>

            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shadow-sm">
              <span className="material-symbols-outlined text-on-primary text-[18px]">person</span>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Strip */}
        <div className="lg:hidden flex items-center gap-1 px-4 py-2 overflow-x-auto bg-surface-container-low border-t border-surface-container">
          {navItems.map((item) => {
            const isActive =
              location.pathname === item.path ||
              (item.path === '/admin/overview' && location.pathname === '/admin');

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`px-2.5 py-1 text-xs whitespace-nowrap rounded-lg font-medium transition ${
                  isActive
                    ? 'bg-primary text-on-primary font-bold'
                    : 'text-on-surface-variant hover:bg-surface-container-high'
                }`}
              >
                {item.name}
              </NavLink>
            );
          })}
        </div>
      </header>

      {/* Main Content Area */}
      <main className="w-full pt-20 lg:pt-20 flex-1 bg-surface">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="w-full bg-surface-container-low py-space-xl border-t border-surface-container-high mt-auto">
        <div className="max-w-7xl mx-auto px-gutter text-center text-on-surface-variant text-body-sm space-y-1">
          <p className="font-semibold text-on-surface">SahiTol Industrial Admin Console • Grounded Operations Platform</p>
          <p className="text-xs text-on-surface-variant">
            Strict Non-EPR & Provenance Separation • Denominator Verified Metrics • Isolated Demo Partitions
          </p>
        </div>
      </footer>
    </div>
  );
}
