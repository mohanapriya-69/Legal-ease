import { useQuery } from '@tanstack/react-query'

import { systemApi } from '../services'
import type { AiStatus } from '../types/api'

const FALLBACK: AiStatus = {
  mode: 'unconfigured',
  configured: false,
  demo_mode: false,
  available: false,
  model: null,
  message: 'Could not reach the LegalEase API.',
}

export const AI_STATUS_QUERY_KEY = ['ai-status'] as const

/**
 * Backend AI mode, polled in the background. Drives the demo/live banner so
 * the user always knows whether a real model was called.
 */
export function useAiStatus() {
  const query = useQuery({
    queryKey: AI_STATUS_QUERY_KEY,
    queryFn: systemApi.aiStatus,
    staleTime: 30_000,
    refetchInterval: 60_000,
    retry: 1,
  })

  const status: AiStatus = query.data ?? FALLBACK

  return {
    ...query,
    status,
    isDemo: status.mode === 'demo',
    isLive: status.mode === 'groq',
    isUnavailable: status.mode === 'unconfigured',
  }
}
