"""Template catalog endpoints. These must work with zero database records."""

from __future__ import annotations

import pytest


def test_lists_all_eighteen_document_types(client):
    body = client.get("/api/templates").json()
    assert body["total"] == 18
    ids = {item["id"] for item in body["items"]}
    assert {
        "nda",
        "employment-contract",
        "offer-letter",
        "freelance-agreement",
        "service-agreement",
        "residential-lease",
        "rental-agreement",
        "partnership-agreement",
        "business-agreement",
        "consulting-agreement",
        "vendor-agreement",
        "mou",
        "terms-and-conditions",
        "privacy-policy",
        "loan-agreement",
        "purchase-agreement",
        "internship-agreement",
        "custom",
    } <= ids


def test_every_template_has_required_display_fields(client):
    for item in client.get("/api/templates").json()["items"]:
        assert item["title"]
        assert item["description"]
        assert item["icon"]
        assert item["category"]
        assert item["estimated_minutes"] >= 1


def test_categories_cover_the_specified_set(client):
    categories = set(client.get("/api/templates").json()["categories"])
    assert categories == {
        "Business",
        "Employment",
        "Freelance",
        "Property",
        "Privacy",
        "Partnership",
        "Personal",
    }


def test_search_filters_templates(client):
    lease = client.get("/api/templates", params={"search": "lease"}).json()
    assert lease["total"] >= 1
    assert any(t["id"] == "residential-lease" for t in lease["items"])

    nda = client.get("/api/templates", params={"search": "confidential"}).json()
    assert any(t["id"] == "nda" for t in nda["items"])

    assert client.get("/api/templates", params={"search": "zzz"}).json()["total"] == 0


def test_category_filter(client):
    body = client.get("/api/templates", params={"category": "Privacy"}).json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == "privacy-policy"


def test_unknown_template_is_404(client):
    response = client.get("/api/templates/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_five_sample_templates_available(client):
    body = client.get("/api/templates").json()
    with_sample = {i["id"] for i in body["items"] if i["has_sample_data"]}
    assert {
        "nda",
        "freelance-agreement",
        "employment-contract",
        "residential-lease",
        "service-agreement",
    } <= with_sample


@pytest.mark.parametrize(
    "template_id",
    ["nda", "freelance-agreement", "employment-contract", "residential-lease", "service-agreement"],
)
def test_sample_data_is_complete(client, template_id):
    body = client.get(f"/api/templates/{template_id}/sample").json()
    payload = body["payload"]
    assert payload["document_type"] == template_id
    assert len(payload["parties"]) >= 2
    assert len(payload["clauses"]) >= 3
    assert payload["jurisdiction"]
    assert payload["branding"]


def test_sample_missing_for_template_without_one(client):
    response = client.get("/api/templates/loan-agreement/sample")
    assert response.status_code == 404


def test_clause_suggestions_include_the_documented_set(client):
    keys = {item["key"] for item in client.get("/api/clauses").json()["items"]}
    assert {
        "payment_terms",
        "confidentiality",
        "intellectual_property",
        "termination",
        "governing_law",
        "dispute_resolution",
        "liability",
        "deliverables",
        "deadlines",
        "non_compete",
        "force_majeure",
    } <= keys


def test_rewrite_actions_expose_all_seven(client):
    items = client.get("/api/rewrite-actions").json()["items"]
    assert len(items) == 7
    labels = {item["label"] for item in items}
    assert "Rewrite professionally" in labels
    assert "Add protection clause" in labels
