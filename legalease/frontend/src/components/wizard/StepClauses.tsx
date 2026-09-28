import { AnimatePresence, motion } from 'framer-motion'
import { GripVertical, Plus, Sparkles, Trash2 } from 'lucide-react'
import { useState } from 'react'

import { Button } from '../ui/Button'
import { Field, Input, Textarea } from '../ui/Input'
import { Switch } from '../ui/Switch'
import type { ClauseDraft } from '../../store/wizardStore'
import { cn } from '../../utils/cn'
import { MAX_CLAUSE_DESCRIPTION } from '../../constants/limits'

interface Props {
  clauses: ClauseDraft[]
  suggestions: string[]
  errors: Record<number, string>
  onAdd: () => void
  onAddWithTitle: (title: string) => void
  onUpdate: (index: number, patch: Partial<ClauseDraft>) => void
  onRemove: (index: number) => void
}

export function StepClauses({
  clauses,
  suggestions,
  errors,
  onAdd,
  onAddWithTitle,
  onUpdate,
  onRemove,
}: Props) {
  const [showSuggestions, setShowSuggestions] = useState(true)

  const unused = suggestions.filter(
    (title) => !clauses.some((clause) => clause.title.toLowerCase() === title.toLowerCase()),
  )

  return (
    <div className="flex flex-col gap-5">
      <p className="text-sm leading-relaxed text-ivory-300/65">
        These become the sections of your document. Describe what each one should cover in
        plain language &mdash; the AI turns it into formal legal prose. Required clauses are
        always included; optional ones are used as guidance.
      </p>

      {unused.length ? (
        <div className="rounded-xl border border-navy-700 bg-navy-900/40 p-4">
          <button
            type="button"
            onClick={() => setShowSuggestions((v) => !v)}
            className="flex w-full items-center gap-2 text-left"
            aria-expanded={showSuggestions}
          >
            <Sparkles className="size-3.5 text-gold-400" aria-hidden />
            <span className="text-sm font-medium text-ivory-100">
              {unused.length} suggested {unused.length === 1 ? 'clause' : 'clauses'} for this
              template
            </span>
          </button>
          <AnimatePresence initial={false}>
            {showSuggestions ? (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.22 }}
                className="overflow-hidden"
              >
                <div className="mt-3 flex flex-wrap gap-2">
                  {unused.map((title) => (
                    <button
                      key={title}
                      type="button"
                      onClick={() => onAddWithTitle(title)}
                      className="rounded-full border border-navy-600 px-3 py-1.5 text-xs text-ivory-200/80 transition-colors hover:border-gold-500/50 hover:bg-gold-500/10 hover:text-gold-200"
                    >
                      <Plus className="mr-1 inline size-3" aria-hidden />
                      {title}
                    </button>
                  ))}
                </div>
              </motion.div>
            ) : null}
          </AnimatePresence>
        </div>
      ) : null}

      <div className="flex flex-col gap-3">
        <AnimatePresence initial={false}>
          {clauses.map((clause, index) => (
            <motion.div
              key={index}
              layout
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, height: 0, marginBottom: 0 }}
              transition={{ duration: 0.24 }}
              className={cn(
                'rounded-xl border p-4 transition-colors',
                errors[index] ? 'border-rose-500/45 bg-rose-500/5' : 'border-navy-700 bg-navy-900/35',
              )}
            >
              <div className="flex items-start gap-3">
                <GripVertical
                  className="mt-2.5 size-4 shrink-0 text-ivory-300/25"
                  aria-hidden
                />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-3">
                    <Input
                      value={clause.title}
                      maxLength={200}
                      placeholder="Section title, e.g. Payment terms"
                      aria-label={`Section ${index + 1} title`}
                      invalid={Boolean(errors[index])}
                      className="h-9 font-medium"
                      onChange={(event) => onUpdate(index, { title: event.target.value })}
                    />
                    <label className="flex shrink-0 items-center gap-2 text-xs text-ivory-300/70">
                      <Switch
                        checked={clause.is_required}
                        onCheckedChange={(checked) => onUpdate(index, { is_required: checked })}
                        aria-label={`Section ${index + 1} is required`}
                      />
                      Required
                    </label>
                    <Button
                      size="icon-sm"
                      variant="ghost"
                      aria-label={`Remove section ${index + 1}`}
                      className="shrink-0 text-ivory-300/50 hover:text-rose-300"
                      onClick={() => onRemove(index)}
                    >
                      <Trash2 aria-hidden />
                    </Button>
                  </div>

                  <Field
                    className="mt-3"
                    label="What should this section cover?"
                    error={errors[index]}
                    hint={`${clause.description.length} / ${MAX_CLAUSE_DESCRIPTION}`}
                  >
                    {(id, describedBy) => (
                      <Textarea
                        id={id}
                        value={clause.description}
                        rows={3}
                        maxLength={MAX_CLAUSE_DESCRIPTION}
                        aria-describedby={describedBy}
                        placeholder="e.g. Net 30 payment from the invoice date, with late fees after 15 days."
                        invalid={Boolean(errors[index])}
                        onChange={(event) => onUpdate(index, { description: event.target.value })}
                      />
                    )}
                  </Field>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      <Button variant="outline" onClick={onAdd}>
        <Plus aria-hidden />
        Add a section
      </Button>
    </div>
  )
}
