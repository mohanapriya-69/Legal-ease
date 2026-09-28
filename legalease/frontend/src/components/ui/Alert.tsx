import { cva, type VariantProps } from 'class-variance-authority'
import { AlertTriangle, Info, ShieldCheck, Sparkles, TriangleAlert } from 'lucide-react'
import type { HTMLAttributes, ReactNode } from 'react'

import { cn } from '../../utils/cn'

/* ----------------------------------------------------------------- Alert */

const alertVariants = cva('rounded-xl border p-4 text-sm leading-relaxed', {
  variants: {
    variant: {
      info: 'border-sky-500/30 bg-sky-500/8 text-sky-100',
      warning: 'border-amber-500/30 bg-amber-500/8 text-amber-100',
      danger: 'border-rose-500/30 bg-rose-500/8 text-rose-100',
      gold: 'border-gold-500/30 bg-gold-500/8 text-gold-100',
      neutral: 'border-navy-600 bg-navy-800/50 text-ivory-200',
    },
  },
  defaultVariants: { variant: 'neutral' },
})

const ALERT_ICON = {
  info: Info,
  warning: AlertTriangle,
  danger: TriangleAlert,
  gold: Sparkles,
  neutral: ShieldCheck,
} as const

export interface AlertProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof alertVariants> {
  title?: string
  icon?: boolean
}

export function Alert({
  className,
  variant = 'neutral',
  title,
  icon = true,
  children,
  ...props
}: AlertProps) {
  const Icon = ALERT_ICON[variant ?? 'neutral']
  return (
    <div
      role="note"
      className={cn(alertVariants({ variant }), className)}
      {...props}
    >
      <div className="flex gap-3">
        {icon ? <Icon className="mt-0.5 size-4 shrink-0 opacity-80" aria-hidden /> : null}
        <div className="min-w-0 flex-1">
          {title ? <p className="mb-1 font-medium">{title}</p> : null}
          <div className="[&_a]:underline [&_a]:underline-offset-2">{children}</div>
        </div>
      </div>
    </div>
  )
}

/* -------------------------------------------------------- Empty state */

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  className,
}: {
  icon: React.ComponentType<{ className?: string }>
  title: string
  description?: string
  action?: ReactNode
  className?: string
}) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center rounded-card border border-dashed',
        'border-navy-600/80 bg-navy-850/40 px-6 py-16 text-center',
        className,
      )}
    >
      <div className="relative mb-5">
        <div
          className="absolute inset-0 -z-10 rounded-full bg-gold-500/12 blur-2xl"
          aria-hidden
        />
        <div className="flex size-14 items-center justify-center rounded-2xl border border-gold-500/25 bg-navy-800">
          <Icon className="size-6 text-gold-400" aria-hidden />
        </div>
      </div>
      <h3 className="font-display text-lg font-semibold text-ivory-50">{title}</h3>
      {description ? (
        <p className="mt-2 max-w-md text-sm leading-relaxed text-ivory-300/65">
          {description}
        </p>
      ) : null}
      {action ? <div className="mt-6">{action}</div> : null}
    </div>
  )
}
