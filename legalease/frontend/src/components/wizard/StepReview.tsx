import { AlertCircle, Check, FileText, Users } from 'lucide-react'

import { DisclaimerAcknowledgement } from '../layout/Disclaimer'
import { Alert } from '../ui/Alert'
import { Button } from '../ui/Button'
import { Card } from '../ui/Card'
import { AiModePill } from '../layout/AiStatusBanner'
import { useAiStatus } from '../../hooks/useAiStatus'
import type { Jurisdiction, TemplateItem } from '../../types/api'
import { formatDate } from '../../utils/format'

export interface ReviewBlock {
  documentType: string | null
  template?: TemplateItem
  title: string
  partyRows: Array<{ name: string; role: string; organization: string }>
  clauseRows: Array<{ title: string; required: boolean; detail: string }>
  effectiveDate: string
  expiryDate: string
  jurisdiction: Jurisdiction
  organisation: string | null
  instructions: string
  disclaimerAccepted: boolean
}

interface Props {
  data: ReviewBlock
  onAccept: (value: boolean) => void
  onEditStep: (index: number) => void
  onGenerate: () => void
  generating: boolean
  problems: string[]
}

export function StepReview({
  data,
  onAccept,
  onEditStep,
  onGenerate,
  generating,
  problems,
}: Props) {
  const { isDemo, isUnavailable, status } = useAiStatus()

  return (
    <div className="flex flex-col gap-6">
      {problems.length ? (
        <Alert variant="danger" title="Fix these before generating">
          <ul className="mt-1 flex flex-col gap-1.5">
            {problems.map((problem) => (
              <li key={problem} className="flex items-start gap-2">
                <AlertCircle className="mt-0.5 size-3.5 shrink-0" aria-hidden />
                {problem}
              </li>
            ))}
          </ul>
        </Alert>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <SummaryCard title="Document" stepIndex={0} onEdit={onEditStep} icon={FileText}>
          <Row label="Type" value={data.template?.title ?? data.documentType ?? 'â€”'} />
          <Row label="Title" value={data.title || 'Untitled'} />
          <Row
            label="Sections requested"
            value={String(data.clauseRows.length)}
          />
        </SummaryCard>

        <SummaryCard title="Parties" stepIndex={1} onEdit={onEditStep} icon={Users}>
          {data.partyRows.length ? (
            data.partyRows.map((party, index) => (
              <Row
                key={`${party.name}-${index}`}
                label={party.role || `Party ${index + 1}`}
                value={party.organization ? `${party.name} (${party.organization})` : party.name}
              />
            ))
          ) : (
            <Row label="â€”" value="No parties added" />
          )}
        </SummaryCard>

        <SummaryCard title="Sections" stepIndex={2} onEdit={onEditStep} icon={FileText}>
          <ul className="mt-1 flex flex-col gap-1.5">
            {data.clauseRows.map((clause, index) => (
              <li key={`${clause.title}-${index}`} className="flex items-start gap-2 text-sm">
                <Check
                  className={clause.required ? 'mt-0.5 size-3.5 text-gold-400' : 'mt-0.5 size-3.5 text-ivory-300/30'}
                  aria-hidden
                />
                <span className="min-w-0 flex-1 text-ivory-200/85">
                  {clause.title || `Section ${index + 1}`}
                  {clause.detail ? (
                    <span className="block truncate text-xs text-ivory-300/50">{clause.detail}</span>
                  ) : (
                    <span className="block text-xs text-ivory-300/35">
                      No description â€” the AI will use the title only.
                    </span>
                  )}
                </span>
              </li>
            ))}
          </ul>
        </SummaryCard>

        <SummaryCard title="Terms & branding" stepIndex={3} onEdit={onEditStep} icon={FileText}>
          <Row label="Effective" value={formatDate(data.effectiveDate || null)} />
          <Row label="Ends" value={formatDate(data.expiryDate || null)} />
          <Row
            label="Governing law"
            value={data.jurisdiction.governing_law || 'Not specified'}
          />
          <Row
            label="Location"
            value={
              [data.jurisdiction.city, data.jurisdiction.state, data.jurisdiction.country]
                .filter(Boolean)
                .join(', ') || 'Not specified'
            }
          />
          <Row label="Letterhead" value={data.organisation || 'None'} />
        </SummaryCard>
      </div>

      {data.instructions ? (
        <Card className="p-5">
          <h3 className="text-sm font-medium text-ivory-50">Additional instructions</h3>
          <p className="mt-2 text-sm leading-relaxed whitespace-pre-wrap text-ivory-300/70">
            {data.instructions}
          </p>
        </Card>
      ) : null}

      <div
        className={
          isUnavailable
            ? 'rounded-card border border-rose-500/35 bg-rose-500/6 p-5'
            : 'rounded-card border border-navy-700 bg-navy-900/35 p-5'
        }
      >
        <div className="flex flex-wrap items-center gap-3">
          <AiModePill />
          <p className="text-xs text-ivory-300/60">
            {isUnavailable
              ? 'AI is not configured. Generation will fail until GROQ_API_KEY is set.'
              : isDemo
                ? 'Demo mode: the backend will return a structured built-in draft without calling a live model.'
                : `A live model (${status.model}) will produce this draft. Response usually takes 10â€“40 seconds.`}
          </p>
        </div>
      </div>

      <DisclaimerAcknowledgement checked={data.disclaimerAccepted} onChange={onAccept} />

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs text-ivory-300/45">
          The document is saved to your local database before it opens in the editor.
        </p>
        <Button
          size="lg"
          loading={generating}
          disabled={!data.disclaimerAccepted || problems.length > 0}
          onClick={onGenerate}
        >
          Generate document
        </Button>
      </div>
    </div>
  )
}

/* ------------------------------------------------------------------ Parts */

function SummaryCard({
  title,
  icon: Icon,
  stepIndex,
  onEdit,
  children,
}: {
  title: string
  icon: typeof FileText
  stepIndex: number
  onEdit: (index: number) => void
  children: React.ReactNode
}) {
  return (
    <Card className="p-5">
      <div className="flex items-center justify-between gap-3">
        <h3 className="flex items-center gap-2 text-sm font-medium text-ivory-50">
          <Icon className="size-3.5 text-gold-400" aria-hidden />
          {title}
        </h3>
        <Button size="sm" variant="ghost" onClick={() => onEdit(stepIndex)}>
          Edit
        </Button>
      </div>
      <div className="mt-3 flex flex-col gap-2">{children}</div>
    </Card>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-3 text-sm">
      <span className="shrink-0 text-ivory-300/50">{label}</span>
      <span className="truncate text-right text-ivory-100" title={value}>
        {value}
      </span>
    </div>
  )
}
