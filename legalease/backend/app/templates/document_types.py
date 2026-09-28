"""The document template catalog.

Each entry is a self-contained template definition. Adding a new legal document
type means appending one ``DocumentTypeDefinition`` here - no schema, route,
service or UI change is required. The frontend renders whatever this module
returns, so new types appear automatically.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Category = Literal[
    "Business",
    "Employment",
    "Freelance",
    "Property",
    "Privacy",
    "Partnership",
    "Personal",
]

# Clause presets surfaced as one-tap suggestions in the wizard.
COMMON_CLAUSES: list[dict[str, object]] = [
    {
        "key": "payment_terms",
        "title": "Payment Terms",
        "description": "Amount, currency, invoicing schedule and late-payment consequences.",
    },
    {
        "key": "confidentiality",
        "title": "Confidentiality",
        "description": "Mutual obligations to protect non-public information, with survival.",
    },
    {
        "key": "intellectual_property",
        "title": "Intellectual Property",
        "description": "Ownership of work product, pre-existing IP and licence grants.",
    },
    {
        "key": "termination",
        "title": "Termination",
        "description": "Grounds, notice period and consequences of early termination.",
    },
    {
        "key": "governing_law",
        "title": "Governing Law",
        "description": "Jurisdiction whose laws govern, and the forum for disputes.",
    },
    {
        "key": "dispute_resolution",
        "title": "Dispute Resolution",
        "description": "Negotiation, mediation or arbitration before litigation.",
    },
    {
        "key": "liability",
        "title": "Limitation of Liability",
        "description": "Cap on aggregate liability and exclusion of indirect damages.",
    },
    {
        "key": "deliverables",
        "title": "Deliverables",
        "description": "Scope of work, acceptance criteria and revision rounds.",
    },
    {
        "key": "deadlines",
        "title": "Deadlines",
        "description": "Milestones, delivery dates and consequences of delay.",
    },
    {
        "key": "non_compete",
        "title": "Non-Compete",
        "description": "Restriction on competing activity for a defined period and territory.",
    },
    {
        "key": "force_majeure",
        "title": "Force Majeure",
        "description": "Relief for events beyond either party's reasonable control.",
    },
    {
        "key": "data_protection",
        "title": "Data Protection",
        "description": "Processing of personal data and compliance with applicable privacy law.",
    },
    {
        "key": "assignment",
        "title": "Assignment",
        "description": "Restrictions on transferring rights or delegating obligations.",
    },
    {
        "key": "notices",
        "title": "Notices",
        "description": "How formal notices must be delivered and when they take effect.",
    },
    {
        "key": "entire_agreement",
        "title": "Entire Agreement",
        "description": "Supersedes prior discussions, proposals and representations.",
    },
    {
        "key": "severability",
        "title": "Severability",
        "description": "Effect of any provision being held invalid or unenforceable.",
    },
]


class DocumentTypeDefinition(BaseModel):
    """A selectable legal document template."""

    id: str
    title: str
    slug: str
    description: str
    category: Category
    icon: str
    estimated_minutes: int = Field(ge=1, le=60)
    default_title: str
    # Section headings the AI is steered towards, in order.
    suggested_sections: list[str] = Field(default_factory=list)
    suggested_clauses: list[str] = Field(default_factory=list)
    sample: bool = False
    popular: bool = False


_T: DocumentTypeDefinition


def _tpl(
    *,
    id: str,
    title: str,
    slug: str,
    description: str,
    category: Category,
    icon: str,
    minutes: int,
    default_title: str,
    sections: list[str],
    clauses: list[str],
    sample: bool = False,
    popular: bool = False,
) -> _T:
    return DocumentTypeDefinition(
        id=id,
        title=title,
        slug=slug,
        description=description,
        category=category,
        icon=icon,
        estimated_minutes=minutes,
        default_title=default_title,
        suggested_sections=sections,
        suggested_clauses=clauses,
        sample=sample,
        popular=popular,
    )


DOCUMENT_TYPES: list[DocumentTypeDefinition] = [
    _tpl(
        id="nda",
        title="Non-Disclosure Agreement",
        slug="non-disclosure-agreement",
        description=(
            "Protect confidential information shared between two parties during "
            "discussions, evaluations or a project."
        ),
        category="Business",
        icon="shield-check",
        minutes=4,
        default_title="Non-Disclosure Agreement",
        sections=[
            "Parties",
            "Purpose of Disclosure",
            "Definition of Confidential Information",
            "Obligations of the Receiving Party",
            "Exclusions from Confidentiality",
            "Term and Survival",
            "Return or Destruction of Information",
            "Remedies",
            "Governing Law",
        ],
        clauses=["confidentiality", "notices", "entire_agreement", "severability"],
        sample=True,
        popular=True,
    ),
    _tpl(
        id="employment-contract",
        title="Employment Contract",
        slug="employment-contract",
        description=(
            "Full terms of employment covering role, compensation, duties, "
            "benefits, confidentiality and termination."
        ),
        category="Employment",
        icon="briefcase",
        minutes=8,
        default_title="Employment Contract",
        sections=[
            "Parties and Position",
            "Commencement of Employment",
            "Duties and Responsibilities",
            "Place of Work",
            "Working Hours and Leave",
            "Compensation and Benefits",
            "Probation Period",
            "Confidentiality",
            "Intellectual Property",
            "Termination of Employment",
            "Governing Law",
        ],
        clauses=[
            "confidentiality",
            "intellectual_property",
            "termination",
            "non_compete",
            "governing_law",
        ],
        sample=True,
        popular=True,
    ),
    _tpl(
        id="offer-letter",
        title="Employment Offer Letter",
        slug="employment-offer-letter",
        description=(
            "A concise offer setting out position, start date, salary, benefits "
            "and conditions of employment."
        ),
        category="Employment",
        icon="mail-open",
        minutes=3,
        default_title="Employment Offer Letter",
        sections=[
            "Offer of Employment",
            "Position and Reporting Line",
            "Start Date",
            "Compensation",
            "Benefits",
            "Conditions of Employment",
            "Probationary Period",
            "Confidentiality",
            "Acceptance",
        ],
        clauses=["confidentiality", "termination", "governing_law"],
    ),
    _tpl(
        id="freelance-agreement",
        title="Freelance Agreement",
        slug="freelance-agreement",
        description=(
            "Engage an independent contractor for defined deliverables, with "
            "clear payment, IP and termination terms."
        ),
        category="Freelance",
        icon="pen-tool",
        minutes=6,
        default_title="Freelance Services Agreement",
        sections=[
            "Parties",
            "Scope of Services",
            "Deliverables and Acceptance",
            "Fees and Payment Terms",
            "Timeline and Deadlines",
            "Independent Contractor Status",
            "Intellectual Property",
            "Confidentiality",
            "Representations and Warranties",
            "Indemnification",
            "Limitation of Liability",
            "Termination",
            "Governing Law",
        ],
        clauses=[
            "payment_terms",
            "deliverables",
            "deadlines",
            "intellectual_property",
            "confidentiality",
            "termination",
            "liability",
            "governing_law",
        ],
        sample=True,
        popular=True,
    ),
    _tpl(
        id="service-agreement",
        title="Service Agreement",
        slug="service-agreement",
        description=(
            "A master agreement for ongoing professional or technical services "
            "between a provider and a client."
        ),
        category="Business",
        icon="handshake",
        minutes=7,
        default_title="Service Agreement",
        sections=[
            "Parties",
            "Scope of Services",
            "Service Levels",
            "Fees and Invoicing",
            "Client Responsibilities",
            "Intellectual Property",
            "Confidentiality",
            "Data Protection",
            "Warranties",
            "Indemnities",
            "Limitation of Liability",
            "Term and Termination",
            "Governing Law and Dispute Resolution",
        ],
        clauses=[
            "payment_terms",
            "deliverables",
            "confidentiality",
            "data_protection",
            "liability",
            "termination",
            "force_majeure",
            "governing_law",
        ],
        sample=True,
        popular=True,
    ),
    _tpl(
        id="residential-lease",
        title="Residential Lease Agreement",
        slug="residential-lease-agreement",
        description=(
            "Lease a residential property with rent, deposit, utilities, repairs "
            "and tenant obligations."
        ),
        category="Property",
        icon="home",
        minutes=8,
        default_title="Residential Lease Agreement",
        sections=[
            "Parties",
            "Premises",
            "Term of Lease",
            "Rent",
            "Security Deposit",
            "Utilities and Services",
            "Use of Premises",
            "Maintenance and Repairs",
            "Alterations and Improvements",
            "Assignment and Subletting",
            "Default and Remedies",
            "Entry by Landlord",
            "Surrender of Premises",
        ],
        clauses=["payment_terms", "liability", "termination", "notices", "governing_law"],
        sample=True,
    ),
    _tpl(
        id="rental-agreement",
        title="Rental Agreement",
        slug="rental-agreement",
        description=(
            "Rent out a property or equipment for a fixed period with clear "
            "deposit, damage and return terms."
        ),
        category="Property",
        icon="key-round",
        minutes=5,
        default_title="Rental Agreement",
        sections=[
            "Parties",
            "Property Description",
            "Rental Period",
            "Rental Amount and Payment",
            "Security Deposit",
            "Condition of Property",
            "Permitted Use",
            "Maintenance and Repairs",
            "Insurance",
            "Early Termination",
            "Return of Property",
        ],
        clauses=["payment_terms", "liability", "termination", "notices"],
    ),
    _tpl(
        id="partnership-agreement",
        title="Partnership Agreement",
        slug="partnership-agreement",
        description=(
            "Define profit sharing, capital contributions, management authority "
            "and exit terms between partners."
        ),
        category="Partnership",
        icon="users-round",
        minutes=8,
        default_title="Partnership Agreement",
        sections=[
            "Parties",
            "Formation and Purpose",
            "Name and Nature of the Partnership",
            "Capital Contributions",
            "Profit and Loss Distribution",
            "Management and Authority",
            "Duties and Responsibilities",
            "Accounts and Records",
            "Admission of New Partners",
            "Transfer of Interest",
            "Death, Withdrawal and Dissolution",
            "Dispute Resolution",
            "Governing Law",
        ],
        clauses=["confidentiality", "liability", "termination", "governing_law"],
    ),
    _tpl(
        id="business-agreement",
        title="Business Agreement",
        slug="business-agreement",
        description=(
            "A general-purpose agreement for a commercial arrangement between "
            "two businesses."
        ),
        category="Business",
        icon="building-2",
        minutes=6,
        default_title="Business Agreement",
        sections=[
            "Parties",
            "Purpose",
            "Term",
            "Commercial Terms",
            "Roles and Responsibilities",
            "Intellectual Property",
            "Confidentiality",
            "Exclusivity",
            "Representations and Warranties",
            "Indemnification",
            "Limitation of Liability",
            "Termination",
            "General Provisions",
        ],
        clauses=[
            "payment_terms",
            "confidentiality",
            "intellectual_property",
            "termination",
            "liability",
            "force_majeure",
            "governing_law",
        ],
    ),
    _tpl(
        id="consulting-agreement",
        title="Consulting Agreement",
        slug="consulting-agreement",
        description=(
            "Engage a consultant for advisory services with an agreed day rate "
            "or fixed fee and defined scope."
        ),
        category="Business",
        icon="compass",
        minutes=5,
        default_title="Consulting Agreement",
        sections=[
            "Parties",
            "Engagement and Scope",
            "Consulting Services",
            "Fees and Expenses",
            "Time and Availability",
            "Deliverables",
            "Conflicts of Interest",
            "Confidentiality",
            "Intellectual Property",
            "Termination",
            "Governing Law",
        ],
        clauses=[
            "payment_terms",
            "deliverables",
            "confidentiality",
            "non_compete",
            "termination",
            "governing_law",
        ],
    ),
    _tpl(
        id="vendor-agreement",
        title="Vendor Agreement",
        slug="vendor-agreement",
        description=(
            "Set terms for purchasing goods or services from a supplier, "
            "including pricing, delivery and quality standards."
        ),
        category="Business",
        icon="truck",
        minutes=6,
        default_title="Vendor Agreement",
        sections=[
            "Parties",
            "Products and Services",
            "Purchase Orders",
            "Pricing and Taxes",
            "Payment Terms",
            "Delivery",
            "Inspection and Acceptance",
            "Quality Standards",
            "Warranties",
            "Intellectual Property",
            "Confidentiality",
            "Limitation of Liability",
            "Term and Termination",
            "Governing Law",
        ],
        clauses=[
            "payment_terms",
            "deliverables",
            "liability",
            "confidentiality",
            "force_majeure",
            "termination",
            "governing_law",
        ],
    ),
    _tpl(
        id="mou",
        title="Memorandum of Understanding",
        slug="memorandum-of-understanding",
        description=(
            "Record the preliminary understanding between parties before a formal "
            "contract is executed."
        ),
        category="Business",
        icon="file-signature",
        minutes=4,
        default_title="Memorandum of Understanding",
        sections=[
            "Parties",
            "Purpose",
            "Scope of Discussion",
            "Key Terms Understood",
            "Roles of the Parties",
            "Confidentiality",
            "Costs and Expenses",
            "Exclusivity",
            "Term of this Memorandum",
            "Governing Law",
        ],
        clauses=["confidentiality", "notices", "entire_agreement", "governing_law"],
    ),
    _tpl(
        id="terms-and-conditions",
        title="Terms and Conditions",
        slug="terms-and-conditions",
        description=(
            "Standard terms governing the use of a product, service or online "
            "platform."
        ),
        category="Business",
        icon="scroll-text",
        minutes=6,
        default_title="Terms and Conditions",
        sections=[
            "Acceptance of Terms",
            "Eligibility",
            "User Accounts",
            "Permitted Use",
            "Prohibited Conduct",
            "Intellectual Property",
            "Third-Party Services",
            "Disclaimers",
            "Limitation of Liability",
            "Indemnification",
            "Modifications",
            "Termination",
            "Governing Law",
        ],
        clauses=["liability", "confidentiality", "data_protection", "termination", "governing_law"],
    ),
    _tpl(
        id="privacy-policy",
        title="Privacy Policy",
        slug="privacy-policy",
        description=(
            "Disclose how personal data is collected, used, shared and protected."
        ),
        category="Privacy",
        icon="shield",
        minutes=6,
        default_title="Privacy Policy",
        sections=[
            "Introduction",
            "Who We Are",
            "Information We Collect",
            "How We Use Information",
            "Legal Bases for Processing",
            "Cookies and Tracking",
            "Sharing and Disclosure",
            "Data Retention",
            "Security",
            "Your Rights",
            "Children's Privacy",
            "International Transfers",
            "Changes to This Policy",
            "Contact Us",
        ],
        clauses=["data_protection", "liability", "notices"],
    ),
    _tpl(
        id="loan-agreement",
        title="Loan Agreement",
        slug="loan-agreement",
        description=(
            "Set out the terms of a loan including principal, interest, "
            "repayment schedule and security."
        ),
        category="Personal",
        icon="landmark",
        minutes=7,
        default_title="Loan Agreement",
        sections=[
            "Parties",
            "Principal Amount",
            "Interest",
            "Repayment Schedule",
            "Payment Terms",
            "Security and Collateral",
            "Representations and Warranties",
            "Default",
            "Events of Default",
            "Remedies",
            "Governing Law",
        ],
        clauses=["payment_terms", "liability", "notices", "force_majeure", "governing_law"],
    ),
    _tpl(
        id="purchase-agreement",
        title="Purchase Agreement",
        slug="purchase-agreement",
        description=(
            "Contract for the sale of goods or assets, covering price, delivery, "
            "title and risk of loss."
        ),
        category="Business",
        icon="shopping-bag",
        minutes=6,
        default_title="Purchase Agreement",
        sections=[
            "Parties",
            "Subject Matter of the Sale",
            "Purchase Price",
            "Payment Terms",
            "Delivery",
            "Title and Risk",
            "Inspection and Acceptance",
            "Representations and Warranties",
            "Indemnification",
            "Breach",
            "Limitation of Liability",
            "Term and Termination",
            "Governing Law",
        ],
        clauses=[
            "payment_terms",
            "deliverables",
            "liability",
            "force_majeure",
            "governing_law",
        ],
    ),
    _tpl(
        id="internship-agreement",
        title="Internship Agreement",
        slug="internship-agreement",
        description=(
            "Set expectations, compensation, duration and confidentiality for an "
            "internship placement."
        ),
        category="Employment",
        icon="graduation-cap",
        minutes=4,
        default_title="Internship Agreement",
        sections=[
            "Parties",
            "Position and Duties",
            "Term of Internship",
            "Working Hours",
            "Compensation and Benefits",
            "Confidentiality",
            "Intellectual Property",
            "Leave and Absence",
            "Termination",
            "Governing Law",
        ],
        clauses=["confidentiality", "intellectual_property", "termination", "governing_law"],
    ),
    _tpl(
        id="custom",
        title="Custom Legal Document",
        slug="custom-legal-document",
        description=(
            "Start from a blank structure and describe the agreement you need in "
            "your own words."
        ),
        category="Personal",
        icon="sparkles",
        minutes=5,
        default_title="Legal Agreement",
        sections=[
            "Parties",
            "Purpose",
            "Terms of the Arrangement",
            "Obligations of the Parties",
            "Term",
            "General Provisions",
        ],
        clauses=["confidentiality", "termination", "governing_law"],
    ),
]

DOCUMENT_TYPES_BY_ID: dict[str, DocumentTypeDefinition] = {
    t.id: t for t in DOCUMENT_TYPES
}

CATEGORIES: list[Category] = [
    "Business",
    "Employment",
    "Freelance",
    "Property",
    "Privacy",
    "Partnership",
    "Personal",
]


def get_document_type(type_id: str) -> DocumentTypeDefinition | None:
    """Look up a template by id, falling back to slug match."""
    if type_id in DOCUMENT_TYPES_BY_ID:
        return DOCUMENT_TYPES_BY_ID[type_id]
    lowered = (type_id or "").strip().lower()
    for template in DOCUMENT_TYPES:
        if template.slug == lowered or template.title.lower() == lowered:
            return template
    return None
