"""Prefilled sample wizard data.

Powers the "Load sample data" action in the wizard so the flow can be
demonstrated (and tested) without typing anything by hand.
"""

from __future__ import annotations

from typing import Any


def _party(name: str, role: str, **kw: Any) -> dict[str, Any]:
    return {
        "name": name,
        "role": role,
        "organization": kw.get("organization"),
        "address": kw.get("address"),
        "email": kw.get("email"),
        "phone": kw.get("phone"),
    }


def _clause(key: str, title: str, description: str, required: bool = True) -> dict[str, Any]:
    return {
        "clause_key": key,
        "title": title,
        "description": description,
        "is_required": required,
    }


SAMPLE_DATA: dict[str, dict[str, Any]] = {
    "nda": {
        "label": "Mutual NDA",
        "summary": "Two parties sharing business information ahead of a partnership discussion.",
        "payload": {
            "document_type": "nda",
            "parties": [
                _party(
                    "Priya Raman",
                    "Disclosing Party",
                    organization="Northwind Analytics",
                    address="42 Brigade Road, Chennai 600001, India",
                    email="priya.raman@northwind.example",
                ),
                _party(
                    "Daniel Okafor",
                    "Receiving Party",
                    organization="Blue Harbor Ventures",
                    address="18 Fenchurch Avenue, London EC3M 5AD, United Kingdom",
                    email="daniel.okafor@blueharbor.example",
                ),
            ],
            "clauses": [
                _clause(
                    "confidentiality",
                    "Confidentiality",
                    "Each party must protect the other's confidential information with no less than reasonable care.",
                ),
                _clause(
                    "term",
                    "Term and Survival",
                    "Confidentiality obligations survive for three years from the date of disclosure.",
                ),
                _clause(
                    "return",
                    "Return or Destruction",
                    "On written request, confidential information must be returned or securely destroyed.",
                ),
                _clause(
                    "governing_law",
                    "Governing Law",
                    "This agreement is governed by the laws of England and Wales.",
                ),
            ],
            "effective_date": "2026-10-01",
            "expiry_date": "2027-10-01",
            "jurisdiction": {
                "country": "United Kingdom",
                "state": "England",
                "city": "London",
                "governing_law": "England and Wales",
            },
            "branding": {
                "organization_name": "Northwind Analytics",
                "address": "42 Brigade Road, Chennai 600001, India",
                "email": "legal@northwind.example",
                "phone": "+44 20 7946 0000",
                "website": "www.northwind.example",
                "footer_text": "Northwind Analytics - Confidential",
            },
            "additional_instructions": (
                "Keep the agreement mutual and commercially neutral. Do not include "
                "non-compete or exclusivity obligations."
            ),
        },
    },
    "employment-contract": {
        "label": "Full-time Engineer",
        "summary": "Permanent engineering role with a six-month probation period.",
        "payload": {
            "document_type": "employment-contract",
            "parties": [
                _party(
                    "Marcus Bell",
                    "Employer",
                    organization="Northwind Analytics",
                    address="42 Brigade Road, Chennai 600001, India",
                    email="hr@northwind.example",
                    phone="+91 44 4000 1234",
                ),
                _party(
                    "Aisha Khan",
                    "Employee",
                    address="7 Residency Road, Bengaluru 560025, India",
                    email="aisha.khan@example.com",
                    phone="+91 98860 11223",
                ),
            ],
            "clauses": [
                _clause(
                    "compensation",
                    "Compensation and Benefits",
                    "Annual salary of INR 24,00,000 paid monthly, plus statutory benefits.",
                ),
                _clause(
                    "probation",
                    "Probation Period",
                    "A six-month probation period applies, extendable by three months once.",
                ),
                _clause(
                    "confidentiality",
                    "Confidentiality",
                    "The employee must not disclose proprietary information during or after employment.",
                ),
                _clause(
                    "ip",
                    "Intellectual Property",
                    "All work product created in the course of employment vests in the employer.",
                ),
                _clause(
                    "termination",
                    "Termination",
                    "Either party may terminate with one month's written notice or payment in lieu.",
                ),
            ],
            "effective_date": "2026-11-01",
            "expiry_date": None,
            "jurisdiction": {
                "country": "India",
                "state": "Tamil Nadu",
                "city": "Chennai",
                "governing_law": "Laws of India, Tamil Nadu",
            },
            "branding": {
                "organization_name": "Northwind Analytics",
                "address": "42 Brigade Road, Chennai 600001, India",
                "email": "hr@northwind.example",
                "phone": "+91 44 4000 1234",
                "website": "www.northwind.example",
                "footer_text": "Northwind Analytics - Human Resources",
            },
            "additional_instructions": (
                "Reference the Shops and Establishments Act where relevant and keep "
                "the tone formal and compliant."
            ),
        },
    },
    "freelance-agreement": {
        "label": "Design Retainer",
        "summary": "Fixed-fee design engagement with clear IP transfer on payment.",
        "payload": {
            "document_type": "freelance-agreement",
            "parties": [
                _party(
                    "Karthikeyan",
                    "Freelancer",
                    address="12 Anna Salai, Chennai 600002, India",
                    email="karthikeyan@example.com",
                    phone="+91 90000 12345",
                ),
                _party(
                    "ABC Technologies",
                    "Client",
                    organization="ABC Technologies",
                    address="5 Park Street, Kolkata 700016, India",
                    email="accounts@abctech.example",
                ),
            ],
            "clauses": [
                _clause(
                    "payment_terms",
                    "Payment Terms",
                    "Payment is due within 15 days of delivery of each milestone.",
                ),
                _clause(
                    "deadlines",
                    "Deadlines",
                    "The project must be completed within 30 days of the effective date.",
                ),
                _clause(
                    "confidentiality",
                    "Confidentiality",
                    "Both parties must maintain confidentiality of all shared information.",
                ),
                _clause(
                    "termination",
                    "Termination",
                    "Either party may terminate with 15 days written notice.",
                ),
            ],
            "effective_date": "2026-10-15",
            "expiry_date": None,
            "jurisdiction": {
                "country": "India",
                "state": "Tamil Nadu",
                "city": "Chennai",
                "governing_law": "Laws of India",
            },
            "branding": {
                "organization_name": "ABC Technologies",
                "email": "legal@abctech.example",
                "website": "www.abctech.example",
                "footer_text": "ABC Technologies",
            },
            "additional_instructions": (
                "Keep clause numbering sequential and use British English spelling."
            ),
        },
    },
    "residential-lease": {
        "label": "12-Month Tenancy",
        "summary": "Furnished apartment lease with a two-month deposit.",
        "payload": {
            "document_type": "residential-lease",
            "parties": [
                _party(
                    "Sofia Almeida",
                    "Landlord",
                    address="88 Marine Drive, Mumbai 400020, India",
                    email="sofia.almeida@example.com",
                    phone="+91 98200 44556",
                ),
                _party(
                    "Rahul Verma",
                    "Tenant",
                    address="31 Lodhi Estate, New Delhi 110003, India",
                    email="rahul.verma@example.com",
                ),
            ],
            "clauses": [
                _clause(
                    "rent",
                    "Rent",
                    "Monthly rent of INR 45,000, payable in advance on the first day of each month.",
                ),
                _clause(
                    "deposit",
                    "Security Deposit",
                    "A refundable security deposit equivalent to two months' rent.",
                ),
                _clause(
                    "repairs",
                    "Maintenance and Repairs",
                    "The landlord handles structural repairs; the tenant handles minor upkeep.",
                ),
            ],
            "effective_date": "2026-12-01",
            "expiry_date": "2027-11-30",
            "jurisdiction": {
                "country": "India",
                "state": "Maharashtra",
                "city": "Mumbai",
                "governing_law": "Laws of India, Maharashtra",
            },
            "branding": {
                "organization_name": "Almeida Properties",
                "email": "tenancy@almeida.example",
                "phone": "+91 98200 44556",
                "footer_text": "Almeida Properties",
            },
            "additional_instructions": (
                "Include an inventory of furnished items in a table and a clause on "
                "leave and licence compliance."
            ),
        },
    },
    "service-agreement": {
        "label": "Managed IT Retainer",
        "summary": "Ongoing support retainer with defined response times.",
        "payload": {
            "document_type": "service-agreement",
            "parties": [
                _party(
                    "Lena Fischer",
                    "Service Provider",
                    organization="Blue Harbor Ventures",
                    address="18 Fenchurch Avenue, London EC3M 5AD, United Kingdom",
                    email="contracts@blueharbor.example",
                ),
                _party(
                    "Tom Whitfield",
                    "Client",
                    organization="Meridian Retail Group",
                    address="9 King Street, Manchester M2 6AG, United Kingdom",
                    email="procurement@meridian.example",
                ),
            ],
            "clauses": [
                _clause(
                    "sla",
                    "Service Levels",
                    "Priority 1 incidents receive a response within 2 business hours.",
                ),
                _clause(
                    "payment_terms",
                    "Fees and Invoicing",
                    "Monthly retainer invoiced on the first business day, payable net 30.",
                ),
                _clause(
                    "data_protection",
                    "Data Protection",
                    "Personal data is processed only on documented instructions from the client.",
                ),
                _clause(
                    "liability",
                    "Limitation of Liability",
                    "Aggregate liability is capped at the fees paid in the preceding 12 months.",
                ),
            ],
            "effective_date": "2026-11-01",
            "expiry_date": "2027-10-31",
            "jurisdiction": {
                "country": "United Kingdom",
                "state": "England",
                "city": "London",
                "governing_law": "England and Wales",
            },
            "branding": {
                "organization_name": "Blue Harbor Ventures",
                "address": "18 Fenchurch Avenue, London EC3M 5AD, United Kingdom",
                "email": "contracts@blueharbor.example",
                "phone": "+44 20 7946 0958",
                "website": "www.blueharbor.example",
                "footer_text": "Blue Harbor Ventures - Confidential",
            },
            "additional_instructions": (
                "Include a service credit mechanism and reference the UK GDPR in the "
                "data protection clause."
            ),
        },
    },
}


def get_sample(document_type_id: str) -> dict[str, Any] | None:
    return SAMPLE_DATA.get(document_type_id)
