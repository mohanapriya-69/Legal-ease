import { AlertTriangle, Bot, Sparkles, WifiOff, X } from 'lucide-react'
import { useState } from 'react'

import { useAiStatus } from '../../hooks/useAiStatus'
import { cn } from '../../utils/cn'

/**
 * Tells the user, honestly, whether a real model answered. It is easy to
 * forget which mode produced a document, so this is always visible.
 */
export function AiStatusBanner() {
  const { isUnavailable, isLive, status, isError } = useAiStatus()
  const [dismissed, setDismissed] = useState(false)

  if (dismissed) return null
  if (isLive) return null

  const tone = isUnavailable || isError ? 'border-rose-500/30 bg-rose-500/8' : 'border-amber-500/30 bg-amber-500/8'
  const Icon = isUnavailable || isError ? WifiOff : Bot
  const message = isError
    ? 'Cannot reach the LegalEase API on port 8000. Start it with uvicorn app.main:app --reload.'
    : (status.message ??
      'Demo mode: no live AI model is configured, so documents use a realistic built-in template. Add GROQ_API_KEY to backend/.env for live drafting.')

  return (
    <div className={cn('border-b px-4 py-2.5 sm:px-6', tone)}>
      <div className="mx-auto flex max-w-7xl items-start gap-3">
        <Icon className="mt-0.5 size-4 shrink-0 text-amber-300" aria-hidden />
        <p className="flex-1 text-xs leading-relaxed text-amber-50/85">
          <span className="font-medium">
            {isUnavailable || isError ? 'API offline' : 'Demo mode'}
          </span>{' '}
          &mdash; {message}
        </p>
        <button
          type="button"
          onClick={() => setDismissed(true)}
          className="rounded-md p-1 text-amber-100/60 transition-colors hover:bg-navy-900/40 hover:text-amber-50"
          aria-label="Dismiss notice"
        >
          <X className="size-3.5" aria-hidden />
        </button>
      </div>
    </div>
  )
}

/** Compact variant for the editor chrome. */
export function AiModePill() {
  const { isDemo, isUnavailable, isLive, isError, status } = useAiStatus()

  const config = isError || isUnavailable
    ? { label: 'Offline', tone: 'text-rose-300 border-rose-500/30 bg-rose-500/10', icon: WifiOff }
    : isDemo
      ? { label: 'Demo AI', tone: 'text-amber-300 border-amber-500/30 bg-amber-500/10', icon: Bot }
      : { label: status.model ?? 'Live AI', tone: 'text-emerald-300 border-emerald-500/30 bg-emerald-500/10', icon: Sparkles }

  const Icon = isLive ? Sparkles : config.icon

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[0.6875rem] font-medium',
        config.tone,
      )}
      title={status.message ?? 'AI model used for generation'}
    >
      <Icon className="size-3" aria-hidden />
      {isError ? <AlertTriangle className="size-3" aria-hidden /> : null}
      {config.label}
    </span>
  )
}
