import { assetUrl, http } from './client'
import type {
  AiStatus,
  Branding,
  BrandProfile,
  ClauseSuggestion,
  HealthResponse,
  LogoUpload,
  SampleData,
  TemplateItem,
} from '../types/api'

export const templatesApi = {
  list: (params?: { search?: string; category?: string }) =>
    http.get<{ items: TemplateItem[]; total: number; categories: string[] }>(
      '/api/templates',
      { params },
    ),

  get: (id: string) => http.get<TemplateItem>(`/api/templates/${id}`),

  sample: (id: string) =>
    http.get<SampleData>(`/api/templates/${id}/sample`),

  clauses: () => http.get<{ items: ClauseSuggestion[] }>('/api/clauses'),

  rewriteActions: () =>
    http.get<{ items: Array<{ key: RewriteActionKey; label: string }> }>(
      '/api/rewrite-actions',
    ),
}

export type RewriteActionKey =
  | 'rewrite_professional'
  | 'simplify'
  | 'more_formal'
  | 'expand'
  | 'shorten'
  | 'fix_grammar'
  | 'add_protection'

export const brandingApi = {
  list: () =>
    http.get<{ items: BrandProfile[]; total: number }>('/api/branding'),

  save: (payload: Branding & { id?: string }) =>
    http.post<BrandProfile>('/api/branding', payload),

  uploadLogo: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return http.post<LogoUpload>('/api/branding/logo', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export const systemApi = {
  health: () => http.get<HealthResponse>('/api/health'),
  aiStatus: () => http.get<AiStatus>('/api/ai/status'),
}

export { assetUrl }
