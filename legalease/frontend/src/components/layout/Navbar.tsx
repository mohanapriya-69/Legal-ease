import { AnimatePresence, motion } from 'framer-motion'
import { FileText, LayoutTemplate, Menu, PenLine, Sparkles, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, NavLink } from 'react-router-dom'

import { Button } from '../ui/Button'
import { Logo } from './Logo'
import { cn } from '../../utils/cn'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: FileText },
  { to: '/templates', label: 'Templates', icon: LayoutTemplate },
  { to: '/create', label: 'New document', icon: Sparkles },
  { to: '/editor', label: 'Editor', icon: PenLine },
] as const

export function Navbar() {
  const [scrolled, setScrolled] = useState(() => window.scrollY > 8)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    if (!mobileOpen) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMobileOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [mobileOpen])

  return (
    <header
      className={cn(
        'sticky top-0 z-40 transition-all duration-300',
        scrolled
          ? 'border-b border-navy-700/70 bg-navy-950/85 backdrop-blur-xl'
          : 'border-b border-transparent bg-transparent',
      )}
    >
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <Logo />

        <nav className="hidden items-center gap-1 lg:flex" aria-label="Main">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  'relative rounded-lg px-3.5 py-2 text-sm font-medium transition-colors duration-200',
                  isActive
                    ? 'text-gold-300'
                    : 'text-ivory-200/75 hover:text-ivory-50',
                )
              }
            >
              {({ isActive }) => (
                <>
                  {isActive ? (
                    <motion.span
                      layoutId="nav-active"
                      className="absolute inset-0 rounded-lg border border-gold-500/25 bg-gold-500/10"
                      transition={{ type: 'spring', stiffness: 420, damping: 34 }}
                    />
                  ) : null}
                  <span className="relative">{item.label}</span>
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="hidden items-center gap-3 lg:flex">
          <Button asChild size="sm" variant="ghost">
            <Link to="/templates">Browse templates</Link>
          </Button>
          <Button asChild size="sm">
            <Link to="/create">
              <Sparkles aria-hidden />
              Draft a document
            </Link>
          </Button>
        </div>

        <Button
          className="lg:hidden"
          size="icon-sm"
          variant="ghost"
          aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={mobileOpen}
          onClick={() => setMobileOpen((v) => !v)}
        >
          {mobileOpen ? <X aria-hidden /> : <Menu aria-hidden />}
        </Button>
      </div>

      <AnimatePresence initial={false}>
        {mobileOpen ? (
          <motion.div
            key="mobile-nav"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.24, ease: [0.22, 1, 0.36, 1] }}
            className="overflow-hidden border-t border-navy-700/60 bg-navy-950/95 backdrop-blur-xl lg:hidden"
          >
            <nav className="flex flex-col gap-1 p-4" aria-label="Mobile">
              {NAV_ITEMS.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={() => setMobileOpen(false)}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                      isActive
                        ? 'border border-gold-500/25 bg-gold-500/10 text-gold-300'
                        : 'text-ivory-200/80 hover:bg-navy-800/70 hover:text-ivory-50',
                    )
                  }
                >
                  <item.icon className="size-4" aria-hidden />
                  {item.label}
                </NavLink>
              ))}
              <Button asChild className="mt-2" size="md" onClick={() => setMobileOpen(false)}>
                <Link to="/create">
                  <Sparkles aria-hidden />
                  Draft a document
                </Link>
              </Button>
            </nav>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </header>
  )
}
