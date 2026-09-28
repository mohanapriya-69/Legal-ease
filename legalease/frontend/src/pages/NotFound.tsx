import { Compass, Home, LayoutTemplate } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Logo } from '../components/layout/Logo'
import { Button } from '../components/ui/Button'

export function NotFound() {
  return (
    <div className="flex min-h-dvh flex-col">
      <header className="border-b border-navy-700/60">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <Logo />
        </div>
      </header>

      <main className="flex flex-1 items-center justify-center px-6 py-20">
        <div className="w-full max-w-lg text-center">
          <div className="mb-6 flex justify-center">
            <div className="flex size-16 items-center justify-center rounded-2xl border border-gold-500/25 bg-navy-850">
              <Compass className="size-7 text-gold-400" aria-hidden />
            </div>
          </div>
          <p className="font-mono text-xs tracking-[0.3em] text-gold-400/80">ERROR 404</p>
          <h1 className="mt-3 font-display text-3xl font-semibold tracking-tight text-ivory-50">
            This page does not exist
          </h1>
          <p className="mt-3 text-sm leading-relaxed text-ivory-300/65">
            The link may be out of date, or the document may have been deleted from the
            database.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Button asChild>
              <Link to="/">
                <Home aria-hidden />
                Back to home
              </Link>
            </Button>
            <Button asChild variant="outline">
              <Link to="/templates">
                <LayoutTemplate aria-hidden />
                Browse templates
              </Link>
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}
