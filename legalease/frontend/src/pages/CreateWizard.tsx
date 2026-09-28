import { AnimatePresence, motion } from 'framer-motion'
import { ArrowLeft, ArrowRight, RotateCcw, Sparkles } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'

import { Stepper } from '../components/wizard/Stepper'
import { StepBranding } from '../components/wizard/StepBranding'
import { StepClauses } from '../components/wizard/StepClauses'
import { StepParties } from '../components/wizard/StepParties'
import { StepReview, type ReviewBlock } from '../components/wizard/StepReview'
import { StepTerms } from '../components/wizard/StepTerms'
import { StepType } from '../components/wizard/StepType'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { WIZARD_STEPS } from '../constants/legal'
import { MAX_CLAUSES, MAX_PARTIES, MAX_TITLE } from '../constants/limits'
import { useTemplateSample, useTemplate, useTemplates } from '../hooks/useTemplates'
import { ApiError, documentsApi } from '../services'
import {
  toGenerateRequest,
  useWizardStore,
  type ClauseDraft,
  type PartyDraft,
} from '../store/wizardStore'
import type { TemplateItem } from '../types/api'

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function CreateWizard() {
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()
  const templateParam = params.get('template')

  const wizard = useWizardStore()
  const {
    step,
    documentType,
    title,
    parties,
    clauses,
    clauseSuggestions,
    effectiveDate,
    expiryDate,
    jurisdiction,
    branding,
    additionalInstructions,
    disclaimerAccepted,
  } = wizard

  const [partyErrors, setPartyErrors] = useState<Record<number, string>>({})
  const [clauseErrors, setClauseErrors] = useState<Record<number, string>>({})
  const [dateError, setDateError] = useState<string | undefined>()
  const [titleError, setTitleError] = useState<string | undefined>()
  const [generating, setGenerating] = useState(false)
  const headingRef = useRef<HTMLHeadingElement>(null)
  const attempted = useRef(false)

  const { data: template } = useTemplate(documentType ?? undefined)
  const { templates } = useTemplates({})

  /* -------------------------------------------------- deep-link a template */
  useEffect(() => {
    if (!templateParam || wizard.documentType === templateParam) return
    const match = templates.find((t) => t.id === templateParam)
    if (match) wizard.setDocumentType(match.id, match.default_title, match.suggested_sections, match.suggested_clauses)
  }, [templateParam, templates, wizard])

  useEffect(() => {
    if (templateParam) setParams({}, { replace: true })
  }, [templateParam, setParams])

  /* ------------------------------------------------------ step validation */
  function validateStep(index: number): string[] {
    const problems: string[] = []

    if (index === 0) {
      if (!documentType) problems.push('Choose a document type.')
      if (!title.trim()) {
        setTitleError('Give the document a title.')
        problems.push('Give the document a title.')
      } else if (title.length > MAX_TITLE) {
        problems.push(`The title must be ${MAX_TITLE} characters or fewer.`)
      } else {
        setTitleError(undefined)
      }
    }

    if (index === 1) {
      const errors: Record<number, string> = {}
      parties.forEach((party, i) => {
        if (!party.name.trim()) errors[i] = 'A legal name is required.'
        else if (party.name.length > 200) errors[i] = 'That name is too long.'
        else if (party.email && !EMAIL_PATTERN.test(party.email))
          errors[i] = 'That email address is not valid.'
      })
      if (parties.length > MAX_PARTIES) {
        problems.push(`A document can have at most ${MAX_PARTIES} parties.`)
      }
      if (Object.keys(errors).length) problems.push('Every party needs a valid name and role.')
      setPartyErrors(errors)
    }

    if (index === 2) {
      const errors: Record<number, string> = {}
      clauses.forEach((clause, i) => {
        if (!clause.title.trim()) errors[i] = 'Every section needs a title.'
        else if (!clause.description.trim())
          errors[i] = 'Describe what this section should cover.'
      })
      if (clauses.length > MAX_CLAUSES)
        problems.push(`A document can have at most ${MAX_CLAUSES} sections.`)
      if (Object.keys(errors).length)
        problems.push('Every section needs a title and a description.')
      setClauseErrors(errors)
    }

    if (index === 3) {
      if (effectiveDate && expiryDate && expiryDate < effectiveDate) {
        setDateError('The end date must be after the effective date.')
        problems.push('The end date must be after the effective date.')
      } else {
        setDateError(undefined)
      }
    }

    return problems
  }

  const review = useMemo<ReviewBlock>(
    () => ({
      documentType,
      template,
      title,
      partyRows: parties
        .filter((party) => party.name.trim() || party.role.trim())
        .map((party) => ({
          name: party.name || 'Unnamed party',
          role: party.role,
          organization: party.organization,
        })),
      clauseRows: clauses
        .filter((clause) => clause.title.trim() || clause.description.trim())
        .map((clause) => ({
          title: clause.title,
          required: clause.is_required,
          detail: clause.description,
        })),
      effectiveDate,
      expiryDate,
      jurisdiction,
      organisation: branding.organization_name ?? null,
      instructions: additionalInstructions,
      disclaimerAccepted,
    }),
    [
      documentType,
      template,
      title,
      parties,
      clauses,
      effectiveDate,
      expiryDate,
      jurisdiction,
      branding.organization_name,
      additionalInstructions,
      disclaimerAccepted,
    ],
  )

  const finalProblems = useMemo(() => {
    const problems: string[] = []
    if (!documentType) problems.push('Choose a document type.')
    if (!title.trim()) problems.push('Give the document a title.')
    if (!parties.some((party) => party.name.trim())) problems.push('Add at least one named party.')
    if (!clauses.some((clause) => clause.title.trim() && clause.description.trim()))
      problems.push('At least one section needs a title and a description.')
    if (effectiveDate && expiryDate && expiryDate < effectiveDate)
      problems.push('The end date must be after the effective date.')
    if (!disclaimerAccepted) problems.push('Accept the legal disclaimer to continue.')
    return problems
  }, [
    documentType,
    title,
    parties,
    clauses,
    effectiveDate,
    expiryDate,
    disclaimerAccepted,
  ])

  /* --------------------------------------------------------------- actions */
  function goTo(index: number) {
    wizard.setStep(Math.max(0, Math.min(index, WIZARD_STEPS.length - 1)))
    headingRef.current?.focus()
  }

  function goNext() {
    if (attempted.current || validateStep(step).length === 0) {
      attempted.current = false
      goTo(step + 1)
    } else {
      attempted.current = true
    }
  }

  async function generate() {
    if (finalProblems.length) {
      setGenerating(false)
      return
    }
    setGenerating(true)
    try {
      const payload = toGenerateRequest(wizard)
      const result = await documentsApi.generate(payload)
      if (result.warnings.length) {
        result.warnings.forEach((warning) => toast.warning(warning))
      }
      toast.success(
        result.generation_source === 'demo'
          ? 'Draft generated in demo mode'
          : `Draft generated in ${(result.elapsed_ms / 1000).toFixed(1)}s`,
      )
      wizard.reset()
      navigate(`/document/${result.document.id}`)
    } catch (error) {
      toast.error(
        error instanceof ApiError ? error.userMessage : 'The document could not be generated.',
      )
    } finally {
      setGenerating(false)
    }
  }

  function selectTemplate(selected: TemplateItem) {
    wizard.setDocumentType(
      selected.id,
      selected.default_title,
      selected.suggested_sections,
      selected.suggested_clauses,
    )
    setTitleError(undefined)
  }

  function loadSample(templateId: string) {
    // Sample data is fetched by the StepType child; this only records intent.
    setSampleTarget(templateId)
  }

  const [sampleTarget, setSampleTarget] = useState<string | null>(null)
  const { data: sample } = useTemplateSample(sampleTarget ?? undefined)

  useEffect(() => {
    if (!sample || sampleTarget !== documentType) return
    wizard.loadSample(sample.payload, sample.label)
  }, [sample, sampleTarget, documentType, wizard])

  const stepDef = WIZARD_STEPS[step]
  const isLast = step === WIZARD_STEPS.length - 1

  return (
    <div className="flex flex-col gap-7">
      <header>
        <p className="text-[0.6875rem] font-medium tracking-[0.18em] text-gold-400/85 uppercase">
          New document
        </p>
        <h1 className="mt-2 font-display text-2xl font-semibold tracking-tight text-ivory-50 sm:text-3xl">
          Draft a legal document
        </h1>
        <p className="mt-2 text-sm text-ivory-300/65">
          Six guided steps. Nothing is sent anywhere except your local backend.
        </p>
      </header>

      <Stepper
        current={step}
        maxVisited={step}
        onSelect={goTo}
        isComplete={(index) => index < step}
      />

      <Card className="overflow-hidden">
        <div className="border-b border-navy-700/70 px-6 py-5">
          <p className="text-xs font-medium tracking-[0.09em] text-gold-400/85 uppercase">
            Step {step + 1} of {WIZARD_STEPS.length}
          </p>
          <h2
            ref={headingRef}
            tabIndex={-1}
            className="mt-1.5 font-display text-xl font-semibold text-ivory-50 outline-none"
          >
            {stepDef.title}
          </h2>
          <p className="mt-1 text-sm text-ivory-300/60">{stepDef.description}</p>
        </div>

        <div className="p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={stepDef.id}
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -16 }}
              transition={{ duration: 0.24, ease: [0.22, 1, 0.36, 1] }}
            >
              {step === 0 ? (
                <StepType
                  selectedId={documentType}
                  title={title}
                  titleError={titleError}
                  onSelect={selectTemplate}
                  onTitleChange={(value) => {
                    wizard.setTitle(value)
                    if (value.trim()) setTitleError(undefined)
                  }}
                  onLoadSample={loadSample}
                  sampleLoadedFor={sampleTarget === documentType ? sampleTarget : null}
                />
              ) : null}

              {step === 1 ? (
                <StepParties
                  parties={parties}
                  errors={partyErrors}
                  onAdd={() => wizard.addParty()}
                  onUpdate={wizard.updateParty}
                  onRemove={wizard.removeParty}
                />
              ) : null}

              {step === 2 ? (
                <StepClauses
                  clauses={clauses}
                  suggestions={clauseSuggestions}
                  errors={clauseErrors}
                  onAdd={() => wizard.addClause()}
                  onAddWithTitle={wizard.addClauseWithTitle}
                  onUpdate={wizard.updateClause}
                  onRemove={wizard.removeClause}
                />
              ) : null}

              {step === 3 ? (
                <StepTerms
                  effectiveDate={effectiveDate}
                  expiryDate={expiryDate}
                  jurisdiction={jurisdiction}
                  dateError={dateError}
                  onDates={wizard.setDates}
                  onJurisdiction={wizard.setJurisdiction}
                />
              ) : null}

              {step === 4 ? (
                <StepBranding
                  branding={branding}
                  instructions={additionalInstructions}
                  title={title}
                  onBranding={wizard.setBranding}
                  onInstructions={wizard.setInstructions}
                  onTitleChange={wizard.setTitle}
                />
              ) : null}

              {step === 5 ? (
                <StepReview
                  data={review}
                  problems={finalProblems}
                  generating={generating}
                  onAccept={wizard.setDisclaimerAccepted}
                  onEditStep={goTo}
                  onGenerate={() => void generate()}
                />
              ) : null}
            </motion.div>
          </AnimatePresence>
        </div>

        <div className="flex flex-col-reverse gap-3 border-t border-navy-700/70 bg-navy-900/30 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex gap-2">
            <Button
              variant="ghost"
              onClick={() => goTo(step - 1)}
              disabled={step === 0 || generating}
            >
              <ArrowLeft aria-hidden />
              Back
            </Button>
            {step > 0 ? (
              <Button
                variant="ghost"
                className="text-ivory-300/60"
                onClick={() => {
                  if (window.confirm('Clear every answer and start over?')) {
                    wizard.reset()
                    goTo(0)
                  }
                }}
                disabled={generating}
              >
                <RotateCcw aria-hidden />
                Reset
              </Button>
            ) : null}
          </div>

          {isLast ? (
            <Button
              size="md"
              loading={generating}
              disabled={!disclaimerAccepted || finalProblems.length > 0}
              onClick={() => void generate()}
            >
              <Sparkles aria-hidden />
              Generate document
            </Button>
          ) : (
            <Button onClick={goNext} disabled={generating}>
              Continue
              <ArrowRight aria-hidden />
            </Button>
          )}
        </div>
      </Card>
    </div>
  )
}

export type { ClauseDraft, PartyDraft }
