import { useQuery } from '@tanstack/react-query'

import { templatesApi } from '../services'
import type { ClauseSuggestion, SampleData, TemplateItem } from '../types/api'

export const TEMPLATE_CATEGORIES = [
  'All',
  'Employment',
  'Business',
  'Real Estate',
  'IP & Digital',
  'Finance',
  'Personal',
  'Education',
] as const

export function useTemplates(params: { search?: string; category?: string } = {}) {
  const query = useQuery({
    queryKey: ['templates', params] as const,
    queryFn: () => templatesApi.list(params),
    placeholderData: (previous) => previous,
    staleTime: 5 * 60_000,
  })

  const items: TemplateItem[] = query.data?.items ?? []

  return {
    ...query,
    templates: items,
    total: query.data?.total ?? 0,
    categories: query.data?.categories ?? [],
  }
}

export function useTemplate(id: string | undefined) {
  return useQuery({
    queryKey: ['templates', id] as const,
    queryFn: () => templatesApi.get(id as string),
    enabled: Boolean(id),
    staleTime: 5 * 60_000,
  })
}

export function useTemplateSample(id: string | undefined) {
  return useQuery({
    queryKey: ['templates', id, 'sample'] as const,
    queryFn: () => templatesApi.sample(id as string),
    enabled: Boolean(id),
    staleTime: 5 * 60_000,
  })
}

export function useClauseSuggestions() {
  const query = useQuery({
    queryKey: ['clauses'] as const,
    queryFn: templatesApi.clauses,
    staleTime: 10 * 60_000,
  })

  return { ...query, clauses: query.data?.items ?? [] as ClauseSuggestion[] }
}

export function useSampleData(id: string | undefined) {
  return useQuery({
    queryKey: ['templates', id, 'sample-data'] as const,
    queryFn: () => templatesApi.sample(id as string) as Promise<SampleData>,
    enabled: Boolean(id),
    staleTime: 10 * 60_000,
  })
}
