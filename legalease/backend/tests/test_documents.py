"""Document CRUD, generation validation, duplication and versioning."""

from __future__ import annotations

import copy


# --- Generation --------------------------------------------------------


def test_generate_creates_a_document(client, payload):
    response = client.post("/api/documents/generate", json=payload)
    assert response.status_code == 201, response.text
    body = response.json()
    document = body["document"]

    assert document["id"]
    assert document["status"] == "generated"
    assert document["document_type"] == "freelance-agreement"
    assert document["effective_date"] == "2026-10-15"
    assert document["jurisdiction"] == "Laws of India"
    assert body["generation_source"] in ("groq", "demo")
    assert body["elapsed_ms"] >= 0


def test_generated_content_is_structured(client, payload):
    content = client.post("/api/documents/generate", json=payload).json()["document"]["content"]

    assert content["title"]
    assert content["intro"]
    assert len(content["sections"]) >= 4

    headings = [s["heading"] for s in content["sections"]]
    # Numbering must be sequential and start at 1.
    for index, heading in enumerate(headings, start=1):
        assert heading.startswith(f"{index}. "), heading

    assert content["signature_blocks"]
    assert {b["party_label"] for b in content["signature_blocks"]} == {
        "Karthikeyan",
        "ABC Technologies",
    }
    assert "not a substitute for advice" in content["disclaimer"].lower()


def test_generation_respects_supplied_parties(client, payload):
    content = client.post("/api/documents/generate", json=payload).json()["document"]["content"]
    joined = content["intro"] + " ".join(s["content"] for s in content["sections"])
    assert "Karthikeyan" in joined
    assert "ABC Technologies" in joined
    assert "Freelancer" in joined


def test_generation_marks_source_in_content(client, payload):
    content = client.post("/api/documents/generate", json=payload).json()["document"]["content"]
    assert content["generation"]["source"] in ("groq", "demo")
    assert content["generation"]["generated_at"]


def test_generation_creates_brand_profile(client, payload):
    response = client.post("/api/documents/generate", json=payload)
    document_id = response.json()["document"]["id"]
    assert response.json()["document"]["brand_id"]

    detail = client.get(f"/api/documents/{document_id}").json()
    assert detail["brand_id"]
    profiles = client.get("/api/branding").json()
    assert profiles["total"] >= 1
    assert profiles["items"][0]["organization_name"] == "ABC Technologies"


# --- Generation validation --------------------------------------------


def test_generate_requires_at_least_one_party(client, payload):
    bad = copy.deepcopy(payload)
    bad["parties"] = []
    response = client.post("/api/documents/generate", json=bad)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_generate_requires_at_least_one_clause(client, payload):
    bad = copy.deepcopy(payload)
    bad["clauses"] = []
    assert client.post("/api/documents/generate", json=bad).status_code == 422


def test_generate_rejects_missing_party_name(client, payload):
    bad = copy.deepcopy(payload)
    bad["parties"][0]["name"] = ""
    assert client.post("/api/documents/generate", json=bad).status_code == 422


def test_generate_rejects_invalid_email(client, payload):
    bad = copy.deepcopy(payload)
    bad["parties"][0]["email"] = "not-an-email"
    assert client.post("/api/documents/generate", json=bad).status_code == 422


def test_generate_rejects_unknown_document_type_length(client, payload):
    bad = copy.deepcopy(payload)
    bad["document_type"] = ""
    assert client.post("/api/documents/generate", json=bad).status_code == 422


def test_generate_rejects_excessive_instructions(client, payload):
    bad = copy.deepcopy(payload)
    bad["additional_instructions"] = "x" * 5000
    assert client.post("/api/documents/generate", json=bad).status_code == 422


def test_generate_rejects_too_many_parties(client, payload):
    bad = copy.deepcopy(payload)
    bad["parties"] = [
        {"name": f"Party {i}", "role": "Signer"} for i in range(25)
    ]
    assert client.post("/api/documents/generate", json=bad).status_code == 422


def test_validation_error_does_not_echo_submitted_values(client, payload):
    bad = copy.deepcopy(payload)
    bad["parties"][0]["email"] = "SENSITIVEVALUE123"
    response = client.post("/api/documents/generate", json=bad)
    assert "SENSITIVEVALUE123" not in response.text
    assert "Traceback" not in response.text


# --- CRUD --------------------------------------------------------------


def test_list_documents(client, generated_document):
    body = client.get("/api/documents").json()
    assert body["meta"]["total"] >= 1
    assert any(d["id"] == generated_document["id"] for d in body["items"])

    item = next(d for d in body["items"] if d["id"] == generated_document["id"])
    assert item["word_count"] > 0
    assert item["section_count"] > 0


def test_get_document(client, generated_document):
    response = client.get(f"/api/documents/{generated_document['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == generated_document["id"]


def test_get_missing_document_is_404(client):
    response = client.get("/api/documents/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_update_title_and_content(client, generated_document):
    document_id = generated_document["id"]
    content = generated_document["content"]
    content["title"] = "Updated Agreement"
    content["sections"][0]["content"] = "Amended parties clause for the test suite."

    response = client.put(
        f"/api/documents/{document_id}",
        json={"title": "Updated Agreement", "content": content},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Agreement"
    assert "Amended parties clause" in response.json()["content"]["sections"][0]["content"]


def test_update_renumbers_sections(client, generated_document):
    document_id = generated_document["id"]
    content = generated_document["content"]
    content["sections"] = content["sections"][:2]
    content["sections"][0]["heading"] = "Parties"
    content["sections"][1]["heading"] = "Services"

    body = client.put(
        f"/api/documents/{document_id}", json={"content": content}
    ).json()
    headings = [s["heading"] for s in body["content"]["sections"]]
    assert headings[0].startswith("1. ")
    assert headings[1].startswith("2. ")


def test_update_status(client, generated_document):
    response = client.patch(
        f"/api/documents/{generated_document['id']}/status",
        json={"status": "completed"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_update_rejects_invalid_status(client, generated_document):
    response = client.patch(
        f"/api/documents/{generated_document['id']}/status",
        json={"status": "banana"},
    )
    assert response.status_code == 422


def test_delete_document(client, generated_document):
    document_id = generated_document["id"]
    assert client.delete(f"/api/documents/{document_id}").status_code == 204
    assert client.get(f"/api/documents/{document_id}").status_code == 404


def test_duplicate_document(client, generated_document):
    response = client.post(f"/api/documents/{generated_document['id']}/duplicate")
    assert response.status_code == 201
    clone = response.json()
    assert clone["id"] != generated_document["id"]
    assert clone["title"].endswith("(Copy)")
    assert clone["status"] == "draft"
    assert len(clone["content"]["sections"]) == len(
        generated_document["content"]["sections"]
    )


def test_list_filters_by_status_and_search(client, generated_document):
    client.patch(
        f"/api/documents/{generated_document['id']}/status", json={"status": "draft"}
    )
    body = client.get("/api/documents", params={"status": "draft"}).json()
    assert body["meta"]["total"] >= 1
    assert all(d["status"] == "draft" for d in body["items"])

    search = client.get("/api/documents", params={"search": "zzzznotfound"}).json()
    assert search["meta"]["total"] == 0


def test_dashboard_stats(client, generated_document):
    body = client.get("/api/documents/stats").json()
    assert body["total_documents"] >= 1
    assert body["generated"] >= 1
    assert body["documents_this_month"] >= 1
    assert body["drafts"] + body["generated"] + body["completed"] == (
        body["total_documents"]
    )


# --- Versioning --------------------------------------------------------


def test_generation_creates_version_one(client, generated_document):
    body = client.get(f"/api/documents/{generated_document['id']}/versions").json()
    assert len(body) == 1
    assert body[0]["version_number"] == 1
    assert "Initial AI draft" in (body[0]["label"] or "")


def test_update_with_create_version_adds_snapshot(client, generated_document):
    document_id = generated_document["id"]
    content = generated_document["content"]
    content["title"] = "Versioned Agreement"
    content["sections"][0]["content"] = "Snapshot me."

    client.put(
        f"/api/documents/{document_id}",
        json={
            "content": content,
            "create_version": True,
            "version_label": "Manual edit",
        },
    )
    versions = client.get(f"/api/documents/{document_id}/versions").json()
    assert len(versions) == 2
    assert versions[0]["version_number"] == 2
    assert versions[0]["label"] == "Manual edit"


def test_update_without_flag_does_not_add_version(client, generated_document):
    document_id = generated_document["id"]
    content = generated_document["content"]
    content["title"] = "Autosaved Title"
    client.put(f"/api/documents/{document_id}", json={"content": content})
    versions = client.get(f"/api/documents/{document_id}/versions").json()
    assert len(versions) == 1


def test_identical_save_does_not_duplicate_version(client, generated_document):
    document_id = generated_document["id"]
    content = generated_document["content"]
    for _ in range(3):
        client.put(
            f"/api/documents/{document_id}",
            json={"content": content, "create_version": True},
        )
    versions = client.get(f"/api/documents/{document_id}/versions").json()
    assert len(versions) == 1


def test_restore_version(client, generated_document):
    document_id = generated_document["id"]
    original_title = generated_document["title"]

    content = generated_document["content"]
    content["title"] = "Broken Title"
    content["sections"][0]["content"] = "Something that should be reverted."
    client.put(
        f"/api/documents/{document_id}",
        json={"content": content, "create_version": True, "version_label": "Bad edit"},
    )

    response = client.post(
        f"/api/documents/{document_id}/versions/1/restore"
    )
    assert response.status_code == 200
    assert response.json()["title"] == original_title
    assert (
        "Something that should be reverted."
        not in response.json()["content"]["sections"][0]["content"]
    )

    # The restore itself is recorded, so it is reversible.
    versions = client.get(f"/api/documents/{document_id}/versions").json()
    assert len(versions) >= 3


def test_restore_missing_version_is_404(client, generated_document):
    response = client.post(
        f"/api/documents/{generated_document['id']}/versions/99/restore"
    )
    assert response.status_code == 404


def test_versions_for_unknown_document_is_404(client):
    assert client.get("/api/documents/nope/versions").status_code == 404
