import { motion } from 'framer-motion'
import { Plus, Trash2, UserRound } from 'lucide-react'

import { Button } from '../ui/Button'
import { Field, Input, Textarea } from '../ui/Input'
import type { PartyDraft } from '../../store/wizardStore'
import { cn } from '../../utils/cn'

interface Props {
  parties: PartyDraft[]
  errors: Record<number, string>
  onAdd: () => void
  onUpdate: (index: number, patch: Partial<PartyDraft>) => void
  onRemove: (index: number) => void
}

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function StepParties({ parties, errors, onAdd, onUpdate, onRemove }: Props) {
  return (
    <div className="flex flex-col gap-5">
      <p className="text-sm leading-relaxed text-ivory-300/65">
        Add each person or company that will sign. The name and role are used in the opening
        paragraphs and the signature blocks, so use the legal names exactly as they should
        appear on the document.
      </p>

      <div className="flex flex-col gap-4">
        {parties.map((party, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.28, delay: Math.min(index, 4) * 0.05 }}
            className={cn(
              'rounded-card border p-5 transition-colors',
              errors[index]
                ? 'border-rose-500/45 bg-rose-500/5'
                : 'border-navy-700 bg-navy-900/35',
            )}
          >
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <span className="flex size-8 items-center justify-center rounded-lg border border-navy-600 bg-navy-800/70 text-ivory-300/70">
                  <UserRound className="size-4" aria-hidden />
                </span>
                <h3 className="text-sm font-medium text-ivory-50">
                  {party.role || `Party ${index + 1}`}
                </h3>
              </div>
              <Button
                size="icon-sm"
                variant="ghost"
                aria-label={`Remove ${party.role || `party ${index + 1}`}`}
                disabled={parties.length <= 1}
                onClick={() => onRemove(index)}
                className="text-ivory-300/50 hover:text-rose-300"
              >
                <Trash2 aria-hidden />
              </Button>
            </div>

            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <Field label="Full legal name" required error={errors[index]}>
                {(id) => (
                  <Input
                    id={id}
                    value={party.name}
                    maxLength={200}
                    placeholder="e.g. Northwind Studio LLC"
                    invalid={Boolean(errors[index])}
                    onChange={(event) => onUpdate(index, { name: event.target.value })}
                  />
                )}
              </Field>

              <Field label="Role in the agreement" required hint="e.g. Client, Contractor, Landlord">
                {(id) => (
                  <Input
                    id={id}
                    value={party.role}
                    maxLength={120}
                    placeholder="e.g. Service Provider"
                    onChange={(event) => onUpdate(index, { role: event.target.value })}
                  />
                )}
              </Field>

              <Field label="Organisation" className="sm:col-span-2">
                {(id) => (
                  <Input
                    id={id}
                    value={party.organization}
                    maxLength={200}
                    placeholder="Registered company name, if different from the legal name"
                    onChange={(event) => onUpdate(index, { organization: event.target.value })}
                  />
                )}
              </Field>

              <Field label="Address" className="sm:col-span-2">
                {(id) => (
                  <Textarea
                    id={id}
                    value={party.address}
                    maxLength={1000}
                    rows={2}
                    placeholder="Street, city, postal code, country"
                    onChange={(event) => onUpdate(index, { address: event.target.value })}
                  />
                )}
              </Field>

              <Field
                label="Email"
                error={party.email && !EMAIL_PATTERN.test(party.email) ? 'Enter a valid email address.' : undefined}
              >
                {(id, describedBy) => (
                  <Input
                    id={id}
                    type="email"
                    value={party.email}
                    maxLength={320}
                    aria-describedby={describedBy}
                    placeholder="name@example.com"
                    invalid={Boolean(party.email && !EMAIL_PATTERN.test(party.email))}
                    onChange={(event) => onUpdate(index, { email: event.target.value })}
                  />
                )}
              </Field>

              <Field label="Phone">
                {(id) => (
                  <Input
                    id={id}
                    type="tel"
                    value={party.phone}
                    maxLength={60}
                    placeholder="+1 555 0100"
                    onChange={(event) => onUpdate(index, { phone: event.target.value })}
                  />
                )}
              </Field>
            </div>
          </motion.div>
        ))}
      </div>

      <Button variant="outline" onClick={onAdd}>
        <Plus aria-hidden />
        Add another party
      </Button>
    </div>
  )
}
