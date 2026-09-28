import { motion } from 'framer-motion'
import { ArrowRight, Clock, Layers, Search, Sparkles } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'

import { templateIcon } from '../components/icons'
import { LegalDisclaimer } from '../components/layout/Disclaimer'
import { Alert, EmptyState } from '../components/ui/Alert'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Field, Input } from '../components/ui/Input'
import { Skeleton } from '../components/ui/Skeleton'
import { useTemplates } from '../hooks/useTemplates'
import { useDebouncedValue } from '../hooks/useDebounce'
import { ApiError } from '../services'
import { pluralize } from '../utils/format'
import { cn } from '../utils/cn'

export function Templates() {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('All')
  const debouncedSearch = useDebouncedValue(search, 250)

  const query = useTemplates({
    search: debouncedSearch || undefined,
    category: category === 'All' ? undefined : category,
  })

  const categories = ['All', ...new Set(query.categories)]
  const templates = query.templates

  return (
    <div className="flex flex-col gap-8">
      <header className="max-w-2xl">
        <p className="text-[0.6875rem] font-medium tracking-[0.18em] text-gold-400/85 uppercase">
          Library
        </p>
        <h1 className="mt-2 font-display text-2xl font-semibold tracking-tight text-ivory-50 sm:text-3xl">
          Document templates
        </h1>
        <p className="mt-2 text-sm leading-relaxed text-ivory-300/65">
          Every template arrives with suggested sections and clauses already selected. Pick one
          to open the guided intake.
        </p>
      </header>

      <Card className="p-4">
        <div className="grid gap-3 sm:grid-cols-[minmax(0,20rem)_1fr]">
          <Field label="Search templates">
            {(id) => (
              <div className="relative">
                <Search
                  className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-ivory-300/40"
                  aria-hidden
                />
                <Input
                  id={id}
                  type="search"
                  value={search}
                  placeholder="e.g. NDA, lease, invoice…"
                  className="pl-9"
                  onChange={(event) => setSearch(event.target.value)}
                />
              </div>
            )}
          </Field>

          <div>
            <p className="mb-2 text-xs font-medium tracking-[0.09em] text-ivory-300/80 uppercase">
              Category
            </p>
            <div className="flex flex-wrap gap-2">
              {categories.map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => setCategory(item)}
                  aria-pressed={category === item}
                  className={cn(
                    'rounded-full border px-3.5 py-1.5 text-xs font-medium transition-all duration-200',
                    category === item
                      ? 'border-gold-500/50 bg-gold-500/12 text-gold-200'
                      : 'border-navy-600 text-ivory-200/70 hover:border-navy-500 hover:text-ivory-50',
                  )}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {query.isError ? (
        <Alert variant="danger" title="Could not load templates">
          {query.error instanceof ApiError
            ? query.error.userMessage
            : 'The template catalog is served by the backend on port 8000.'}
        </Alert>
      ) : query.isLoading ? (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }, (_, i) => (
            <Skeleton key={i} className="h-56 rounded-card" />
          ))}
        </div>
      ) : templates.length ? (
        <>
          <p className="text-xs text-ivory-300/45">
            {pluralize(query.total, 'template')}
            {category !== 'All' || debouncedSearch ? ' matching your filters' : ''}
          </p>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {templates.map((template, index) => {
              const Icon = templateIcon(template.icon)
              return (
                <motion.div
                  key={template.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.32, delay: Math.min(index, 8) * 0.035 }}
                >
                  <Link
                    to={`/create?template=${template.id}`}
                    className="group block h-full rounded-card focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold-400"
                  >
                    <Card className="flex h-full flex-col p-6 group-hover:border-gold-500/40">
                      <div className="flex items-start justify-between gap-3">
                        <span className="flex size-11 items-center justify-center rounded-xl border border-navy-600 bg-navy-800/70 text-gold-400">
                          <Icon className="size-5" aria-hidden />
                        </span>
                        <div className="flex flex-col items-end gap-1.5">
                          {template.popular ? (
                            <Badge variant="gold" size="sm">
                              Popular
                            </Badge>
                          ) : null}
                          {template.has_sample_data ? (
                            <Badge variant="info" size="sm">
                              <Sparkles className="size-2.5" aria-hidden />
                              Sample
                            </Badge>
                          ) : null}
                        </div>
                      </div>

                      <h2 className="mt-5 font-display text-base font-semibold text-ivory-50">
                        {template.title}
                      </h2>
                      <p className="mt-2 flex-1 text-sm leading-relaxed text-ivory-300/60">
                        {template.description}
                      </p>

                      {template.suggested_sections.length ? (
                        <div className="mt-4">
                          <p className="flex items-center gap-1.5 text-[0.6875rem] tracking-wide text-ivory-300/45 uppercase">
                            <Layers className="size-3" aria-hidden />
                            {template.suggested_sections.length} suggested sections
                          </p>
                          <ul className="mt-2 flex flex-wrap gap-1.5">
                            {template.suggested_sections.slice(0, 3).map((section) => (
                              <li
                                key={section}
                                className="rounded border border-navy-700 bg-navy-900/60 px-1.5 py-0.5 text-[0.625rem] text-ivory-300/60"
                              >
                                {section}
                              </li>
                            ))}
                            {template.suggested_sections.length > 3 ? (
                              <li className="px-1 py-0.5 text-[0.625rem] text-ivory-300/40">
                                +{template.suggested_sections.length - 3}
                              </li>
                            ) : null}
                          </ul>
                        </div>
                      ) : null}

                      <div className="mt-5 flex items-center justify-between border-t border-navy-700/60 pt-4">
                        <span className="inline-flex items-center gap-1.5 text-[0.6875rem] text-ivory-300/45">
                          <Clock className="size-3" aria-hidden />~{template.estimated_minutes} min
                        </span>
                        <span className="inline-flex items-center gap-1 text-xs font-medium text-gold-300 transition-transform group-hover:translate-x-0.5">
                          Use template
                          <ArrowRight className="size-3.5" aria-hidden />
                        </span>
                      </div>
                    </Card>
                  </Link>
                </motion.div>
              )
            })}
          </div>
        </>
      ) : (
        <EmptyState
          icon={Search}
          title="No templates match that search"
          description="Try a broader term, or clear the category filter to see all eighteen document types."
          action={
            <Button
              variant="outline"
              onClick={() => {
                setSearch('')
                setCategory('All')
              }}
            >
              Reset filters
            </Button>
          }
        />
      )}

      <LegalDisclaimer className="mt-4" />
    </div>
  )
}
