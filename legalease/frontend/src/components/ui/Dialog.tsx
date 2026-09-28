import * as DialogPrimitive from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import type { ComponentPropsWithoutRef } from 'react'

import { cn } from '../../utils/cn'

export const Dialog = DialogPrimitive.Root
export const DialogTrigger = DialogPrimitive.Trigger
export const DialogClose = DialogPrimitive.Close

export function DialogContent({
  className,
  children,
  ...props
}: ComponentPropsWithoutRef<typeof DialogPrimitive.Content>) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay
        className={cn(
          'fixed inset-0 z-50 bg-navy-950/75 backdrop-blur-sm',
          'data-[state=open]:animate-in data-[state=closed]:animate-out',
          'data-[state=open]:fade-in-0 data-[state=closed]:fade-out-0',
        )}
      />
      <DialogPrimitive.Content
        className={cn(
          'fixed top-1/2 left-1/2 z-50 w-[min(94vw,38rem)] -translate-x-1/2 -translate-y-1/2',
          'rounded-2xl border border-navy-600 bg-navy-850 shadow-lift',
          'focus:outline-none',
          'data-[state=open]:animate-in data-[state=closed]:animate-out',
          'data-[state=open]:fade-in-0 data-[state=closed]:fade-out-0',
          'data-[state=open]:zoom-in-95 data-[state=closed]:zoom-out-95',
          'max-h-[88vh] overflow-y-auto',
          className,
        )}
        {...props}
      >
        {children}
        <DialogPrimitive.Close
          className={cn(
            'absolute top-4 right-4 rounded-md p-1.5 text-ivory-300/60 transition-colors',
            'hover:bg-navy-700/70 hover:text-ivory-50',
            'focus-visible:outline-2 focus-visible:outline-gold-400',
          )}
          aria-label="Close dialog"
        >
          <X className="size-4" aria-hidden />
        </DialogPrimitive.Close>
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  )
}

export function DialogHeader({ className, ...props }: ComponentPropsWithoutRef<'div'>) {
  return <div className={cn('flex flex-col gap-1.5 p-6 pb-4', className)} {...props} />
}

export function DialogTitle({
  className,
  ...props
}: ComponentPropsWithoutRef<typeof DialogPrimitive.Title>) {
  return (
    <DialogPrimitive.Title
      className={cn('font-display text-xl font-semibold text-ivory-50', className)}
      {...props}
    />
  )
}

export function DialogDescription({
  className,
  ...props
}: ComponentPropsWithoutRef<typeof DialogPrimitive.Description>) {
  return (
    <DialogPrimitive.Description
      className={cn('text-sm leading-relaxed text-ivory-300/70', className)}
      {...props}
    />
  )
}

export function DialogFooter({ className, ...props }: ComponentPropsWithoutRef<'div'>) {
  return (
    <div
      className={cn('flex flex-col-reverse gap-2 p-6 pt-0 sm:flex-row sm:justify-end', className)}
      {...props}
    />
  )
}
