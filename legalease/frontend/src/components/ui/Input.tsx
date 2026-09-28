import * as LabelPrimitive from '@radix-ui/react-label'
import { AlertCircle } from 'lucide-react'
import { forwardRef, useId } from 'react'
import type { InputHTMLAttributes, TextareaHTMLAttributes } from 'react'

import { cn } from '../../utils/cn'

/* ---------------------------------------------------------------- Label */

export const Label = forwardRef<
  HTMLLabelElement,
  React.ComponentPropsWithoutRef<typeof LabelPrimitive.Root>
>(({ className, ...props }, ref) => (
  <LabelPrimitive.Root
    ref={ref}
    className={cn(
      'text-xs font-medium uppercase tracking-[0.09em] text-ivory-300/80',
      className,
    )}
    {...props}
  />
))
Label.displayName = LabelPrimitive.Root.displayName

/* ---------------------------------------------------------------- Field */

interface FieldProps {
  label?: string
  hint?: string
  error?: string
  required?: boolean
  children: (id: string, describedBy: string | undefined) => React.ReactNode
  className?: string
}

/** Wires a label, hint and error message to a control with correct ARIA. */
export function Field({
  label,
  hint,
  error,
  required,
  children,
  className,
}: FieldProps) {
  const id = useId()
  const hintId = hint ? `${id}-hint` : undefined
  const errorId = error ? `${id}-error` : undefined
  const describedBy = [errorId, hintId].filter(Boolean).join(' ') || undefined

  return (
    <div className={cn('flex flex-col gap-2', className)}>
      {label ? (
        <Label htmlFor={id}>
          {label}
          {required ? <span className="ml-1 text-gold-400">*</span> : null}
        </Label>
      ) : null}
      {children(id, describedBy)}
      {error ? (
        <p
          id={errorId}
          role="alert"
          className="flex items-start gap-1.5 text-xs text-rose-300"
        >
          <AlertCircle className="mt-px size-3.5 shrink-0" aria-hidden />
          <span>{error}</span>
        </p>
      ) : hint ? (
        <p id={hintId} className="text-xs text-ivory-300/55">
          {hint}
        </p>
      ) : null}
    </div>
  )
}

/* ----------------------------------------------------------------- Input */

const controlBase = [
  'w-full rounded-lg border bg-navy-900/60 text-ivory-50 placeholder:text-ivory-300/35',
  'transition-all duration-200 outline-none',
  'focus:border-gold-500/70 focus:bg-navy-900 focus:ring-2 focus:ring-gold-500/20',
  'disabled:cursor-not-allowed disabled:opacity-55',
].join(' ')

export const Input = forwardRef<
  HTMLInputElement,
  InputHTMLAttributes<HTMLInputElement> & { invalid?: boolean }
>(({ className, invalid, ...props }, ref) => (
  <input
    ref={ref}
    aria-invalid={invalid || undefined}
    className={cn(
      controlBase,
      'h-10 px-3 text-sm',
      invalid
        ? 'border-rose-500/60 focus:border-rose-400 focus:ring-rose-500/20'
        : 'border-navy-600 hover:border-navy-500',
      className,
    )}
    {...props}
  />
))
Input.displayName = 'Input'

/* -------------------------------------------------------------- Textarea */

export const Textarea = forwardRef<
  HTMLTextAreaElement,
  TextareaHTMLAttributes<HTMLTextAreaElement> & { invalid?: boolean }
>(({ className, invalid, ...props }, ref) => (
  <textarea
    ref={ref}
    aria-invalid={invalid || undefined}
    className={cn(
      controlBase,
      'min-h-24 resize-y px-3 py-2.5 text-sm leading-relaxed',
      invalid
        ? 'border-rose-500/60 focus:border-rose-400 focus:ring-rose-500/20'
        : 'border-navy-600 hover:border-navy-500',
      className,
    )}
    {...props}
  />
))
Textarea.displayName = 'Textarea'

/* --------------------------------------------------------------- Select */

export const NativeSelect = forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement> & { invalid?: boolean }
>(({ className, invalid, children, ...props }, ref) => (
  <div className="relative">
    <select
      ref={ref}
      aria-invalid={invalid || undefined}
      className={cn(
        controlBase,
        'h-10 appearance-none pr-9 text-sm',
        invalid
          ? 'border-rose-500/60'
          : 'border-navy-600 hover:border-navy-500',
        className,
      )}
      {...props}
    >
      {children}
    </select>
    <svg
      className="pointer-events-none absolute top-1/2 right-3 size-4 -translate-y-1/2 text-ivory-300/50"
      viewBox="0 0 20 20"
      fill="none"
      aria-hidden
    >
      <path
        d="M6 8l4 4 4-4"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  </div>
))
NativeSelect.displayName = 'NativeSelect'
