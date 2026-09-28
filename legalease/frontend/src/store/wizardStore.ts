/**
 * Wizard state.
 *
 * The wizard is long (six steps) and the user can jump between them, so the
 * draft lives in a store rather than in one component's local state. It is
 * serialised to sessionStorage so a refresh mid-draft does not lose answers.
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

import type { Branding, Clause, GenerateRequest, Jurisdiction, Party } from '../types/api'

export interface PartyDraft {
  name: string
  role: string
  organization: string
  address: string
  email: string
  phone: string
}

export interface ClauseDraft {
  title: string
  description: string
  is_required: boolean
}

export interface WizardState {
  step: number
  documentType: string | null
  title: string
  parties: PartyDraft[]
  clauses: ClauseDraft[]
  /** Clause titles the template suggests, offered as one-click adds in step 3. */
  clauseSuggestions: string[]
  effectiveDate: string
  expiryDate: string
  jurisdiction: Jurisdiction
  branding: Branding
  additionalInstructions: string
  disclaimerAccepted: boolean
  usedSample: boolean

  setStep: (step: number) => void
  setDocumentType: (id: string, defaultTitle: string, sections: string[], clauses: string[]) => void
  setTitle: (title: string) => void
  addParty: () => void
  updateParty: (index: number, patch: Partial<PartyDraft>) => void
  removeParty: (index: number) => void
  setParties: (parties: PartyDraft[]) => void
  addClause: () => void
  addClauseWithTitle: (title: string) => void
  updateClause: (index: number, patch: Partial<ClauseDraft>) => void
  removeClause: (index: number) => void
  setClauses: (clauses: ClauseDraft[]) => void
  setDates: (effective: string, expiry: string) => void
  setJurisdiction: (patch: Jurisdiction) => void
  setBranding: (patch: Branding) => void
  setInstructions: (text: string) => void
  setDisclaimerAccepted: (value: boolean) => void
  loadSample: (payload: GenerateRequest, label: string) => void
  reset: () => void
}

const EMPTY_PARTY: PartyDraft = {
  name: '',
  role: '',
  organization: '',
  address: '',
  email: '',
  phone: '',
}

const initialState = {
  step: 0,
  documentType: null,
  title: '',
  parties: [
    { ...EMPTY_PARTY, role: 'First party' },
    { ...EMPTY_PARTY, role: 'Second party' },
  ] as PartyDraft[],
  clauses: [] as ClauseDraft[],
  clauseSuggestions: [] as string[],
  effectiveDate: '',
  expiryDate: '',
  jurisdiction: {
    country: '',
    state: '',
    city: '',
    governing_law: '',
  } as Jurisdiction,
  branding: {} as Branding,
  additionalInstructions: '',
  disclaimerAccepted: false,
  usedSample: false,
}

function optional(value: string): string | null {
  const trimmed = value.trim()
  return trimmed.length ? trimmed : null
}

export const toPartyPayload = (draft: PartyDraft): Party => ({
  name: draft.name.trim(),
  role: draft.role.trim(),
  organization: optional(draft.organization),
  address: optional(draft.address),
  email: optional(draft.email),
  phone: optional(draft.phone),
})

export const toClausePayload = (draft: ClauseDraft): Clause => ({
  title: draft.title.trim(),
  description: draft.description.trim(),
  is_required: draft.is_required,
})

export const toGenerateRequest = (state: WizardState): GenerateRequest => ({
  document_type: state.documentType ?? '',
  parties: state.parties
    .map(toPartyPayload)
    .filter((party) => party.name.length > 0 && party.role.length > 0),
  clauses: state.clauses
    .map(toClausePayload)
    .filter((clause) => clause.title.length > 0 && clause.description.length > 0),
  effective_date: state.effectiveDate || null,
  expiry_date: state.expiryDate || null,
  jurisdiction: state.jurisdiction,
  branding: state.branding,
  additional_instructions: state.additionalInstructions.trim(),
  title: optional(state.title),
})

export const useWizardStore = create<WizardState>()(
  persist(
    (set) => ({
      ...initialState,

      setStep: (step) => set({ step }),

      setDocumentType: (id, defaultTitle, sections, clauses) =>
        set((state) => ({
          documentType: id,
          title: state.title || defaultTitle,
          clauseSuggestions: clauses,
          // Seed sections as clause rows, but never clobber what the user wrote.
          clauses: state.clauses.length
            ? state.clauses
            : sections.map((title) => ({
                title,
                description: '',
                is_required: true,
              })),
        })),

      setTitle: (title) => set({ title }),

      addParty: () =>
        set((state) => ({
          parties: [
            ...state.parties,
            { ...EMPTY_PARTY, role: `Party ${state.parties.length + 1}` },
          ],
        })),

      updateParty: (index, patch) =>
        set((state) => ({
          parties: state.parties.map((party, i) =>
            i === index ? { ...party, ...patch } : party,
          ),
        })),

      removeParty: (index) =>
        set((state) => ({
          parties: state.parties.filter((_, i) => i !== index),
        })),

      setParties: (parties) => set({ parties }),

      addClause: () =>
        set((state) => ({
          clauses: [...state.clauses, { title: '', description: '', is_required: true }],
        })),

      addClauseWithTitle: (title) =>
        set((state) => {
          if (state.clauses.some((clause) => clause.title.toLowerCase() === title.toLowerCase())) {
            return state
          }
          return {
            clauses: [...state.clauses, { title, description: '', is_required: true }],
          }
        }),

      updateClause: (index, patch) =>
        set((state) => ({
          clauses: state.clauses.map((clause, i) =>
            i === index ? { ...clause, ...patch } : clause,
          ),
        })),

      removeClause: (index) =>
        set((state) => ({ clauses: state.clauses.filter((_, i) => i !== index) })),

      setClauses: (clauses) => set({ clauses }),

      setDates: (effectiveDate, expiryDate) => set({ effectiveDate, expiryDate }),

      setJurisdiction: (patch) =>
        set((state) => ({ jurisdiction: { ...state.jurisdiction, ...patch } })),

      setBranding: (patch) =>
        set((state) => ({ branding: { ...state.branding, ...patch } })),

      setInstructions: (additionalInstructions) => set({ additionalInstructions }),

      setDisclaimerAccepted: (disclaimerAccepted) => set({ disclaimerAccepted }),

      loadSample: (payload, label) =>
        set({
          documentType: payload.document_type,
          title: payload.title ?? label,
          parties: payload.parties.map((party) => ({
            name: party.name,
            role: party.role,
            organization: party.organization ?? '',
            address: party.address ?? '',
            email: party.email ?? '',
            phone: party.phone ?? '',
          })),
          clauses: payload.clauses.map((clause) => ({
            title: clause.title,
            description: clause.description,
            is_required: clause.is_required,
          })),
          effectiveDate: payload.effective_date ?? '',
          expiryDate: payload.expiry_date ?? '',
          jurisdiction: payload.jurisdiction,
          branding: payload.branding,
          additionalInstructions: payload.additional_instructions,
          clauseSuggestions: [],
          usedSample: true,
        }),

      reset: () => set({ ...initialState, parties: initialState.parties.map((p) => ({ ...p })) }),
    }),
    {
      name: 'legalease.wizard',
      version: 1,
      partialize: (state) => ({
        step: state.step,
        documentType: state.documentType,
        title: state.title,
        parties: state.parties,
        clauses: state.clauses,
        clauseSuggestions: state.clauseSuggestions,
        effectiveDate: state.effectiveDate,
        expiryDate: state.expiryDate,
        jurisdiction: state.jurisdiction,
        branding: state.branding,
        additionalInstructions: state.additionalInstructions,
        disclaimerAccepted: state.disclaimerAccepted,
        usedSample: state.usedSample,
      }),
    },
  ),
)
