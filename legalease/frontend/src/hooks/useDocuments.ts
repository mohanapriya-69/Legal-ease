import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

import { ApiError, documentsApi } from '../services'
import type {
  DocumentRecord,
  DocumentStatus,
  DocumentSummary,
  DocumentUpdatePayload,
  Paged,
  RewriteAction,
} from '../types/api'

export const DOCUMENTS_KEY = ['documents'] as const

export function documentKey(id: string) {
  return ['documents', id] as const
}

export function documentListKey(filters: Record<string, string | number | undefined>) {
  return ['documents', 'list', filters] as const
}

/** Paginated document list with search and filters. */
export function useDocuments(filters: {
  search?: string
  document_type?: string
  status?: DocumentStatus
  limit?: number
  offset?: number
} = {}) {
  const query = useQuery({
    queryKey: documentListKey(filters),
    queryFn: () => documentsApi.list(filters),
    placeholderData: (previous) => previous,
    staleTime: 5_000,
  })

  return {
    ...query,
    documents: query.data?.items ?? [],
    meta: query.data?.meta,
    total: query.data?.meta.total ?? 0,
  }
}

/** Dashboard counters. */
export function useDashboardStats() {
  return useQuery({
    queryKey: [...DOCUMENTS_KEY, 'stats'],
    queryFn: documentsApi.stats,
    staleTime: 10_000,
  })
}

export function useDocument(id: string | undefined) {
  return useQuery({
    queryKey: documentKey(id ?? 'none'),
    queryFn: () => documentsApi.get(id as string),
    enabled: Boolean(id),
    staleTime: 2_000,
  })
}

export function useDocumentVersions(id: string | undefined) {
  return useQuery({
    queryKey: [...documentKey(id ?? 'none'), 'versions'],
    queryFn: () => documentsApi.versions(id as string),
    enabled: Boolean(id),
    staleTime: 2_000,
  })
}

function reportError(error: unknown, fallback: string) {
  toast.error(error instanceof ApiError ? error.userMessage : fallback)
}

/** Delete / duplicate / status mutations, with cache invalidation. */
export function useDocumentActions(id?: string) {
  const client = useQueryClient()

  const invalidate = () => {
    void client.invalidateQueries({ queryKey: DOCUMENTS_KEY })
    if (id) void client.invalidateQueries({ queryKey: documentKey(id) })
  }

  const remove = useMutation({
    mutationFn: (documentId: string) => documentsApi.remove(documentId),
    onSuccess: () => {
      toast.success('Document deleted')
      invalidate()
    },
    onError: (error) => reportError(error, 'Could not delete the document.'),
  })

  const duplicate = useMutation({
    mutationFn: (documentId: string) => documentsApi.duplicate(documentId),
    onSuccess: (document: DocumentRecord) => {
      toast.success('Document duplicated')
      invalidate()
      return document
    },
    onError: (error) => reportError(error, 'Could not duplicate the document.'),
  })

  const setStatus = useMutation({
    mutationFn: ({ documentId, status }: { documentId: string; status: DocumentStatus }) =>
      documentsApi.setStatus(documentId, status),
    onSuccess: (document) => {
      toast.success(`Marked as ${document.status}`)
      invalidate()
    },
    onError: (error) => reportError(error, 'Could not update the status.'),
  })

  return { remove, duplicate, setStatus }
}

/** Explicit save from the editor (autosave is handled separately). */
export function useSaveDocument(id: string | undefined) {
  const client = useQueryClient()

  return useMutation({
    mutationFn: (payload: DocumentUpdatePayload) => documentsApi.update(id as string, payload),
    onSuccess: (document: DocumentRecord) => {
      client.setQueryData(documentKey(id as string), document)
      void client.invalidateQueries({ queryKey: [...documentKey(id as string), 'versions'] })
    },
    onError: (error) => reportError(error, 'Could not save your changes.'),
  })
}

export function useRestoreVersion(id: string | undefined) {
  const client = useQueryClient()

  return useMutation({
    mutationFn: (versionNumber: number) =>
      documentsApi.restoreVersion(id as string, versionNumber),
    onSuccess: (restored) => {
      toast.success('Version restored')
      client.setQueryData(documentKey(id as string), restored)
      void client.invalidateQueries({
        queryKey: [...documentKey(id as string), 'versions'],
      })
    },
    onError: (error) => reportError(error, 'Could not restore that version.'),
  })
}

export function useRewriteSection(id: string | undefined) {
  const client = useQueryClient()

  return useMutation({
    mutationFn: (body: {
      section_index: number
      action: RewriteAction
      custom_instruction?: string
    }) => documentsApi.rewriteSection(id as string, body),
    onSuccess: (result) => {
      client.setQueryData(documentKey(id as string), result.document)
      void client.invalidateQueries({ queryKey: [...documentKey(id as string), 'versions'] })
      if (result.warnings.length) result.warnings.forEach((w) => toast.warning(w))
    },
    onError: (error) => reportError(error, 'The AI could not revise that section.'),
  })
}

export type { DocumentRecord, DocumentSummary, Paged }
