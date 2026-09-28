import { Scale, ShieldAlert } from 'lucide-react'

import { Alert } from '../ui/Alert'
import { LEGAL_DISCLAIMER, LEGAL_DISCLAIMER_SHORT } from '../../constants/legal'
import { cn } from '../../utils/cn'

/** Full disclaimer block. Used on the landing page, wizard and templates. */
export function LegalDisclaimer({
  className,
  title = 'Important: not legal advice',
  text = LEGAL_DISCLAIMER,
}: {
  className?: string
  title?: string
  text?: string
}) {
  return (
    <Alert className={className} variant="warning" title={title}>
      <span className="text-amber-50/90">{text}</span>
    </Alert>
  )
}

/** Compact inline note. Used in the editor toolbar and export menus. */
export function LegalDisclaimerInline({ className }: { className?: string }) {
  return (
    <p
      className={cn(
        'flex items-start gap-2 text-xs leading-relaxed text-ivory-300/55',
        className,
      )}
    >
      <Scale className="mt-0.5 size-3.5 shrink-0" aria-hidden />
      <span>{LEGAL_DISCLAIMER_SHORT}</span>
    </p>
  )
}

/** Blocking acknowledgement the user must tick before generating. */
export function DisclaimerAcknowledgement({
  checked,
  onChange,
  className,
  id = 'disclaimer-acknowledgement',
}: {
  checked: boolean
  onChange: (value: boolean) => void
  className?: string
  id?: string
}) {
  return (
    <label
      htmlFor={id}
      className={cn(
        'flex cursor-pointer items-start gap-3 rounded-xl border p-4 transition-colors',
        checked
          ? 'border-gold-500/40 bg-gold-500/8'
          : 'border-navy-600 bg-navy-850/50 hover:border-navy-500',
        className,
      )}
    >
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
        className="peer sr-only"
      />
      <span
        aria-hidden
        className={cn(
          'mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-md border transition-all',
          'peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-gold-400',
          checked
            ? 'border-gold-400 bg-gold-500 text-navy-950'
            : 'border-navy-500 bg-navy-900',
        )}
      >
        {checked ? (
          <svg viewBox="0 0 16 16" className="size-3.5" fill="none" stroke="currentColor" strokeWidth="2.4">
            <path d="M3.5 8.5l3 3 6-6.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        ) : null}
      </span>
      <span className="text-xs leading-relaxed text-ivory-200/80">
        <span className="mb-0.5 flex items-center gap-1.5 font-medium text-amber-200">
          <ShieldAlert className="size-3.5" aria-hidden />
          {LEGAL_DISCLAIMER_SHORT}
        </span>
        I understand this document is a starting point generated with AI assistance, and I will
        have it reviewed by a qualified legal professional before relying on it.
      </span>
    </label>
  )
}
