import * as TooltipPrimitive from '@radix-ui/react-tooltip'
import type { ComponentPropsWithoutRef, ReactNode } from 'react'

import { cn } from '../../utils/cn'

export const TooltipProvider = TooltipPrimitive.Provider
export const TooltipRoot = TooltipPrimitive.Root
export const TooltipTrigger = TooltipPrimitive.Trigger

export function TooltipContent({
  className,
  sideOffset = 6,
  ...props
}: ComponentPropsWithoutRef<typeof TooltipPrimitive.Content>) {
  return (
    <TooltipPrimitive.Portal>
      <TooltipPrimitive.Content
        sideOffset={sideOffset}
        className={cn(
          'z-50 max-w-64 rounded-lg border border-navy-600 bg-navy-800 px-2.5 py-1.5',
          'text-xs leading-relaxed text-ivory-100 shadow-lift',
          'data-[state=delayed-open]:animate-in data-[state=closed]:animate-out',
          'data-[state=delayed-open]:fade-in-0 data-[state=closed]:fade-out-0',
          'data-[state=delayed-open]:zoom-in-95',
          className,
        )}
        {...props}
      />
    </TooltipPrimitive.Portal>
  )
}

/** Convenience wrapper: `<Tooltip label="...">{trigger}</Tooltip>`. */
export function Tooltip({
  label,
  children,
  side = 'bottom',
  className,
}: {
  label: ReactNode
  children: ReactNode
  side?: 'top' | 'right' | 'bottom' | 'left'
  className?: string
}) {
  return (
    <TooltipRoot>
      <TooltipTrigger asChild>{children}</TooltipTrigger>
      <TooltipContent side={side} className={className}>
        {label}
      </TooltipContent>
    </TooltipRoot>
  )
}
