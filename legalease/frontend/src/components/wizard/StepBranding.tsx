import { Building2, ImageUp, Loader2, Save, Trash2 } from 'lucide-react'
import { useRef, useState } from 'react'

import { Button } from '../ui/Button'
import { Card } from '../ui/Card'
import { Field, Input, Textarea } from '../ui/Input'
import { assetUrl } from '../../services'
import { useBranding, useSaveBranding, useUploadLogo } from '../../hooks/useBranding'
import {
  LOGO_ACCEPT,
  MAX_ADDRESS,
  MAX_EMAIL,
  MAX_FOOTER_TEXT,
  MAX_INSTRUCTIONS,
  MAX_LOGO_BYTES,
  MAX_ORGANIZATION,
  MAX_PHONE,
  MAX_TITLE,
  MAX_WEBSITE,
} from '../../constants/limits'
import type { Branding } from '../../types/api'
import { formatNumber } from '../../utils/format'

interface Props {
  branding: Branding
  instructions: string
  title: string
  onBranding: (patch: Branding) => void
  onInstructions: (text: string) => void
  onTitleChange: (title: string) => void
}

export function StepBranding({
  branding,
  instructions,
  title,
  onBranding,
  onInstructions,
  onTitleChange,
}: Props) {
  const { active } = useBranding()
  const saveBrand = useSaveBranding()
  const uploadLogo = useUploadLogo()
  const fileInput = useRef<HTMLInputElement>(null)
  const [localError, setLocalError] = useState<string | null>(null)

  const logoUrl = branding.logo_path ? assetUrl(`/api/branding/logo/${branding.logo_path}`) : null

  function pickFile(file: File | undefined) {
    setLocalError(null)
    if (!file) return
    if (file.size > MAX_LOGO_BYTES) {
      setLocalError(
        `That image is ${formatNumber(Math.round(file.size / 1024))} KB. The limit is ${formatNumber(
          MAX_LOGO_BYTES / 1024,
        )} KB.`,
      )
      return
    }
    uploadLogo.mutate(file, {
      onSuccess: (result) => onBranding({ logo_path: result.logo_path }),
    })
  }

  return (
    <div className="flex flex-col gap-6">
      <Card className="p-5">
        <div className="flex items-center gap-2.5">
          <span className="flex size-8 items-center justify-center rounded-lg border border-navy-600 bg-navy-800/70 text-gold-400">
            <Building2 className="size-4" aria-hidden />
          </span>
          <div>
            <h3 className="text-sm font-medium text-ivory-50">Document title</h3>
            <p className="text-xs text-ivory-300/50">Shown at the top of the preview and export.</p>
          </div>
        </div>
        <Field className="mt-4" label="Title">
          {(id) => (
            <Input
              id={id}
              value={title}
              maxLength={MAX_TITLE}
              onChange={(event) => onTitleChange(event.target.value)}
            />
          )}
        </Field>
      </Card>

      <Card className="p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="flex size-8 items-center justify-center rounded-lg border border-navy-600 bg-navy-800/70 text-gold-400">
              <ImageUp className="size-4" aria-hidden />
            </span>
            <div>
              <h3 className="text-sm font-medium text-ivory-50">Letterhead</h3>
              <p className="text-xs text-ivory-300/50">
                PNG or JPEG, up to {formatNumber(MAX_LOGO_BYTES / 1024)} KB. Appears in exports.
              </p>
            </div>
          </div>
          <Button
            size="sm"
            variant="outline"
            loading={uploadLogo.isPending}
            onClick={() => fileInput.current?.click()}
          >
            {logoUrl ? 'Replace logo' : 'Upload logo'}
          </Button>
          <input
            ref={fileInput}
            type="file"
            accept={LOGO_ACCEPT}
            className="sr-only"
            aria-label="Upload company logo"
            onChange={(event) => pickFile(event.target.files?.[0])}
          />
        </div>

        {localError ? <p className="mt-3 text-xs text-rose-300">{localError}</p> : null}

        {logoUrl ? (
          <div className="mt-5 flex items-center gap-4 rounded-xl border border-navy-700 bg-navy-900/40 p-4">
            <span className="flex size-16 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-navy-600 bg-ivory-100 p-1.5">
              <img src={logoUrl} alt="Uploaded logo preview" className="max-h-full max-w-full object-contain" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-sm text-ivory-100">Logo attached</p>
              <p className="mt-0.5 text-xs text-ivory-300/50">
                Used in the PDF header, the Word header and the document footer.
              </p>
            </div>
            <Button
              size="icon-sm"
              variant="ghost"
              aria-label="Remove logo"
              className="text-ivory-300/50 hover:text-rose-300"
              onClick={() => onBranding({ logo_path: null })}
            >
              <Trash2 aria-hidden />
            </Button>
          </div>
        ) : active?.logo_url ? (
          <p className="mt-5 text-xs text-ivory-300/50">
            Your saved profile has a logo.{' '}
            <button
              type="button"
              className="text-gold-300 underline underline-offset-2"
              onClick={() =>
                onBranding({ logo_path: active.logo_path, brand_profile_id: active.id })
              }
            >
              Use the saved logo
            </button>
          </p>
        ) : null}
      </Card>

      <Card className="p-5">
        <h3 className="text-sm font-medium text-ivory-50">Organisation details</h3>
        <p className="mt-1 text-xs text-ivory-300/55">
          Optional. Fills the letterhead block and the notice details at the end of the
          document.
        </p>

        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <Field label="Organisation name" className="sm:col-span-2">
            {(id) => (
              <Input
                id={id}
                value={branding.organization_name ?? ''}
                maxLength={MAX_ORGANIZATION}
                placeholder="e.g. Northwind Studio LLC"
                onChange={(event) => onBranding({ organization_name: event.target.value })}
              />
            )}
          </Field>

          <Field label="Email" className="sm:col-span-2">
            {(id) => (
              <Input
                id={id}
                type="email"
                value={branding.email ?? ''}
                maxLength={MAX_EMAIL}
                placeholder="legal@northwind.studio"
                onChange={(event) => onBranding({ email: event.target.value })}
              />
            )}
          </Field>

          <Field label="Phone">
            {(id) => (
              <Input
                id={id}
                type="tel"
                value={branding.phone ?? ''}
                maxLength={MAX_PHONE}
                onChange={(event) => onBranding({ phone: event.target.value })}
              />
            )}
          </Field>

          <Field label="Website">
            {(id) => (
              <Input
                id={id}
                type="url"
                value={branding.website ?? ''}
                maxLength={MAX_WEBSITE}
                placeholder="https://example.com"
                onChange={(event) => onBranding({ website: event.target.value })}
              />
            )}
          </Field>

          <Field label="Address" className="sm:col-span-2">
            {(id) => (
              <Textarea
                id={id}
                rows={2}
                value={branding.address ?? ''}
                maxLength={MAX_ADDRESS}
                onChange={(event) => onBranding({ address: event.target.value })}
              />
            )}
          </Field>

          <Field
            label="Footer text"
            className="sm:col-span-2"
            hint="Printed on every exported page."
          >
            {(id) => (
              <Input
                id={id}
                value={branding.footer_text ?? ''}
                maxLength={MAX_FOOTER_TEXT}
                placeholder="e.g. Confidential — Northwind Studio LLC"
                onChange={(event) => onBranding({ footer_text: event.target.value })}
              />
            )}
          </Field>
        </div>

        <div className="mt-5 flex flex-wrap items-center gap-3 border-t border-navy-700/60 pt-4">
          <Button
            size="sm"
            variant="secondary"
            loading={saveBrand.isPending}
            onClick={() => saveBrand.mutate({ ...branding })}
          >
            {saveBrand.isPending ? <Loader2 className="animate-spin" aria-hidden /> : <Save aria-hidden />}
            Save as reusable profile
          </Button>
          <p className="text-xs text-ivory-300/45">
            Reuses these details for the next document you draft.
          </p>
        </div>
      </Card>

      <Card className="p-5">
        <Field
          label="Additional instructions for the AI"
          hint={`${instructions.length} / ${MAX_INSTRUCTIONS} - tone, length, or anything unusual about this agreement.`}
        >
          {(id, describedBy) => (
            <Textarea
              id={id}
              rows={5}
              value={instructions}
              maxLength={MAX_INSTRUCTIONS}
              aria-describedby={describedBy}
              placeholder="e.g. Use a mutual confidentiality obligation, keep the payment terms mutual, and add a non-solicitation clause for 12 months."
              onChange={(event) => onInstructions(event.target.value)}
            />
          )}
        </Field>
      </Card>
    </div>
  )
}
