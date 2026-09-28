import * as DropdownMenuPrimitive from '@radix-ui/react-dropdown-menu'
import { Check } from 'lucide-react'
import type { ComponentPropsWithoutRef } from 'react'

import { cn } from '../../utils/cn'

export const DropdownMenu = DropdownMenuPrimitive.Root
export const DropdownMenuTrigger = DropdownMenuPrimitive.Trigger
export const DropdownMenuGroup = DropdownMenuPrimitive.Group

export function DropdownMenuContent({
  className,
  sideOffset = 6,
  align = 'end',
  ...props
}: ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Content>) {
  return (
    <DropdownMenuPrimitive.Portal>
      <DropdownMenuPrimitive.Content
        sideOffset={sideOffset}
        align={align}
        className={cn(
          'z-50 min-w-52 overflow-hidden rounded-xl border border-navy-600',
          'bg-navy-850 p-1 shadow-lift',
          'data-[state=open]:animate-in data-[state=closed]:animate-out',
          'data-[state=open]:fade-in-0 data-[state=closed]:fade-out-0',
          'data-[state=open]:zoom-in-95 data-[state=closed]:zoom-out-95',
          className,
        )}
        {...props}
      />
    </DropdownMenuPrimitive.Portal>
  )
}

export function DropdownMenuItem({
  className,
  destructive,
  ...props
}: ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Item> & {
  destructive?: boolean
}) {
  return (
    <DropdownMenuPrimitive.Item
      className={cn(
        'flex cursor-pointer items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm',
        'text-ivory-200 outline-none transition-colors',
        'focus:bg-navy-700/80 focus:text-ivory-50',
        'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
        '[&_svg]:size-4 [&_svg]:shrink-0',
        destructive && 'text-rose-300 focus:bg-rose-500/15 focus:text-rose-200',
        className,
      )}
      {...props}
    />
  )
}

export function DropdownMenuCheckboxItem({
  className,
  children,
  ...props
}: ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.CheckboxItem>) {
  return (
    <DropdownMenuPrimitive.CheckboxItem
      className={cn(
        'relative flex cursor-pointer items-center gap-2 rounded-lg py-2 pr-2.5 pl-8 text-sm',
        'text-ivory-200 outline-none transition-colors focus:bg-navy-700/80 focus:text-ivory-50',
        className,
      )}
      {...props}
    >
      <span className="absolute left-2.5 flex size-3.5 items-center justify-center">
        <DropdownMenuPrimitive.ItemIndicator>
          <Check className="size-3.5 text-gold-400" aria-hidden />
        </DropdownMenuPrimitive.ItemIndicator>
      </span>
      {children}
    </DropdownMenuPrimitive.CheckboxItem>
  )
}

export function DropdownMenuLabel({
  className,
  ...props
}: ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Label>) {
  return (
    <DropdownMenuPrimitive.Label
      className={cn(
        'px-2.5 py-1.5 text-[0.6875rem] font-medium tracking-[0.09em] text-ivory-300/55 uppercase',
        className,
      )}
      {...props}
    />
  )
}

export function DropdownMenuSeparator({
  className,
  ...props
}: ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Separator>) {
  return (
    <DropdownMenuPrimitive.Separator
      className={cn('my-1 h-px bg-navy-700', className)}
      {...props}
    />
  )
}
