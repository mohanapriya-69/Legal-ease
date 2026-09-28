"""Deterministic offline document generator.

Used when ``DEMO_MODE=true`` and no API key is available. Output is derived
purely from the supplied request - no randomness, no clock-dependent content -
so the same input always produces the same document. Every result is tagged
``source="demo"`` and rendered with a "Demo AI Response" badge in the UI so it
is never mistaken for real LLM output.
"""

from __future__ import annotations

import uuid

from app.schemas.ai import (
    Clause,
    DocumentContent,
    DocumentDraft,
    DocumentSection,
    DocumentTable,
    GenerateDocumentRequest,
    Jurisdiction,
    SignatureBlock,
    renumber_sections,
)
from app.templates.disclaimer import LEGAL_DISCLAIMER

DEMO_NOTE = (
    "This draft was produced by LegalEase in demo mode, without a live AI "
    "connection. The wording below is generated deterministically from the "
    "information you supplied and is provided so the workflow can be "
    "evaluated end to end. It is a placeholder draft, not legal advice."
)


def _placeholder(value: str | None, fallback: str) -> str:
    value = (value or "").strip()
    return value if value else fallback


def _party_phrase(party) -> str:  # noqa: ANN001 - Party
    if party.organization:
        return f"{party.organization}, acting through {party.name}"
    return party.name


def _describe_party(party) -> str:  # noqa: ANN001 - Party
    bits = [f"{party.name}"]
    if party.organization:
        bits.append(f"of {party.organization}")
    bits.append(f'(the "{party.role}")')
    sentence = " ".join(bits)
    if party.address:
        sentence += f", of {party.address}"
    if party.email:
        sentence += f", contactable at {party.email}"
    if party.phone:
        sentence += f" or {party.phone}"
    return sentence + "."


def _jurisdiction_phrase(jurisdiction: Jurisdiction) -> str:
    law = _placeholder(jurisdiction.governing_law, "[INSERT GOVERNING LAW]")
    location = ", ".join(
        p for p in (jurisdiction.city, jurisdiction.state, jurisdiction.country) if p
    )
    if location:
        return f"{law} (location: {location})"
    return law


def _effective_phrase(request: GenerateDocumentRequest) -> str:
    if request.effective_date:
        phrase = f"This Agreement takes effect on {request.effective_date.isoformat()}"
        if request.expiry_date:
            phrase += (
                f" and continues until {request.expiry_date.isoformat()}, unless "
                "terminated earlier in accordance with its terms"
            )
        return phrase + "."
    return (
        "This Agreement takes effect on [EFFECTIVE DATE] and continues until "
        "[EXPIRY DATE], unless terminated earlier in accordance with its terms."
    )


# --- Clause body templates --------------------------------------------
# Keyed by the clause key used in the template catalog. Unknown keys fall back
# to a generic body built from the user's own description.


def _body_confidentiality(request: GenerateDocumentRequest) -> str:
    names = ", ".join(
        _party_phrase(p) for p in request.parties[:2]
    ) or "each party"
    return (
        f"Each party undertakes to the other that it will, during the term of this "
        f"Agreement and for a period of [SURVIVAL PERIOD IN YEARS] afterwards, keep "
        f"confidential all information disclosed to it by the other party that is "
        f"identified as confidential or that a reasonable person would treat as "
        f"confidential, and will not use that information for any purpose other than "
        f"the performance of this Agreement.\n\n"
        f"The obligations in this section do not apply to information that: "
        f"(a) is or becomes publicly available other than through breach of this "
        f"Agreement; (b) was lawfully known to the receiving party before "
        f"disclosure; (c) is lawfully received from a third party without restriction; "
        f"or (d) is independently developed without use of or reference to the "
        f"disclosing party's information.\n\n"
        f"Where disclosure is required by law, court order or a competent regulator, "
        f"the receiving party may disclose the minimum information required, provided "
        f"it gives the disclosing party prompt written notice where lawfully permitted "
        f"to do so."
    )


def _body_payment(request: GenerateDocumentRequest) -> str:
    return (
        "The Client shall pay the fees set out in this Agreement or in any "
        "statement of work signed by the parties. Unless otherwise stated, invoices "
        "are payable within [PAYMENT PERIOD IN DAYS] days of the invoice date.\n\n"
        "Where an invoice is not paid when due, the Contractor may charge interest "
        "on the overdue amount at [INTEREST RATE] per annum, accruing daily, "
        "provided that this does not exceed the maximum rate permitted by "
        "applicable law.\n\n"
        "The Client shall reimburse reasonable, pre-approved out-of-pocket expenses "
        "within [EXPENSE REIMBURSEMENT PERIOD IN DAYS] days of being incurred and "
        "supported by receipts."
    )


def _body_ip(request: GenerateDocumentRequest) -> str:
    return (
        "Each party retains all right, title and interest in intellectual property "
        "owned by or licensed to it before the Effective Date (\"Background IP\").\n\n"
        "On full payment of all sums due under this Agreement, the Contractor "
        "assigns to the Client, with full title guarantee and free from encumbrances, "
        "all intellectual property rights in the Deliverables, excluding Background "
        "IP. Where the Deliverables incorporate Background IP, the Contractor grants "
        "the Client a perpetual, irrevocable, worldwide, non-exclusive, royalty-free "
        "licence to use, copy, modify and exploit that Background IP to the extent "
        "necessary to exploit the Deliverables.\n\n"
        "The Contractor may continue to use general skills, techniques and know-how "
        "developed in the performance of this Agreement, provided no Confidential "
        "Information of the Client is disclosed."
    )


def _body_termination(request: GenerateDocumentRequest) -> str:
    return (
        "Either party may terminate this Agreement by giving the other written "
        "notice of not less than [NOTICE PERIOD IN DAYS] days.\n\n"
        "Either party may terminate immediately by written notice if the other "
        "party: (a) commits a material breach that is incapable of remedy; "
        "(b) commits a material breach that is capable of remedy and fails to remedy "
        "it within [CURE PERIOD IN DAYS] days of written notice; or (c) becomes "
        "insolvent or enters liquidation.\n\n"
        "Termination does not affect any right or liability accrued before "
        "termination. On termination the Client shall pay for all work performed and "
        "expenses properly incurred up to the effective date of termination, and the "
        "Confidentiality provisions survive."
    )


def _body_governing_law(request: GenerateDocumentRequest) -> str:
    law = _placeholder(
        request.jurisdiction.governing_law, "[INSERT GOVERNING LAW]"
    )
    courts = _placeholder(
        request.jurisdiction.city and f"the courts of {request.jurisdiction.city}",
        "[INSERT FORUM]",
    )
    return (
        f"This Agreement and any dispute or claim arising out of or in connection "
        f"with it or its subject matter, including any non-contractual dispute, are "
        f"governed by and construed in accordance with {law}.\n\n"
        f"The parties submit to the exclusive jurisdiction of {courts} in respect of "
        f"any such dispute or claim, save that either party may seek injunctive "
        f"relief in any competent court to protect its Confidential Information or "
        f"intellectual property."
    )


def _body_liability(request: GenerateDocumentRequest) -> str:
    return (
        "Neither party excludes or limits liability for death or personal injury "
        "caused by its negligence, for fraud or fraudulent misrepresentation, or for "
        "any other liability that cannot lawfully be excluded or limited.\n\n"
        "Subject to the preceding paragraph, neither party is liable for any indirect "
        "or consequential loss, loss of profit, loss of anticipated savings, loss of "
        "business opportunity or loss of goodwill, in each case whether direct or "
        "indirect.\n\n"
        "Subject to the preceding paragraphs, each party's total aggregate liability "
        "arising out of or in connection with this Agreement is limited to "
        "[LIABILITY CAP - suggest 100% of fees paid or payable in the preceding 12 "
        "months]."
    )


def _body_deliverables(request: GenerateDocumentRequest) -> str:
    return (
        "The Contractor shall provide the following deliverables: [DESCRIBE "
        "DELIVERABLES].\n\n"
        "Deliverables are deemed accepted when the Client confirms acceptance in "
        "writing, or, if the Client does not raise a written objection specifying "
        "the deficiency within [REVIEW PERIOD IN DAYS] days of delivery, the "
        "deliverables are deemed accepted.\n\n"
        "The Contractor shall correct any deficiency notified under this section at "
        "no additional charge within [REMEDY PERIOD IN DAYS] days. This does not "
        "limit the Client's right to reject a deliverable that cannot be remedied."
    )


def _body_deadlines(request: GenerateDocumentRequest) -> str:
    effective = (
        request.effective_date.isoformat()
        if request.effective_date
        else "[EFFECTIVE DATE]"
    )
    return (
        f"The Contractor shall complete the Services and deliver all Deliverables "
        f"no later than [COMPLETION DEADLINE]. Time is of the essence.\n\n"
        f"Progress against the agreed milestones shall be reported weekly, starting "
        f"from {effective}. Where the Contractor anticipates that it will miss a "
        f"milestone it shall notify the Client in writing as soon as reasonably "
        f"practicable, stating the reason and the revised date.\n\n"
        f"Delay caused by the Client's failure to provide information, materials or "
        f"approvals required for performance is excused to the extent of the resulting "
        f"delay, and the delivery schedule is extended accordingly."
    )


def _body_dispute_resolution(request: GenerateDocumentRequest) -> str:
    return (
        "Before commencing proceedings, the parties shall attempt in good faith to "
        "resolve any dispute by negotiation between senior representatives within "
        "[NEGOTIATION PERIOD IN DAYS] days of written notice of the dispute.\n\n"
        "If the dispute is not resolved within that period, either party may refer it "
        "to mediation before a mutually agreed mediator, with the costs of the "
        "mediator shared equally.\n\n"
        "Nothing in this section prevents either party from seeking urgent interim or "
        "injunctive relief from a court of competent jurisdiction."
    )


def _body_force_majeure(request: GenerateDocumentRequest) -> str:
    return (
        "Neither party is liable for any failure or delay in performing its "
        "obligations under this Agreement to the extent that the failure or delay is "
        "caused by an event beyond its reasonable control, including acts of God, "
        "natural disaster, war, terrorism, civil unrest, epidemic, pandemic, "
        "government action, embargo, or failure of a third-party network or utility "
        "provider.\n\n"
        "The affected party shall notify the other as soon as reasonably practicable, "
        "and the parties shall use all reasonable endeavours to mitigate the effect. "
        "If a force majeure event continues for more than [FORCE MAJEURE PERIOD IN "
        "DAYS] days, either party may terminate this Agreement by written notice "
        "without liability, save for sums already accrued."
    )


def _body_data_protection(request: GenerateDocumentRequest) -> str:
    return (
        "Each party shall comply with all applicable data protection legislation, "
        "including [APPLICABLE DATA PROTECTION LAW].\n\n"
        "Where the Contractor processes personal data on behalf of the Client, the "
        "Contractor shall do so only on documented instructions from the Client, "
        "shall ensure that persons acting under its authority process that data only "
        "on those instructions, and shall implement appropriate technical and "
        "organisational measures to protect it.\n\n"
        "The Contractor shall notify the Client without undue delay, and in any event "
        "within [NOTIFICATION PERIOD IN DAYS] days, on becoming aware of any personal "
        "data breach, and shall provide reasonable assistance with the Client's "
        "obligations to respond to data subject requests."
    )


def _body_non_compete(request: GenerateDocumentRequest) -> str:
    return (
        "During the term of this Agreement and for a period of [RESTRICTION PERIOD IN "
        "MONTHS] months afterwards, neither party shall, within [TERRITORY], directly "
        "or indirectly engage in, provide, or hold an interest in any business that "
        "competes with the other party's business in relation to the subject matter of "
        "this Agreement.\n\n"
        "This restriction does not prevent either party from holding an investment of "
        "less than [PERCENTAGE]% in a publicly traded company whose shares are listed "
        "on a recognised exchange, provided that party does not participate in its "
        "management.\n\n"
        "Each party acknowledges that this restriction is reasonable and necessary to "
        "protect its legitimate business interests, and that a court may sever any "
        "part of it that is not."
    )


def _body_assignment(request: GenerateDocumentRequest) -> str:
    return (
        "Neither party may assign, novate, charge or otherwise deal with any of its "
        "rights or obligations under this Agreement without the prior written consent "
        "of the other party, such consent not to be unreasonably withheld or delayed.\n\n"
        "A party may assign this Agreement to a member of its group on written notice, "
        "provided the assignee assumes the assigning party's obligations in full.\n\n"
        "Any purported assignment in breach of this section is void."
    )


def _body_notices(request: GenerateDocumentRequest) -> str:
    return (
        "Notices under this Agreement must be in writing and delivered by hand, by "
        "recorded delivery post, or by email to the addresses set out in this "
        "Agreement (or such other address as a party notifies in writing).\n\n"
        "A notice is deemed received: if delivered by hand, on delivery; if sent by "
        "post, at 9.00 am on the second business day after posting; and if sent by "
        "email, at the time of transmission, provided no delivery failure notification "
        "is received. A notice received outside normal business hours is deemed "
        "received at the next business hour."
    )


def _body_entire_agreement(request: GenerateDocumentRequest) -> str:
    return (
        "This Agreement, together with any schedules and any statement of work signed "
        "by the parties, constitutes the entire agreement between the parties in "
        "relation to its subject matter and supersedes all prior drafts, proposals, "
        "representations and understandings, whether written or oral.\n\n"
        "Each party acknowledges that it has not relied on any statement or "
        "representation not expressly set out in this Agreement. Nothing in this "
        "clause limits liability for fraud or fraudulent misrepresentation."
    )


def _body_severability(request: GenerateDocumentRequest) -> str:
    return (
        "If any provision of this Agreement is or becomes invalid, illegal or "
        "unenforceable, it shall be deemed modified to the minimum extent necessary to "
        "make it enforceable. If such modification is not possible, the provision "
        "shall be deemed deleted.\n\n"
        "Any modification or deletion does not affect the validity, legality and "
        "enforceability of the remaining provisions, which shall continue in full "
        "force and effect."
    )


_CLAUSE_BODIES = {
    "confidentiality": _body_confidentiality,
    "payment_terms": _body_payment,
    "intellectual_property": _body_ip,
    "termination": _body_termination,
    "governing_law": _body_governing_law,
    "liability": _body_liability,
    "deliverables": _body_deliverables,
    "deadlines": _body_deadlines,
    "dispute_resolution": _body_dispute_resolution,
    "force_majeure": _body_force_majeure,
    "data_protection": _body_data_protection,
    "non_compete": _body_non_compete,
    "assignment": _body_assignment,
    "notices": _body_notices,
    "entire_agreement": _body_entire_agreement,
    "severability": _body_severability,
}


def _clause_body(clause: Clause, request: GenerateDocumentRequest) -> str:
    if clause.clause_key and clause.clause_key in _CLAUSE_BODIES:
        body = _CLAUSE_BODIES[clause.clause_key](request)
        return f"{body}\n\nThe parties have recorded the following requirement in "
        f"relation to this provision: {clause.description}"
    return clause.description


# --- Section builders --------------------------------------------------


def _build_sections(
    request: GenerateDocumentRequest, template_sections: list[str]
) -> list[DocumentSection]:
    sections: list[DocumentSection] = []

    def add(heading: str, content: str, **extra) -> None:  # noqa: ANN003
        sections.append(
            DocumentSection(
                id=uuid.uuid4().hex[:12],
                heading=heading,
                content=content,
                **extra,
            )
        )

    primary = request.parties[0]
    secondary = request.parties[1] if len(request.parties) > 1 else None

    # Parties
    if secondary:
        add(
            "Parties",
            f"This Agreement is made on {_effective_phrase(request).split(' takes effect on ')[0]}"
            if request.effective_date
            else "This Agreement is made between:",
        )
        sections[-1].content = (
            f"This Agreement is made between:\n\n"
            f"(1) {_describe_party(primary)}\n\n"
            f"(2) {_describe_party(secondary)}"
            + (
                f"\n\nEach of the parties is a \"Party\" and together they are the "
                f"\"Parties\"."
            )
        )

    # Clause sections, in the order the user supplied them.
    for clause in request.clauses:
        heading = clause.title
        content = _clause_body(clause, request)
        extra = {}
        if clause.clause_key == "payment_terms" or clause.clause_key == "deadlines":
            extra["table"] = DocumentTable(
                caption="Summary of key commercial terms",
                headers=["Item", "Detail"],
                rows=[
                    ["Effective date", request.effective_date.isoformat()
                     if request.effective_date else "[EFFECTIVE DATE]"],
                    ["Expiry date", request.expiry_date.isoformat()
                     if request.expiry_date else "[EXPIRY DATE]"],
                    ["Governing law", _placeholder(
                        request.jurisdiction.governing_law, "[INSERT GOVERNING LAW]"
                    )],
                    ["Jurisdiction", request.jurisdiction.summary()],
                ],
            )
        if clause.clause_key == "deliverables":
            extra["bullets"] = [
                "Deliverable 1: [DESCRIBE DELIVERABLE]",
                "Deliverable 2: [DESCRIBE DELIVERABLE]",
                "Deliverable 3: [DESCRIBE DELIVERABLE]",
            ]
        add(heading, content, **extra)

    # Fill any structural gaps from the template's suggested sections.
    covered = {s.heading.strip().lower() for s in sections}
    for heading in template_sections:
        lowered = heading.strip().lower()
        if lowered in covered:
            continue
        if lowered == "parties" and sections and sections[0].heading.lower() == "parties":
            continue
        if lowered in {"governing law", "governing law and dispute resolution"} and any(
            s.heading.strip().lower().startswith("governing law") for s in sections
        ):
            continue
        add(
            heading,
            f"[DEMO PLACEHOLDER] This section is reserved for \"{heading}\". In a "
            f"live AI draft this provision would be drafted in full against the "
            f"facts supplied. Review and complete it before execution.",
        )

    if not sections:
        add(
            "Terms",
            "[DEMO PLACEHOLDER] No terms were supplied for this document. Add "
            "clauses in the wizard and regenerate, or write the terms directly "
            "in the editor.",
        )

    return renumber_sections(sections)


def build_demo_draft(
    request: GenerateDocumentRequest,
    *,
    template_title: str,
    template_sections: list[str],
) -> DocumentDraft:
    """Produce a deterministic draft from ``request``. Never calls an API."""
    title = (request.title or "").strip() or template_title

    parties_line = " and ".join(
        _party_phrase(p) for p in request.parties[:2]
    ) or "the parties"
    intro = (
        f"{DEMO_NOTE}\n\n"
        f"This {template_title} is entered into by {parties_line}. "
        f"{_effective_phrase(request)} "
        f"This draft is governed by {_jurisdiction_phrase(request.jurisdiction)}."
    )

    return DocumentDraft(
        title=title,
        intro=intro,
        sections=_build_sections(request, template_sections),
        signature_blocks=[
            SignatureBlock(party_label=p.name, role=p.role)
            for p in request.parties
        ],
        disclaimer=LEGAL_DISCLAIMER,
    )


def build_demo_revision(
    *,
    heading: str,
    content: str,
    action: str,
    custom_instruction: str = "",
) -> str:
    """Deterministic stand-in for a section revision, clearly marked as demo."""
    lead = f"[DEMO AI RESPONSE - {action.replace('_', ' ')}] "

    body = (content or "").strip()
    if not body:
        return (
            f"{lead}This section is currently empty. A live AI revision would draft "
            f"\"{heading}\" in full from the surrounding context. In demo mode the "
            f"text is left as a marked placeholder so it is obvious no live model "
            f"was called."
        )

    lowered = body.lower()
    if action == "shorten":
        sentences = [s.strip() for s in body.replace("\n", " ").split(".") if s.strip()]
        trimmed = ". ".join(sentences[: max(1, len(sentences) // 2)]) or sentences[0]
        trimmed = trimmed.rstrip(".") + "."
        return f"{lead}{trimmed} [DEMO: shortened from {len(body)} to {len(trimmed)} characters]"

    if action == "expand":
        return (
            f"{lead}{body}\n\n[DEMO: expansion placeholder] A live AI revision would "
            f"add the procedural detail, notice mechanics and interaction rules a "
            f"reviewing lawyer would expect in \"{heading}\", using clearly marked "
            f"placeholders for any value not supplied."
        )

    if action == "simplify":
        return (
            f"{lead}{body}\n\n[DEMO: plain-language pass] A live AI revision would "
            f"restate the above in shorter sentences while keeping the legal effect "
            f"identical."
        )

    if action == "fix_grammar":
        notes = []
        if "  " in body:
            notes.append("double spaces")
        if lowered.count("the ") > 6:
            notes.append("repeated determiner usage")
        suffix = (
            f" [DEMO: reviewed for {' and '.join(notes)}]"
            if notes
            else " [DEMO: no mechanical errors detected]"
        )
        return f"{lead}{body}{suffix}"

    if action == "add_protection":
        return (
            f"{lead}{body}\n\n[DEMO: protective provisions placeholder] A live AI "
            f"revision would add notice mechanics, a cure period, materiality "
            f"thresholds, carve-outs and remedies, strengthening \"{heading}\" "
            f"without making it unenforceable."
        )

    if action == "more_formal":
        return (
            f"{lead}{body}\n\n[DEMO: formal-register pass] A live AI revision would "
            f"apply counsel-style drafting conventions and formal connectives while "
            f"preserving the substance exactly."
        )

    instruction = (
        f" {custom_instruction.strip()}" if custom_instruction.strip() else ""
    )
    return (
        f"{lead}{body}\n\n[DEMO: polished rewrite placeholder]{instruction} A live AI "
        f"revision would return rewritten clause text only. Demo mode does not call "
        f"a model, so this marker is left in place."
    )

