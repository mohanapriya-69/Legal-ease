import { useCallback, useEffect, useRef, useState } from 'react'

/** Debounced mirror of a value. */
export function useDebouncedValue<T>(value: T, delay = 400): T {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debounced
}

export interface DebouncedCallback<Args extends unknown[]> {
  /** Schedule the call. Repeated calls reset the timer. */
  run: (...args: Args) => void
  /** Run the pending call immediately (on blur, on save, on unmount flush). */
  flush: () => void
  /** Drop the pending call. */
  cancel: () => void
  /** Whether a call is currently scheduled. */
  isPending: () => boolean
}

/**
 * Debounces a callback. Always invokes the latest closure, so callers do not
 * need to memoise the function they pass in.
 */
export function useDebouncedCallback<Args extends unknown[]>(
  callback: (...args: Args) => void | Promise<void>,
  delay = 800,
): DebouncedCallback<Args> {
  const callbackRef = useRef(callback)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const pendingArgsRef = useRef<Args | null>(null)

  useEffect(() => {
    callbackRef.current = callback
  }, [callback])

  const cancel = useCallback(() => {
    if (timerRef.current !== null) clearTimeout(timerRef.current)
    timerRef.current = null
    pendingArgsRef.current = null
  }, [])

  const flush = useCallback(() => {
    if (timerRef.current === null) return
    clearTimeout(timerRef.current)
    timerRef.current = null
    const queued = pendingArgsRef.current
    pendingArgsRef.current = null
    if (queued) void callbackRef.current(...queued)
  }, [])

  const run = useCallback(
    (...args: Args) => {
      pendingArgsRef.current = args
      if (timerRef.current !== null) clearTimeout(timerRef.current)
      timerRef.current = setTimeout(() => {
        const queued = pendingArgsRef.current
        timerRef.current = null
        pendingArgsRef.current = null
        if (queued) void callbackRef.current(...queued)
      }, delay)
    },
    [delay],
  )

  const isPending = useCallback(() => timerRef.current !== null, [])

  useEffect(() => cancel, [cancel])

  return { run, flush, cancel, isPending }
}
