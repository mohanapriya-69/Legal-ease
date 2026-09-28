import { Outlet } from 'react-router-dom'

import { Footer } from './Footer'
import { Navbar } from './Navbar'
import { AiStatusBanner } from './AiStatusBanner'

/** Public marketing shell: nav, ambient background, banner, footer. */
export function RootLayout() {
  return (
    <div className="relative flex min-h-dvh flex-col">
      <AmbientBackdrop />
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:rounded-lg focus:bg-gold-500 focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-navy-950"
      >
        Skip to content
      </a>
      <Navbar />
      <AiStatusBanner />
      <main id="main" className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}

/** Fixed decorative gradients. Pointer-transparent so it never blocks input. */
function AmbientBackdrop() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden" aria-hidden>
      <div className="absolute -top-40 -left-32 size-[38rem] rounded-full bg-navy-700/25 blur-3xl" />
      <div className="absolute top-1/3 -right-40 size-[34rem] rounded-full bg-gold-500/6 blur-3xl" />
      <div
        className="absolute inset-0 opacity-[0.55] [mask-image:radial-gradient(ellipse_at_50%_0%,black,transparent_75%)]"
        style={{
          backgroundImage:
            'linear-gradient(to right, rgba(232,199,127,0.045) 1px, transparent 1px), linear-gradient(to bottom, rgba(232,199,127,0.045) 1px, transparent 1px)',
          backgroundSize: '64px 64px',
        }}
      />
    </div>
  )
}
