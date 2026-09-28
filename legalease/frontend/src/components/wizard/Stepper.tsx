import { Check } from 'lucide-react'

import { WIZARD_STEPS } from '../../constants/legal'
import { cn } from '../../utils/cn'

export function Stepper({
  current,
  maxVisited,
  onSelect,
  isComplete,
}: {
  current: number
  maxVisited: number
  onSelect: (index: number) => void
  isComplete: (index: number) => boolean
}) {
  return (
    <nav aria-label="Document setup progress">
      <ol className="flex items-center gap-1 overflow-x-auto pb-1">
        {WIZARD_STEPS.map((step, index) => {
          const active = index === current
          const done = isComplete(index)
          const reachable = index <= maxVisited

          return (
            <li key={step.id} className="flex shrink-0 items-center gap-1">
              <button
                type="button"
                onClick={() => reachable && onSelect(index)}
                disabled={!reachable}
                aria-current={active ? 'step' : undefined}
                className={cn(
                  'group flex items-center gap-2.5 rounded-lg border px-3 py-2 text-left transition-all duration-200',
                  active
                    ? 'border-gold-500/45 bg-gold-500/10'
                    : reachable
                      ? 'border-navy-700 hover:border-navy-500'
                      : 'border-transparent opacity-45',
                )}
              >
                <span
                  className={cn(
                    'flex size-6 shrink-0 items-center justify-center rounded-full border text-[0.6875rem] font-semibold transition-colors',
                    active
                      ? 'border-gold-400 bg-gold-500 text-navy-950'
                      : done
                        ? 'border-emerald-500/50 bg-emerald-500/15 text-emerald-300'
                        : 'border-navy-600 text-ivory-300/60',
                  )}
                >
                  {done && !active ? <Check className="size-3.5" aria-hidden /> : index + 1}
                </span>
                <span className="hidden sm:block">
                  <span
                    className={cn(
                      'block text-xs leading-tight font-medium',
                      active ? 'text-gold-200' : 'text-ivory-200/80',
                    )}
                  >
                    {step.title}
                  </span>
                </span>
              </button>
              {index < WIZARD_STEPS.length - 1 ? (
                <span
                  className={cn(
                    'h-px w-4 shrink-0 transition-colors sm:w-6',
                    index < current ? 'bg-gold-500/40' : 'bg-navy-700',
                  )}
                  aria-hidden
                />
              ) : null}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
