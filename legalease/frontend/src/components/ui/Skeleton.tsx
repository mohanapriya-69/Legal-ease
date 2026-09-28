import { cn } from '../../utils/cn'

/** Shimmering placeholder used while data loads. */
export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      aria-hidden
      className={cn('skeleton-sheen rounded-md', className)}
      {...props}
    />
  )
}

export function SkeletonText({
  lines = 3,
  className,
}: {
  lines?: number
  className?: string
}) {
  return (
    <div className={cn('flex flex-col gap-2', className)} aria-hidden>
      {Array.from({ length: lines }, (_, i) => (
        <Skeleton
          key={i}
          className={cn('h-3', i === lines - 1 ? 'w-2/3' : 'w-full')}
        />
      ))}
    </div>
  )
}

export function SkeletonCard() {
  return (
    <div className="rounded-card border border-navy-700/80 bg-navy-850/70 p-5">
      <div className="flex items-center gap-3">
        <Skeleton className="size-10 rounded-lg" />
        <div className="flex-1">
          <Skeleton className="h-4 w-1/2" />
          <SkeletonText lines={2} className="mt-2" />
        </div>
      </div>
    </div>
  )
}
