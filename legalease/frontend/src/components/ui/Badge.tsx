import { cva, type VariantProps } from 'class-variance-authority'
import type { HTMLAttributes } from 'react'

import { cn } from '../../utils/cn'

const badgeVariants = cva(
  'inline-flex items-center gap-1.5 rounded-full border font-medium whitespace-nowrap',
  {
    variants: {
      variant: {
        neutral: 'border-navy-600 bg-navy-800/70 text-ivory-200',
        gold: 'border-gold-500/35 bg-gold-500/12 text-gold-200',
        success: 'border-emerald-500/35 bg-emerald-500/12 text-emerald-300',
        warning: 'border-amber-500/35 bg-amber-500/12 text-amber-300',
        danger: 'border-rose-500/35 bg-rose-500/12 text-rose-300',
        info: 'border-sky-500/35 bg-sky-500/12 text-sky-300',
        paper: 'border-ivory-300 bg-ivory-100 text-ink-900',
      },
      size: {
        sm: 'px-2 py-0.5 text-[0.6875rem]',
        md: 'px-2.5 py-1 text-xs',
      },
    },
    defaultVariants: { variant: 'neutral', size: 'md' },
  },
)

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, size, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant, size }), className)} {...props} />
}

const statusVariant: Record<string, BadgeProps['variant']> = {
  draft: 'neutral',
  generated: 'info',
  completed: 'success',
}

export function StatusBadge({ status }: { status: string }) {
  return (
    <Badge variant={statusVariant[status] ?? 'neutral'} size="sm" className="capitalize">
      <span
        className={cn(
          'size-1.5 rounded-full',
          status === 'draft' && 'bg-ivory-300/50',
          status === 'generated' && 'bg-sky-400',
          status === 'completed' && 'bg-emerald-400',
        )}
        aria-hidden
      />
      {status}
    </Badge>
  )
}
