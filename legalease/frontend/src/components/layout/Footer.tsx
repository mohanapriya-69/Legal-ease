import { Link } from 'react-router-dom'

import { Logo } from './Logo'
import { NAV_ITEMS } from './navItems'

const TRUST_NOTES = [
  'Documents stay on this machine in a local SQLite database.',
  'AI output is a starting point, not legal advice.',
]

export function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="mt-24 border-t border-navy-700/60 bg-navy-950/60">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
        <div className="grid gap-10 md:grid-cols-[1.4fr_1fr_1fr]">
          <div className="max-w-sm">
            <Logo linkTo={null} />
            <p className="mt-4 text-sm leading-relaxed text-ivory-300/60">
              Professional legal documents, drafted in minutes instead of days. Choose a
              template, answer a few guided questions, and get an editable first draft with
              PDF, Word and plain-text export.
            </p>
          </div>

          <nav aria-label="Footer navigation">
            <h2 className="text-[0.6875rem] font-medium tracking-[0.14em] text-ivory-300/50 uppercase">
              Product
            </h2>
            <ul className="mt-4 flex flex-col gap-2.5 text-sm">
              {NAV_ITEMS.map((item) => (
                <li key={item.to}>
                  <Link
                    to={item.to}
                    className="text-ivory-200/70 transition-colors hover:text-gold-300"
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          <div>
            <h2 className="text-[0.6875rem] font-medium tracking-[0.14em] text-ivory-300/50 uppercase">
              Good to know
            </h2>
            <ul className="mt-4 flex flex-col gap-2.5 text-sm text-ivory-200/70">
              {TRUST_NOTES.map((note) => (
                <li key={note} className="leading-relaxed">
                  {note}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-12 flex flex-col gap-4 border-t border-navy-700/60 pt-6 text-xs text-ivory-300/45 sm:flex-row sm:items-center sm:justify-between">
          <p>&copy; {year} LegalEase. For professional use.</p>
          <p className="max-w-xl leading-relaxed sm:text-right">
            LegalEase is not a law firm and does not provide legal advice. Review every
            document with a qualified lawyer before relying on it.
          </p>
        </div>
      </div>
    </footer>
  )
}
