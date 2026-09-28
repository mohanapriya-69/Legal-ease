/**
 * Copy that must stay identical to the backend.
 * Keep in sync with `backend/app/templates/disclaimer.py`.
 */

export const LEGAL_DISCLAIMER =
  'LegalEase provides AI-assisted drafting and general informational content. Generated documents are not a substitute for advice from a qualified legal professional. Laws vary by jurisdiction. Review important agreements with a licensed lawyer before signing.'

export const LEGAL_DISCLAIMER_SHORT =
  'AI-assisted draft. Not a substitute for advice from a qualified legal professional. Laws vary by jurisdiction.'

export const AI_MISSING_CONFIG_MESSAGE =
  'AI configuration is missing. Add GROQ_API_KEY to backend/.env.'

/** Wizard copy for each step. */
export const WIZARD_STEPS = [
  {
    id: 'type',
    title: 'Document type',
    description: 'Pick the agreement you need and prefill the strongest clauses.',
  },
  {
    id: 'parties',
    title: 'Parties',
    description: 'Who is signing, and in what capacity.',
  },
  {
    id: 'clauses',
    title: 'Terms & clauses',
    description: 'Review suggested terms, add your own, drop what does not apply.',
  },
  {
    id: 'terms',
    title: 'Dates & jurisdiction',
    description: 'Effective date, term and the governing law.',
  },
  {
    id: 'branding',
    title: 'Branding & details',
    description: 'Optional letterhead, contact details and extra instructions.',
  },
  {
    id: 'review',
    title: 'Review & generate',
    description: 'Confirm everything looks right, then draft the document.',
  },
] as const

export type WizardStepId = (typeof WIZARD_STEPS)[number]['id']
