import * as SwitchPrimitive from '@radix-ui/react-switch'
import type { ComponentPropsWithoutRef } from 'react'

import { cn } from '../../utils/cn'

export function Switch({
  className,
  ...props
}: ComponentPropsWithoutRef<typeof SwitchPrimitive.Root>) {
  return (
    <SwitchPrimitive.Root
      className={cn(
        'peer inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full',
        'border border-transparent transition-colors duration-200',
        'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold-400',
        'disabled:cursor-not-allowed disabled:opacity-50',
        'data-[state=checked]:bg-gold-500 data-[state=unchecked]:bg-navy-600',
        className,
      )}
      {...props}
    >
      <SwitchPrimitive.Thumb
        className={cn(
          'pointer-events-none block size-4 rounded-full bg-ivory-50 shadow-sm ring-0',
          'transition-transform duration-200 ease-[cubic-bezier(0.22,1,0.36,1)]',
          'data-[state=checked]:translate-x-4 data-[state=unchecked]:translate-x-0.5',
        )}
      />
    </SwitchPrimitive.Root>
  )
}
