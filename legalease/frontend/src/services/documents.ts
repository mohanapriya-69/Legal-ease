import { http } from './client'
import type {
  DocumentRecord,
  DocumentStatus,
  DocumentSummary,
  DocumentUpdatePayload,
  DocumentVersion,
  DashboardStats,
  GenerateRequest,
  GenerationResponse,
  Paged,
  RewriteAction,
  RewriteResponse,
} from '../types/api'

export const documentsApi = {
  generate: (payload: GenerateRequest) =>
    http.post<GenerationResponse>('/api/documents/generate', payload),

  list: (params?: {
    search?: string
    document_type?: string
    status?: DocumentStatus
    limit?: number
    offset?: number
  }) => http.get<Paged<DocumentSummary>>('/api/documents', { params }),

  get: (id: string) => http.get<DocumentRecord>(`/api/documents/${id}`),

  update: (id: string, payload: DocumentUpdatePayload) =>
    http.put<DocumentRecord>(`/api/documents/${id}`, payload),

  setStatus: (id: string, status: DocumentStatus) =>
    http.patch<DocumentRecord>(`/api/documents/${id}/status`, { status }),

  remove: (id: string) => http.delete<void>(`/api/documents/${id}`),

  duplicate: (id: string) =>
    http.post<DocumentRecord>(`/api/documents/${id}/duplicate`),

  rewriteSection: (
    id: string,
    body: {
      section_index: number
      action: RewriteAction
      custom_instruction?: string
    },
  ) => http.post<RewriteResponse>(`/api/documents/${id}/rewrite-section`, body),

  versions: (id: string) =>
    http.get<DocumentVersion[]>(`/api/documents/${id}/versions`),

  restoreVersion: (id: string, versionNumber: number) =>
    http.post<DocumentRecord>(
      `/api/documents/${id}/versions/${versionNumber}/restore`,
    ),

  stats: () => http.get<DashboardStats>('/api/documents/stats'),

  exportUrl: (id: string, format: 'pdf' | 'docx' | 'txt') =>
    `/api/documents/${id}/export/${format}`,
}
