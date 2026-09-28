import { motion, useReducedMotion } from 'framer-motion'
import { Link } from 'react-router-dom'

import { cn } from '../../utils/cn'

/** The LegalEase wordmark. Uses the display serif for a legal-tech feel. */
export function Logo({
  className,
  compact = false,
  linkTo = '/',
}: {
  className?: string
  compact?: boolean
  linkTo?: string | null
}) {
  const reduce = useReducedMotion()

  const mark = (
    <span className={cn('group inline-flex items-center gap-2.5', className)}>
      <span className="relative flex size-9 shrink-0 items-center justify-center overflow-hidden rounded-[0.6rem] border border-gold-500/30 bg-gradient-to-br from-navy-700 to-navy-850 shadow-[0_1px_0_0_rgba(232,199,127,0.18)_inset]">
        <svg
          viewBox="0 0 24 24"
          className="size-[1.15rem] text-gold-400"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden
        >
          <path d="M6 2.75h8.5L19 7.4V21.25H6z" />
          <path d="M14 2.75V7.5h5" />
          <path d="M9 12.5h6M9 16h4.5" />
        </svg>
        <span
          className={cn(
            'absolute inset-0 bg-gradient-to-tr from-gold-400/0 via-gold-300/18 to-gold-400/0',
            !reduce && 'opacity-0 transition-opacity duration-500 group-hover:opacity-100',
          )}
          aria-hidden
        />
      </span>
      {!compact ? (
        <span className="flex flex-col leading-none">
          <span className="font-display text-[1.0625rem] font-semibold tracking-tight text-ivory-50">
            Legal<span className="text-gold-400">Ease</span>
          </span>
          <span className="mt-0.5 text-[0.5625rem] font-medium tracking-[0.22em] text-ivory-300/50 uppercase">
            AI Legal Drafting
          </span>
        </span>
      ) : null}
    </span>
  )

  if (!linkTo) return mark

  return (
    <Link
      to={linkTo}
      className="rounded-lg focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-gold-400"
      aria-label="LegalEase home"
    >
      {mark}
    </Link>
  )
}

/** Small animated gold rule used under section headings. */
export function GoldRule({ className }: { className?: string }) {
  return (
    <motion.span
      className={cn('block h-px w-14 origin-left bg-gradient-to-r from-gold-400 to-transparent', className)}
      initial={{ scaleX: 0 }}
      whileInView={{ scaleX: 1 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      aria-hidden
    />
  )
}
