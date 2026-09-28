"""PDF, DOCX and TXT export behaviour."""

from __future__ import annotations

import io
import zipfile

from docx import Document as DocxReader


def _export(client, document_id: str, fmt: str):
    return client.get(f"/api/documents/{document_id}/export/{fmt}")


# --- PDF ---------------------------------------------------------------


def test_pdf_export_returns_a_valid_pdf(client, generated_document):
    response = _export(client, generated_document["id"], "pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")
    assert len(response.content) > 1500


def test_pdf_declares_a4_page_size(client, generated_document):
    response = _export(client, generated_document["id"], "pdf")
    data = response.content
    # A4 is 595.27 x 841.89 pt; ReportLab emits the MediaBox either way.
    assert b"MediaBox" in data
    assert b"595" in data and b"841" in data


def test_pdf_paginates_with_page_numbers(client, payload):
    long_payload = dict(payload)
    long_payload["clauses"] = payload["clauses"] + [
        {
            "clause_key": f"extra-{i}",
            "title": f"Additional Provision {i}",
            "description": "This is filler content. " * 60,
            "is_required": False,
        }
        for i in range(8)
    ]
    document_id = client.post("/api/documents/generate", json=long_payload).json()[
        "document"
    ]["id"]
    data = _export(client, document_id, "pdf").content
    assert data.count(b"/Type /Page") >= 2 or data.count(b"/Type/Page") >= 2
    assert b"Page" in data


def test_pdf_uses_a_safe_download_filename(client, generated_document):
    response = _export(client, generated_document["id"], "pdf")
    disposition = response.headers["content-disposition"]
    assert disposition.startswith("attachment;")
    filename = disposition.split('filename="')[1].rstrip('"')
    assert filename.endswith(".pdf")
    assert filename.isascii()


def test_pdf_filename_is_sanitised(client, generated_document):
    document_id = generated_document["id"]
    content = client.get(f"/api/documents/{document_id}").json()["content"]
    content["title"] = "../../etc/passwd" * 5
    client.put(f"/api/documents/{document_id}", json={"content": content})

    disposition = _export(client, document_id, "pdf").headers["content-disposition"]
    filename = disposition.split('filename="')[1].rstrip('"')
    assert "/" not in filename
    assert ".." not in filename
    assert filename == "etcpasswdetcpasswdetcpasswdetcpasswdetcpasswdetcpasswdetcpasswdetcpasswdetc.pdf"[:89] or len(filename) <= 90


# --- DOCX --------------------------------------------------------------


def test_docx_export_returns_a_valid_docx(client, generated_document):
    response = _export(client, generated_document["id"], "docx")
    assert response.status_code == 200
    assert "wordprocessingml" in response.headers["content-type"]
    assert response.content.startswith(b"PK\x03\x04")
    assert len(response.content) > 1000


def test_docx_is_a_readable_zip(client, generated_document):
    response = _export(client, generated_document["id"], "docx")
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        assert archive.testzip() is None
        assert "word/document.xml" in archive.namelist()


def test_docx_uses_times_new_roman(client, generated_document):
    """The font name lives in the compressed styles part, so read the zip."""
    response = _export(client, generated_document["id"], "docx")
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        styles = archive.read("word/styles.xml").decode("utf-8")
        document_xml = archive.read("word/document.xml").decode("utf-8")
    assert "Times New Roman" in styles
    assert "Times New Roman" in document_xml


def test_docx_contains_sections_and_signatures(client, generated_document):
    response = _export(client, generated_document["id"], "docx")
    document = DocxReader(io.BytesIO(response.content))
    text = "\n".join(p.text for p in document.paragraphs)
    assert generated_document["content"]["sections"][0]["heading"] in text
    assert "SIGNATURES" in text
    assert "not a substitute for advice" in text.lower()


def test_docx_has_a_footer_with_page_field(client, generated_document):
    response = _export(client, generated_document["id"], "docx")
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        footer_names = [n for n in archive.namelist() if "footer" in n]
        assert footer_names
        footer_xml = archive.read(footer_names[0]).decode("utf-8")
        assert "PAGE" in footer_xml


def test_docx_table_renders_when_section_has_one(client, payload):
    response = client.post("/api/documents/generate", json=payload).json()
    document = response["document"]
    document_id = document["id"]

    content = document["content"]
    content["sections"][0]["table"] = {
        "caption": "Key terms",
        "headers": ["Item", "Detail"],
        "rows": [["Effective date", "2026-10-15"], ["Governing law", "Laws of India"]],
    }
    client.put(f"/api/documents/{document_id}", json={"content": content})

    docx_bytes = _export(client, document_id, "docx").content
    parsed = DocxReader(io.BytesIO(docx_bytes))
    assert len(parsed.tables) >= 1


# --- TXT ---------------------------------------------------------------


def test_txt_export_is_plain_text(client, generated_document):
    response = _export(client, generated_document["id"], "txt")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    text = response.text
    assert generated_document["content"]["sections"][0]["heading"].upper() in text
    assert "SIGNATURES" in text
    assert len(text) > 500


def test_txt_includes_every_party(client, generated_document):
    text = _export(client, generated_document["id"], "txt").text
    assert "Karthikeyan" in text
    assert "ABC Technologies" in text


def test_txt_contains_the_disclaimer(client, generated_document):
    text = _export(client, generated_document["id"], "txt").text
    assert "not a substitute for advice" in text.lower()


def test_txt_has_safe_filename(client, generated_document):
    disposition = _export(client, generated_document["id"], "txt").headers[
        "content-disposition"
    ]
    assert disposition.endswith('.txt"')


# --- Cross-cutting -----------------------------------------------------


def test_export_unknown_document_is_404(client):
    for fmt in ("pdf", "docx", "txt"):
        assert _export(client, "does-not-exist", fmt).status_code == 404


def test_all_three_exports_succeed_for_every_template(client, payload):
    for template_id in ("nda", "employment-contract", "partnership-agreement"):
        request = dict(payload)
        request["document_type"] = template_id
        document_id = client.post("/api/documents/generate", json=request).json()[
            "document"
        ]["id"]
        for fmt, magic in (("pdf", b"%PDF"), ("docx", b"PK"), ("txt", None)):
            response = _export(client, document_id, fmt)
            assert response.status_code == 200, f"{template_id}/{fmt}"
            if magic:
                assert response.content.startswith(magic), f"{template_id}/{fmt}"


def test_export_never_interprets_content_as_markup(
    client, generated_document
):
    """Injected markup must be escaped in the rendered formats.

    TXT legitimately carries the characters verbatim - it is a plain-text
    download served as ``text/plain``, not HTML.
    """
    document_id = generated_document["id"]
    hostile = "<script>alert('x')</script> & <b>bold</b> 5 < 6 > 4"
    content = client.get(f"/api/documents/{document_id}").json()["content"]
    content["sections"][0]["content"] = hostile
    client.put(f"/api/documents/{document_id}", json={"content": content})

    pdf = _export(client, document_id, "pdf")
    assert pdf.status_code == 200
    assert b"<script>" not in pdf.content
    assert b"alert" not in pdf.content

    docx_response = _export(client, document_id, "docx")
    with zipfile.ZipFile(io.BytesIO(docx_response.content)) as archive:
        document_xml = archive.read("word/document.xml").decode("utf-8")
    assert "&lt;script&gt;" in document_xml
    assert "<script>" not in document_xml

    txt = _export(client, document_id, "txt")
    assert txt.headers["content-type"].startswith("text/plain")
    assert "<script>" in txt.text  # preserved as literal text, as intended
