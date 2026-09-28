import { Skeleton } from './ui/Skeleton'

/** Suspense fallback for lazily loaded routes. */
export function PageFallback({ label }: { label: string }) {
  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-10 sm:px-6 lg:px-8" role="status" aria-busy>
      <span className="sr-only">{label}</span>
      <Skeleton className="h-8 w-64" />
      <Skeleton className="mt-3 h-4 w-96" />
      <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }, (_, i) => (
          <Skeleton key={i} className="h-44 rounded-card" />
        ))}
      </div>
    </div>
  )
}
