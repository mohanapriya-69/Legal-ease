import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { Loader2 } from 'lucide-react'
import type { ButtonHTMLAttributes } from 'react'

import { cn } from '../../utils/cn'

const buttonVariants = cva(
  [
    'relative inline-flex items-center justify-center gap-2 whitespace-nowrap',
    'font-medium transition-all duration-200 ease-[cubic-bezier(0.22,1,0.36,1)]',
    'disabled:pointer-events-none disabled:opacity-50',
    '[&_svg]:shrink-0 active:scale-[0.985]',
    'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold-400',
  ],
  {
    variants: {
      variant: {
        primary:
          'bg-gradient-to-b from-gold-300 to-gold-500 text-navy-950 shadow-[0_1px_0_0_rgba(255,255,255,0.35)_inset,0_10px_24px_-12px_rgba(201,162,39,0.7)] hover:from-gold-200 hover:to-gold-400 hover:shadow-[0_1px_0_0_rgba(255,255,255,0.45)_inset,0_14px_30px_-12px_rgba(201,162,39,0.85)]',
        secondary:
          'bg-navy-700/70 text-ivory-100 border border-navy-600 hover:bg-navy-700 hover:border-navy-500',
        outline:
          'border border-navy-600 bg-transparent text-ivory-200 hover:border-gold-500/60 hover:bg-navy-800/60 hover:text-ivory-50',
        ghost: 'text-ivory-200 hover:bg-navy-800/70 hover:text-ivory-50',
        danger:
          'bg-rose-500/12 text-rose-300 border border-rose-500/30 hover:bg-rose-500/20 hover:border-rose-400/50',
        paper:
          'bg-ivory-100 text-ink-900 hover:bg-ivory-50 shadow-[0_1px_2px_rgba(26,26,26,0.12)]',
        link: 'text-gold-300 underline-offset-4 hover:underline hover:text-gold-200',
      },
      size: {
        sm: 'h-8 rounded-md px-3 text-xs [&_svg]:size-3.5',
        md: 'h-10 rounded-lg px-4 text-sm [&_svg]:size-4',
        lg: 'h-12 rounded-xl px-6 text-[0.9375rem] [&_svg]:size-[1.125rem]',
        icon: 'size-10 rounded-lg [&_svg]:size-[1.125rem]',
        'icon-sm': 'size-8 rounded-md [&_svg]:size-4',
      },
    },
    defaultVariants: { variant: 'primary', size: 'md' },
  },
)

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
  loading?: boolean
}

export function Button({
  className,
  variant,
  size,
  asChild = false,
  loading = false,
  disabled,
  children,
  ...props
}: ButtonProps) {
  const Component = asChild ? Slot : 'button'

  return (
    <Component
      className={cn(buttonVariants({ variant, size }), className)}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...props}
    >
      {loading ? (
        <>
          <Loader2 className="animate-spin" aria-hidden />
          <span className="sr-only">Working</span>
          {asChild ? null : children}
        </>
      ) : (
        children
      )}
    </Component>
  )
}
