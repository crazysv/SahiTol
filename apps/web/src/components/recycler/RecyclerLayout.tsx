import React from 'react';
import { NavLink, Outlet, Link } from 'react-router-dom';

export default function RecyclerLayout() {
  const navItems = [
    { to: '/recycler', label: 'Inbox', end: true },
    { to: '/recycler/incoming', label: 'Incoming Lot' },
    { to: '/recycler/quote', label: 'Quote Terminal' },
    { to: '/recycler/scan', label: 'QR Scan' },
    { to: '/recycler/profile', label: 'Operational Profile' },
    { to: '/recycler/history', label: 'History & Exports' },
  ];

  return (
    <div className="min-h-screen bg-surface font-body text-on-surface">
      {/* Top Fixed Header */}
      <header className="fixed top-0 w-full z-50 bg-surface/90 backdrop-blur-xl border-b border-surface-container-high shadow-[0_1px_8px_rgba(0,0,0,0.04)]">
        <div className="h-16 max-w-7xl mx-auto px-gutter flex items-center justify-between">
          <div className="flex items-center gap-space-md">
            <Link to="/" className="flex items-center gap-2 group">
              <span className="material-symbols-outlined text-primary text-[28px] group-hover:scale-105 transition-transform" style={{ fontVariationSettings: "'FILL' 1" }}>
                scale
              </span>
              <div>
                <h1 className="text-label-lg font-headline font-bold text-on-surface">SahiTol Recycler</h1>
                <p className="text-label-sm text-on-surface-variant">Yard #402 - Okhla Industrial</p>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-space-xs">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `px-space-md py-space-sm rounded-lg text-sm font-headline transition-colors ${
                    isActive
                      ? 'bg-primary text-on-primary font-bold shadow-sm'
                      : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          {/* Header Action Items */}
          <div className="flex items-center gap-space-md">
            <button
              title="Notifications"
              className="relative p-space-sm rounded-full hover:bg-surface-container-high transition-colors"
            >
              <span className="material-symbols-outlined text-on-surface-variant text-[20px]">notifications</span>
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-primary ring-2 ring-surface"></span>
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-on-primary font-bold text-xs shadow-sm">
                VE
              </div>
              <span className="hidden sm:inline text-xs font-semibold text-on-surface">Verma Electricals</span>
            </div>
          </div>
        </div>

        {/* Mobile Horizontal Scroll Navigation */}
        <nav className="md:hidden flex overflow-x-auto px-gutter py-space-sm gap-space-sm bg-surface-container-low border-t border-surface-container">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `whitespace-nowrap px-space-md py-space-xs rounded-lg text-xs font-headline transition-colors ${
                  isActive
                    ? 'bg-primary text-on-primary font-bold'
                    : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      {/* Main Content Area */}
      <main className="w-full pt-20 md:pt-24 pb-space-xl max-w-7xl mx-auto px-gutter">
        <Outlet />
      </main>
    </div>
  );
}
