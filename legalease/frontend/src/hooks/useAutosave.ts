import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'

import { useDebouncedCallback } from './useDebounce'

export type SaveState = 'idle' | 'dirty' | 'saving' | 'saved' | 'error'

export interface AutosavePayload<T> {
  value: T
  createVersion: boolean
  versionLabel: string | null
}

export interface UseAutosaveOptions<T> {
  /** Current value. Autosave keys off its serialised form. */
  value: T
  /** Persist function. Rejections are captured, not thrown. */
  save: (payload: AutosavePayload<T>) => Promise<unknown>
  delay?: number
  enabled?: boolean
  /** Create a labelled version snapshot alongside the save. */
  createVersion?: boolean
  versionLabel?: string | null
  onError?: (error: unknown) => void
  onSaved?: (value: T) => void
}

/**
 * Debounced autosave with explicit state.
 *
 * Saves after `delay` ms of quiet, flushes pending work on unmount so closing
 * the tab never loses the last edit, and reports failures instead of dropping
 * them silently.
 */
export function useAutosave<T>({
  value,
  save,
  delay = 1200,
  enabled = true,
  createVersion = false,
  versionLabel = null,
  onError,
  onSaved,
}: UseAutosaveOptions<T>) {
  const [state, setState] = useState<SaveState>('idle')
  const [lastError, setLastError] = useState<string | null>(null)
  const baselineRef = useRef<string>(JSON.stringify(value))
  const valueRef = useRef<T>(value)
  const inFlightRef = useRef(false)
  const mountedRef = useRef(true)
  const serialised = JSON.stringify(value)

  // The persist callback runs from a timer, so it needs the latest value.
  // Writing in an effect keeps the ref out of the render path.
  useLayoutEffect(() => {
    valueRef.current = value
  }, [value])

  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
    }
  }, [])

  const persist = useCallback(async () => {
    if (inFlightRef.current) return
    inFlightRef.current = true
    if (mountedRef.current) setState('saving')
    try {
      await save({
        value: valueRef.current,
        createVersion,
        versionLabel,
      })
      baselineRef.current = JSON.stringify(valueRef.current)
      if (mountedRef.current) setState('saved')
      onSaved?.(valueRef.current)
    } catch (error) {
      if (mountedRef.current) {
        setLastError(error instanceof Error ? error.message : String(error))
        setState('error')
      }
      onError?.(error)
    } finally {
      inFlightRef.current = false
    }
  }, [save, createVersion, versionLabel, onSaved, onError])

  const { run, flush, cancel, isPending } = useDebouncedCallback(
    () => void persist(),
    delay,
  )

  // Content objects are rebuilt on every keystroke, so compare serialised
  // forms rather than references to avoid saving unchanged text.
  useEffect(() => {
    if (!enabled) return
    if (serialised === baselineRef.current) {
      cancel()
      if (mountedRef.current) setState((current) => (current === 'saved' ? 'idle' : current))
      return
    }
    setState((current) => (current === 'saving' ? current : 'dirty'))
    run()
  }, [serialised, enabled, run, cancel])

  // Never lose the final keystroke when the view unmounts.
  useEffect(() => {
    return () => {
      if (isPending()) flush()
    }
  }, [flush, isPending])

  const saveNow = useCallback(() => {
    cancel()
    return persist()
  }, [cancel, persist])

  const isDirty = state === 'dirty' || state === 'saving' || state === 'error'

  return { state, isDirty, saveNow, lastError }
}
