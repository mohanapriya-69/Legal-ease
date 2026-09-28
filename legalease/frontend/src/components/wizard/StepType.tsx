import { motion } from 'framer-motion'
import { Check, Sparkles, Wand2 } from 'lucide-react'
import { useState } from 'react'

import { templateIcon } from '../icons'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { Field, Input } from '../ui/Input'
import { Skeleton } from '../ui/Skeleton'
import { Tooltip } from '../ui/Tooltip'
import { useTemplateSample, useTemplates } from '../../hooks/useTemplates'
import { toast } from 'sonner'
import type { TemplateItem } from '../../types/api'
import { cn } from '../../utils/cn'

interface Props {
  selectedId: string | null
  title: string
  titleError?: string
  onSelect: (template: TemplateItem) => void
  onTitleChange: (title: string) => void
  onLoadSample: (templateId: string) => void
  sampleLoadedFor: string | null
}

export function StepType({
  selectedId,
  title,
  titleError,
  onSelect,
  onTitleChange,
  onLoadSample,
  sampleLoadedFor,
}: Props) {
  const [search, setSearch] = useState('')
  const { templates, isLoading } = useTemplates({ search: search || undefined })
  const selected = templates.find((template) => template.id === selectedId)

  return (
    <div className="flex flex-col gap-6">
      <Field
        label="Document title"
        required
        error={titleError}
        hint="You can rename this later in the editor."
      >
        {(id, describedBy) => (
          <Input
            id={id}
            value={title}
            maxLength={300}
            aria-describedby={describedBy}
            invalid={Boolean(titleError)}
            placeholder={selected?.default_title ?? 'e.g. Independent Contractor Agreement'}
            onChange={(event) => onTitleChange(event.target.value)}
          />
        )}
      </Field>

      <div>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs font-medium tracking-[0.09em] text-ivory-300/80 uppercase">
            Choose a document type
          </p>
          <Input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Filter templates…"
            className="h-9 w-full max-w-56 text-sm"
            aria-label="Filter templates"
          />
        </div>

        {isLoading ? (
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {Array.from({ length: 6 }, (_, i) => (
              <Skeleton key={i} className="h-24 rounded-xl" />
            ))}
          </div>
        ) : (
          <div className="mt-4 grid max-h-[26rem] gap-3 overflow-y-auto pr-1 sm:grid-cols-2">
            {templates.map((template) => {
              const Icon = templateIcon(template.icon)
              const active = template.id === selectedId
              return (
                <button
                  key={template.id}
                  type="button"
                  onClick={() => onSelect(template)}
                  aria-pressed={active}
                  className={cn(
                    'group relative flex items-start gap-3.5 rounded-xl border p-4 text-left transition-all duration-200',
                    active
                      ? 'border-gold-500/55 bg-gold-500/8'
                      : 'border-navy-700 bg-navy-900/40 hover:border-navy-500 hover:bg-navy-850/60',
                  )}
                >
                  <span
                    className={cn(
                      'flex size-9 shrink-0 items-center justify-center rounded-lg border transition-colors',
                      active
                        ? 'border-gold-500/40 bg-navy-800 text-gold-300'
                        : 'border-navy-600 bg-navy-800/60 text-ivory-300/70 group-hover:text-gold-400',
                    )}
                  >
                    <Icon className="size-[1.05rem]" aria-hidden />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="flex items-center gap-2">
                      <span className="truncate text-sm font-medium text-ivory-50">
                        {template.title}
                      </span>
                      {template.popular ? (
                        <Badge variant="gold" size="sm">
                          Popular
                        </Badge>
                      ) : null}
                    </span>
                    <span className="mt-1 line-clamp-2 block text-xs leading-relaxed text-ivory-300/55">
                      {template.description}
                    </span>
                    <span className="mt-2 block text-[0.625rem] tracking-wide text-ivory-300/40">
                      {template.suggested_sections.length} sections &middot; ~
                      {template.estimated_minutes} min
                    </span>
                  </span>
                  {active ? (
                    <Check
                      className="absolute top-3 right-3 size-4 text-gold-400"
                      aria-hidden
                    />
                  ) : null}
                </button>
              )
            })}
          </div>
        )}
      </div>

      {selected ? <SampleLoader template={selected} onLoad={onLoadSample} current={sampleLoadedFor} /> : null}
    </div>
  )
}

function SampleLoader({
  template,
  onLoad,
  current,
}: {
  template: TemplateItem
  onLoad: (templateId: string) => void
  current: string | null
}) {
  // Hook first, so the order is stable even for templates without a sample.
  const { data, isLoading } = useTemplateSample(
    template.has_sample_data ? template.id : undefined,
  )

  if (!template.has_sample_data) {
    return (
      <p className="rounded-xl border border-navy-700 bg-navy-900/40 p-4 text-xs leading-relaxed text-ivory-300/55">
        This template has no pre-filled example, but every section below is prefilled with
        suggested clauses.
      </p>
    )
  }

  const loaded = current === template.id

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-gold-500/25 bg-gold-500/6 p-4"
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <p className="flex items-center gap-1.5 text-sm font-medium text-gold-200">
            <Wand2 className="size-4" aria-hidden />
            Try it with example data
          </p>
          {isLoading ? (
            <Skeleton className="mt-2 h-4 w-2/3" />
          ) : data ? (
            <>
              <p className="mt-1.5 text-sm text-ivory-200/80">{data.summary}</p>
              <p className="mt-1 text-xs text-ivory-300/50">
                Fills every step with &ldquo;{data.label}&rdquo; so you can see the finished
                document first, then edit it.
              </p>
            </>
          ) : null}
        </div>
        <Button
          size="sm"
          variant={loaded ? 'ghost' : 'primary'}
          disabled={isLoading}
          onClick={() => {
            onLoad(template.id)
            toast.success(`Loaded example: ${data?.label ?? template.title}`)
          }}
        >
          <Sparkles aria-hidden />
          {loaded ? 'Reload example' : 'Load example'}
        </Button>
      </div>
      {loaded ? (
        <Tooltip label="Example data replaced the fields below. Edit anything you like.">
          <p className="mt-3 text-[0.6875rem] text-ivory-300/45">Example data is now loaded.</p>
        </Tooltip>
      ) : null}
    </motion.div>
  )
}
