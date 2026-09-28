/**
 * Input limits mirrored from `backend/app/config.py` and the Pydantic schemas.
 * Kept in sync so the UI can prevent over-long submissions before the round trip.
 */

export const MAX_TITLE = 300
export const MAX_PARTY_NAME = 200
export const MAX_PARTY_ROLE = 120
export const MAX_ORGANIZATION = 200
export const MAX_ADDRESS = 1000
export const MAX_EMAIL = 320
export const MAX_PHONE = 60

/** `Clause.description` is bounded by `max_free_text_chars`. */
export const MAX_CLAUSE_DESCRIPTION = 2_000

/** `GenerateDocumentRequest.additional_instructions` -> `max_instructions_chars`. */
export const MAX_INSTRUCTIONS = 4_000

export const MAX_FOOTER_TEXT = 500
export const MAX_WEBSITE = 255
export const MAX_PARTIES = 20
export const MAX_CLAUSES = 60

/** `max_logo_bytes` (2 MB). */
export const MAX_LOGO_BYTES = 2 * 1024 * 1024
export const LOGO_ACCEPT = 'image/png,image/jpeg'
