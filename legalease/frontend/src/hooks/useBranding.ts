import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

import { ApiError, brandingApi } from '../services'
import type { Branding } from '../types/api'

export const BRANDING_KEY = ['branding'] as const

export function useBranding() {
  const query = useQuery({
    queryKey: BRANDING_KEY,
    queryFn: brandingApi.list,
    staleTime: 30_000,
  })

  return {
    ...query,
    profiles: query.data?.items ?? [],
    /** Most recent profile, which is what generation uses by default. */
    active: query.data?.items[0] ?? null,
  }
}

export function useSaveBranding() {
  const client = useQueryClient()

  return useMutation({
    mutationFn: (payload: Branding & { id?: string }) => brandingApi.save(payload),
    onSuccess: () => {
      toast.success('Branding saved')
      void client.invalidateQueries({ queryKey: BRANDING_KEY })
    },
    onError: (error) =>
      toast.error(
        error instanceof ApiError ? error.userMessage : 'Could not save your branding.',
      ),
  })
}

export function useUploadLogo() {
  const client = useQueryClient()

  return useMutation({
    mutationFn: (file: File) => brandingApi.uploadLogo(file),
    onSuccess: (result) => {
      toast.success(`Logo uploaded (${Math.round(result.size_bytes / 1024)} KB)`)
      void client.invalidateQueries({ queryKey: BRANDING_KEY })
    },
    onError: (error) =>
      toast.error(
        error instanceof ApiError ? error.userMessage : 'That logo could not be uploaded.',
      ),
  })
}
