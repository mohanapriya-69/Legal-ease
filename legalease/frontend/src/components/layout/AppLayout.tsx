import { motion } from 'framer-motion'
import { NavLink, Outlet, useLocation } from 'react-router-dom'

import { Logo } from './Logo'
import { AiModePill } from './AiStatusBanner'
import { cn } from '../../utils/cn'

/** App chrome used by the dashboard, templates and wizard: nav + no footer. */
export function AppLayout() {
  const location = useLocation()

  // The editor manages its own toolbar and must not sit under the nav.
  if (location.pathname.startsWith('/editor') || location.pathname.startsWith('/document/')) {
    return <Outlet />
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <AppHeader />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6 lg:px-8">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.32, ease: [0.22, 1, 0.36, 1] }}
        >
          <Outlet />
        </motion.div>
      </main>
    </div>
  )
}

function AppHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-navy-700/70 bg-navy-950/85 backdrop-blur-xl">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <Logo />
        <nav className="flex items-center gap-1.5" aria-label="App">
          {[
            { to: '/dashboard', label: 'Documents' },
            { to: '/templates', label: 'Templates' },
          ].map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  'hidden rounded-lg px-3 py-1.5 text-sm font-medium transition-colors sm:block',
                  isActive ? 'text-gold-300' : 'text-ivory-200/70 hover:text-ivory-50',
                )
              }
            >
              {item.label}
            </NavLink>
          ))}
          <AiModePill />
        </nav>
      </div>
    </header>
  )
}
