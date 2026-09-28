/** Shapes returned by the LegalEase backend. */

export type DocumentStatus = 'draft' | 'generated' | 'completed'

export type GenerationSource = 'groq' | 'demo'

export interface Party {
  name: string
  role: string
  organization?: string | null
  address?: string | null
  email?: string | null
  phone?: string | null
}

export interface Clause {
  clause_key?: string | null
  title: string
  description: string
  is_required: boolean
}

export interface Jurisdiction {
  country?: string | null
  state?: string | null
  city?: string | null
  governing_law?: string | null
}

export interface Branding {
  organization_name?: string | null
  brand_profile_id?: string | null
  logo_path?: string | null
  address?: string | null
  email?: string | null
  phone?: string | null
  website?: string | null
  footer_text?: string | null
}

export interface GenerateRequest {
  document_type: string
  parties: Party[]
  clauses: Clause[]
  effective_date?: string | null
  expiry_date?: string | null
  jurisdiction: Jurisdiction
  branding: Branding
  additional_instructions: string
  title?: string | null
}

export interface DocumentTable {
  headers: string[]
  rows: string[][]
  caption?: string | null
}

export interface DocumentSection {
  id: string
  heading: string
  content: string
  bullets: string[]
  table: DocumentTable | null
}

export interface SignatureBlock {
  party_label: string
  role?: string | null
  fields: string[]
}

export interface GenerationMeta {
  source: GenerationSource
  model?: string | null
  generated_at?: string | null
  disclaimer?: string | null
}

export interface DocumentContent {
  title: string
  subtitle?: string | null
  intro: string
  sections: DocumentSection[]
  signature_blocks: SignatureBlock[]
  disclaimer: string
  generation: GenerationMeta | null
}

export interface DocumentRecord {
  id: string
  title: string
  document_type: string
  status: DocumentStatus
  content: DocumentContent
  brand_id?: string | null
  jurisdiction?: string | null
  effective_date?: string | null
  created_at: string
  updated_at: string
}

export interface DocumentSummary {
  id: string
  title: string
  document_type: string
  status: DocumentStatus
  word_count: number
  section_count: number
  jurisdiction?: string | null
  effective_date?: string | null
  created_at: string
  updated_at: string
  generation_source?: GenerationSource | null
}

export interface PageMeta {
  total: number
  limit: number
  offset: number
}

export interface Paged<T> {
  items: T[]
  meta: PageMeta
}

export interface DocumentVersion {
  id: string
  document_id: string
  version_number: number
  label?: string | null
  content: DocumentContent
  created_at: string
}

export interface DashboardStats {
  total_documents: number
  drafts: number
  generated: number
  completed: number
  documents_this_month: number
}

export interface GenerationResponse {
  document: DocumentRecord
  generation_source: GenerationSource
  model?: string | null
  elapsed_ms: number
  warnings: string[]
}

export interface RewriteResponse {
  document: DocumentRecord
  section_index: number
  action: string
  version_number?: number | null
  warnings: string[]
}

export interface DocumentUpdatePayload {
  title?: string
  content?: DocumentContent
  status?: DocumentStatus
  brand_id?: string | null
  jurisdiction?: string | null
  effective_date?: string | null
  create_version?: boolean
  version_label?: string | null
}

export interface BrandProfile {
  id: string
  organization_name?: string | null
  logo_path?: string | null
  logo_url?: string | null
  address?: string | null
  email?: string | null
  phone?: string | null
  website?: string | null
  footer_text?: string | null
  created_at: string
}

export interface LogoUpload {
  id: string
  logo_path: string
  logo_url: string
  size_bytes: number
  content_type: string
}

export interface TemplateItem {
  id: string
  title: string
  slug: string
  description: string
  category: string
  icon: string
  estimated_minutes: number
  default_title: string
  suggested_sections: string[]
  suggested_clauses: string[]
  sample: boolean
  popular: boolean
  has_sample_data: boolean
}

export interface ClauseSuggestion {
  key: string
  title: string
  description: string
}

export interface SampleData {
  document_type: string
  label: string
  summary: string
  payload: GenerateRequest
}

export type AiMode = 'groq' | 'demo' | 'unconfigured'

export interface AiStatus {
  mode: AiMode
  configured: boolean
  model?: string | null
  demo_mode: boolean
  available: boolean
  message?: string | null
}

export interface HealthResponse {
  status: string
  app: string
  version: string
  environment: string
  database: string
  ai: AiStatus
  legal_disclaimer: string
}

export type RewriteAction =
  | 'rewrite_professional'
  | 'simplify'
  | 'more_formal'
  | 'expand'
  | 'shorten'
  | 'fix_grammar'
  | 'add_protection'
