import { CalendarClock, MapPin } from 'lucide-react'

import { Card } from '../ui/Card'
import { Field, Input } from '../ui/Input'
import type { Jurisdiction } from '../../types/api'
import { formatDate } from '../../utils/format'

interface Props {
  effectiveDate: string
  expiryDate: string
  jurisdiction: Jurisdiction
  dateError?: string
  onDates: (effective: string, expiry: string) => void
  onJurisdiction: (patch: Jurisdiction) => void
}

export function StepTerms({
  effectiveDate,
  expiryDate,
  jurisdiction,
  dateError,
  onDates,
  onJurisdiction,
}: Props) {
  const today = new Date().toISOString().slice(0, 10)
  const expiryBeforeEffective = Boolean(
    effectiveDate && expiryDate && expiryDate < effectiveDate,
  )

  return (
    <div className="flex flex-col gap-6">
      <Card className="p-5">
        <div className="flex items-center gap-2.5">
          <span className="flex size-8 items-center justify-center rounded-lg border border-navy-600 bg-navy-800/70 text-gold-400">
            <CalendarClock className="size-4" aria-hidden />
          </span>
          <h3 className="text-sm font-medium text-ivory-50">Key dates</h3>
        </div>

        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <Field label="Effective date" hint="Leave blank to leave it open.">
            {(id) => (
              <Input
                id={id}
                type="date"
                value={effectiveDate}
                onChange={(event) => onDates(event.target.value, expiryDate)}
              />
            )}
          </Field>

          <Field
            label="Expiry / end date"
            error={expiryBeforeEffective ? 'The end date must be after the effective date.' : dateError}
          >
            {(id, describedBy) => (
              <Input
                id={id}
                type="date"
                min={effectiveDate || today}
                value={expiryDate}
                aria-describedby={describedBy}
                invalid={expiryBeforeEffective || Boolean(dateError)}
                onChange={(event) => onDates(effectiveDate, event.target.value)}
              />
            )}
          </Field>
        </div>

        {effectiveDate || expiryDate ? (
          <p className="mt-4 text-xs text-ivory-300/50">
            The document will read:{' '}
            <span className="text-ivory-200/80">
              effective {formatDate(effectiveDate || null)}
              {expiryDate ? ` until ${formatDate(expiryDate)}` : ''}
            </span>
            .
          </p>
        ) : null}
      </Card>

      <Card className="p-5">
        <div className="flex items-center gap-2.5">
          <span className="flex size-8 items-center justify-center rounded-lg border border-navy-600 bg-navy-800/70 text-gold-400">
            <MapPin className="size-4" aria-hidden />
          </span>
          <h3 className="text-sm font-medium text-ivory-50">Jurisdiction</h3>
        </div>
        <p className="mt-2 text-xs leading-relaxed text-ivory-300/55">
          Used for the governing-law clause. Omitting it produces a neutral clause that defers
          the choice, which is often the right answer for a first draft.
        </p>

        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <Field label="Governing law" className="sm:col-span-2" hint="e.g. the laws of the State of New York">
            {(id) => (
              <Input
                id={id}
                value={jurisdiction.governing_law ?? ''}
                maxLength={300}
                placeholder="e.g. State of Delaware, USA"
                onChange={(event) => onJurisdiction({ governing_law: event.target.value })}
              />
            )}
          </Field>

          <Field label="Country">
            {(id) => (
              <Input
                id={id}
                value={jurisdiction.country ?? ''}
                maxLength={120}
                placeholder="e.g. United States"
                onChange={(event) => onJurisdiction({ country: event.target.value })}
              />
            )}
          </Field>

          <Field label="State / province">
            {(id) => (
              <Input
                id={id}
                value={jurisdiction.state ?? ''}
                maxLength={120}
                placeholder="e.g. California"
                onChange={(event) => onJurisdiction({ state: event.target.value })}
              />
            )}
          </Field>

          <Field label="City" className="sm:col-span-2">
            {(id) => (
              <Input
                id={id}
                value={jurisdiction.city ?? ''}
                maxLength={120}
                placeholder="e.g. San Francisco"
                onChange={(event) => onJurisdiction({ city: event.target.value })}
              />
            )}
          </Field>
        </div>
      </Card>
    </div>
  )
}
