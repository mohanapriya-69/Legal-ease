"""Prompts used for legal drafting.

The output contract is NOT described here. It is supplied to the model as a JSON
schema (``response_json_schema``), and the SDK's own guidance is to avoid
duplicating the schema in the prompt - doing so degrades output quality. This
module therefore carries only drafting *behaviour*.
"""

from __future__ import annotations

from app.schemas.ai import (
    BrandingInput,
    Clause,
    GenerateDocumentRequest,
    Jurisdiction,
    Party,
)

SYSTEM_PROMPT = """\
You are a senior commercial lawyer drafting agreements on behalf of a legal
technology platform. You produce publication-quality first drafts that a
qualified lawyer can review, revise and execute.

NON-NEGOTIABLE RULES

1. Use only the facts supplied in the request. Never invent, guess, infer or
   complete any name, role, organization, address, email address, telephone
   number, date, currency amount, fee, rate, duration, notice period or
   reference number. If a value the user did not provide is needed for a
   provision to make sense, insert a clearly marked placeholder in square
   brackets, for example [FEE AMOUNT], [NOTICE PERIOD IN DAYS] or
   [INSERT GOVERNING LAW].
2. Placeholders must be specific and self-describing. Never write
   "TBD", "XXX", "____" or an empty bracket pair.
3. Do not silently drop a party. Every supplied party must appear in the
   Parties section with the exact role the user gave them.
4. Internal consistency is mandatory. A duration, payment period or notice
   period must be the same everywhere it appears. If two supplied terms
   conflict, surface the conflict in the `intro` and draft around it rather
   than silently picking one.
5. Honour every supplied clause. Clauses marked required must be present and
   substantive. Clauses marked optional should be included only where they
   fit naturally.
6. Do not include clauses the user did not ask for. In particular never add
   non-compete, exclusivity, arbitration, auto-renewal or liquidated damages
   provisions unless the user requested them.

STRUCTURE

- Use a clear, descriptive document title reflecting the actual agreement
  type. Do not simply echo the template name if the arrangement is narrower.
- Open with a short `intro` of two to four sentences: the date, the parties in
  their contract roles, and the commercial purpose. Do not restate every term.
- Write sections with sequential Arabic numbering, e.g. "1. Parties",
  "2. Scope of Services". Never skip a number.
- Order sections so that commercial substance comes before boilerplate.
  Definitions and parties first, then obligations, then payment, then term
  and termination, then general provisions.
- Keep each section focused on one idea. Use sub-numbering such as
  2.1 and 2.2 inside a section when a provision has distinct limbs.
- Use `bullets` only for genuine lists such as deliverables, payment
  milestones or permitted uses. Use prose paragraphs otherwise.
- Use a `table` when tabular presentation is genuinely clearer, for example
  a schedule of fees, deliverables and due dates, or a furniture inventory.
  Do not force prose into a table.
- Populate `signature_blocks` with one entry per party, using the party's
  name and the role the user assigned. Do not invent signatories.

DRAFTING STYLE

- Register: precise, neutral and professional. Third person, present tense.
- Prefer short sentences. Avoid padding, legalese for its own sake, and
  rhetorical flourish.
- Use defined terms consistently and capitalise them once introduced.
- Where drafting would benefit from a real lawyer's judgement, state the
  commercial intent plainly and let the reviewing lawyer decide the
  enforcement question.

LEGAL SAFETY

- Close `disclaimer` with wording stating the document is an AI-assisted
  draft, is not legal advice, and should be reviewed by a qualified lawyer
  before signing. Do not assert that the document is legally valid,
  enforceable or lawyer approved.
"""

REWRITE_SYSTEM_PROMPT = """\
You are a senior commercial lawyer revising a single clause of a legal
agreement that a qualified lawyer is reviewing.

Revise only the text you are given. You have no authority to add new sections,
change the agreement structure, or introduce parties, dates, amounts or
jurisdictions that do not already appear in the supplied text or context.

Preserve the legal meaning of the clause. Improvements in style, precision,
grammar and structure are welcome; a change that shifts the commercial
allocation of risk is not.

If the instruction asks for something that would require facts you do not
have, insert a clearly marked, self-describing placeholder such as
[INSERT NOTICE PERIOD IN DAYS] rather than inventing a value.

Return the revised text only.
"""

REVISION_INSTRUCTIONS: dict[str, str] = {
    "rewrite_professional": (
        "Rewrite this clause in polished professional legal English. Improve "
        "clarity, sentence structure and consistency of defined terms. Preserve "
        "the legal meaning exactly and do not add or remove any obligation."
    ),
    "simplify": (
        "Rewrite this clause in plain, easily understood English while keeping "
        "the legal effect identical. Replace dense constructions with short "
        "sentences. Remove unnecessary words. Do not weaken any protection."
    ),
    "more_formal": (
        "Rewrite this clause in a more formal register suitable for execution "
        "by counsel. Use precise drafting conventions and formal connectives. "
        "Preserve the substance exactly."
    ),
    "expand": (
        "Expand this clause into a more complete provision. Add the detail a "
        "reviewing lawyer would expect, such as procedural steps, notice "
        "mechanics, and how the parties interact under the clause. Do not "
        "invent specific dates, amounts or party names; use clearly marked "
        "placeholders where a value is required."
    ),
    "shorten": (
        "Condense this clause by roughly forty percent while preserving its "
        "full legal effect. Cut redundancy and merge duplicated concepts. Do "
        "not remove any obligation or exception."
    ),
    "fix_grammar": (
        "Correct all grammar, spelling, punctuation, capitalisation and "
        "numbering errors in this clause. Do not change its meaning, structure "
        "or length."
    ),
    "add_protection": (
        "Strengthen this clause so it better protects the party that is "
        "currently disadvantaged, without making it unenforceable. Consider "
        "notice mechanics, cure periods, materiality, carve-outs and remedies. "
        "Do not invent specific dates or amounts; use clearly marked "
        "placeholders."
    ),
}


def _format_parties(parties: list[Party]) -> str:
    if not parties:
        return "(none supplied)"
    return "\n\n".join(
        f"Party {index}:\n{party.as_context()}"
        for index, party in enumerate(parties, start=1)
    )


def _format_clauses(clauses: list[Clause]) -> str:
    if not clauses:
        return "(none supplied)"
    return "\n".join(f"- {clause.as_context()}" for clause in clauses)


def _format_branding(branding: BrandingInput) -> str:
    if branding.is_empty():
        return "(no branding supplied - the document will not carry an organisation header)"
    bits = [
        f"Organisation: {value}"
        for value in (
            branding.organization_name,
            branding.address,
            branding.email,
            branding.phone,
            branding.website,
            branding.footer_text,
        )
        if value
    ]
    return "\n".join(bits)


def _format_jurisdiction(jurisdiction: Jurisdiction) -> str:
    if jurisdiction.is_empty():
        return "(none supplied)"
    return jurisdiction.as_context()


def build_generation_prompt(
    *,
    document_type_title: str,
    document_type_description: str,
    suggested_sections: list[str],
    request: GenerateDocumentRequest,
) -> str:
    """Assemble the user turn for a full document generation."""
    # The date fields are optional in the request schema, so both are formatted
    # defensively - a missing date must degrade to a placeholder, not a 500.
    effective = (
        f"Effective date: {request.effective_date.isoformat()}"
        if request.effective_date
        else "Effective date: (not supplied - use a clear 'DATED' placeholder)"
    )
    if request.expiry_date:
        expiry = f"Expiry date: {request.expiry_date.isoformat()}"
    else:
        expiry = "Expiry date: (not supplied)"

    dates = [effective, expiry]

    parts = [
        "Draft the following agreement.",
        "",
        "DOCUMENT TYPE",
        f"Title: {document_type_title}",
        f"Purpose: {document_type_description}",
        "",
        "SUGGESTED SECTION STRUCTURE",
        "Use this as a guide, adapting it to the facts supplied:",
        "\n".join(f"{i}. {heading}" for i, heading in enumerate(suggested_sections, 1))
        if suggested_sections
        else "(no structure supplied - choose an appropriate one)",
        "",
        "PARTIES",
        _format_parties(request.parties),
        "",
        "TERMS AND CLAUSES THE USER HAS SPECIFIED",
        _format_clauses(request.clauses),
        "",
        "DATES",
        "\n".join(dates),
        "",
        "JURISDICTION",
        _format_jurisdiction(request.jurisdiction),
        "",
        "BRANDING",
        _format_branding(request.branding),
    ]

    if request.additional_instructions.strip():
        parts.extend(
            [
                "",
                "ADDITIONAL INSTRUCTIONS FROM THE USER",
                "These take precedence over the general guidance above.",
                request.additional_instructions.strip(),
            ]
        )

    parts.extend(
        [
            "",
            "Reminder: use only the facts above. Mark anything missing with a "
            "specific, self-describing placeholder in square brackets. Do not "
            "claim the document is legally valid or enforceable.",
        ]
    )
    return "\n".join(parts)


def build_rewrite_prompt(
    *,
    action: str,
    heading: str,
    content: str,
    custom_instruction: str = "",
    document_title: str = "",
    previous_heading: str | None = None,
    next_heading: str | None = None,
) -> str:
    """Assemble the user turn for a single-section revision."""
    context_bits = [f"Document: {document_title}"] if document_title else []
    if previous_heading:
        context_bits.append(f"Preceding section: {previous_heading}")
    if next_heading:
        context_bits.append(f"Following section: {next_heading}")
    context = "\n".join(context_bits) if context_bits else "(no document context)"

    instruction = REVISION_INSTRUCTIONS.get(
        action, REVISION_INSTRUCTIONS["rewrite_professional"]
    )
    if custom_instruction.strip():
        instruction = (
            f"{instruction}\n\nAdditional instruction from the reviewing "
            f"lawyer:\n{custom_instruction.strip()}"
        )

    return "\n".join(
        [
            "REVISE A SINGLE CLAUSE OF AN EXISTING AGREEMENT.",
            "",
            "CONTEXT",
            context,
            "",
            "TARGET SECTION",
            f"Heading: {heading}",
            "",
            "CURRENT TEXT",
            content or "(this section is currently empty)",
            "",
            "INSTRUCTION",
            instruction,
            "",
            "Return only the revised clause text. Do not include a heading, "
            "section number, commentary or quotation marks.",
        ]
    )

