"""Branding profiles, logo upload validation and path-traversal defences."""

from __future__ import annotations

import io

from app.config import settings
from app.utils.security import safe_download_filename, sniff_image_type


# --- Profiles ----------------------------------------------------------


def test_create_and_list_brand_profile(client):
    created = client.post(
        "/api/branding",
        json={
            "organization_name": "Northwind Analytics",
            "address": "42 Brigade Road, Chennai",
            "email": "legal@northwind.example",
            "phone": "+91 44 4000 1234",
            "website": "www.northwind.example",
            "footer_text": "Northwind Analytics - Confidential",
        },
    )
    assert created.status_code == 201
    assert created.json()["organization_name"] == "Northwind Analytics"

    listed = client.get("/api/branding").json()
    assert listed["total"] >= 1
    assert listed["items"][0]["footer_text"].endswith("Confidential")


def test_second_post_updates_rather_than_duplicating(client):
    first = client.post("/api/branding", json={"organization_name": "A"}).json()
    second = client.post("/api/branding", json={"organization_name": "B"}).json()
    assert first["id"] == second["id"]
    assert second["organization_name"] == "B"

    profiles = client.get("/api/branding").json()
    # The id is reused and appears exactly once.
    assert [p["id"] for p in profiles["items"]].count(first["id"]) == 1


def test_update_by_unknown_id_is_404(client):
    response = client.post(
        "/api/branding", json={"id": "nope", "organization_name": "X"}
    )
    assert response.status_code == 404


# --- Logo upload -------------------------------------------------------


def test_upload_valid_png(client, png_bytes):
    response = client.post(
        "/api/branding/logo",
        files={"file": ("logo.png", io.BytesIO(png_bytes), "image/png")},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["content_type"] == "image/png"
    assert body["logo_path"].endswith(".png")
    # The stored name is generated, never the uploaded one.
    assert "logo" not in body["logo_path"].replace(".png", "")


def test_upload_valid_jpeg_is_accepted(client):
    jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 64
    response = client.post(
        "/api/branding/logo",
        files={"file": ("brand.jpg", io.BytesIO(jpeg), "image/jpeg")},
    )
    assert response.status_code == 201
    assert response.json()["content_type"] == "image/jpeg"


def test_uploaded_logo_is_served(client, png_bytes):
    upload = client.post(
        "/api/branding/logo",
        files={"file": ("logo.png", io.BytesIO(png_bytes), "image/png")},
    ).json()

    response = client.get(upload["logo_url"])
    assert response.status_code == 200
    assert response.content.startswith(b"\x89PNG")
    assert response.headers["content-type"] == "image/png"


def test_rejects_non_image_bytes(client):
    response = client.post(
        "/api/branding/logo",
        files={"file": ("evil.png", io.BytesIO(b"<html>not an image</html>"), "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "UPLOAD_REJECTED"


def test_rejects_pdf_disguised_as_png(client):
    response = client.post(
        "/api/branding/logo",
        files={"file": ("x.png", io.BytesIO(b"%PDF-1.7\nmalicious"), "image/png")},
    )
    assert response.status_code == 400


def test_rejects_content_type_mismatch(client, png_bytes):
    response = client.post(
        "/api/branding/logo",
        files={"file": ("x.jpg", io.BytesIO(png_bytes), "image/jpeg")},
    )
    assert response.status_code == 400


def test_rejects_empty_file(client):
    response = client.post(
        "/api/branding/logo",
        files={"file": ("empty.png", io.BytesIO(b""), "image/png")},
    )
    assert response.status_code == 400


def test_rejects_oversized_file(client):
    oversized = b"\x89PNG\r\n\x1a\n" + b"\x00" * (settings.max_logo_bytes + 1024)
    response = client.post(
        "/api/branding/logo",
        files={"file": ("big.png", io.BytesIO(oversized), "image/png")},
    )
    assert response.status_code == 400
    assert "smaller than" in response.json()["error"]["message"]


def test_traversal_filename_is_not_used_on_disk(client, png_bytes):
    """A traversal filename must still be stored under a generated name."""
    response = client.post(
        "/api/branding/logo",
        files={
            "file": (
                "../../../../etc/passwd.png",
                io.BytesIO(png_bytes),
                "image/png",
            )
        },
    )
    assert response.status_code == 201
    stored = response.json()["logo_path"]
    assert "/" not in stored
    assert ".." not in stored


# --- Path traversal ----------------------------------------------------


def test_logo_route_rejects_traversal(client):
    for attempt in (
        "../../../etc/passwd",
        "..%2F..%2Fetc%2Fpasswd",
        "....//....//etc/passwd",
    ):
        response = client.get(f"/api/branding/logo/{attempt}")
        assert response.status_code in (400, 404), attempt
        assert b"root:" not in response.content


def test_logo_route_rejects_unknown_file(client):
    assert client.get("/api/branding/logo/does-not-exist.png").status_code == 400


def test_build_logo_filename_rejects_escapes():
    from app.utils.security import build_logo_filename

    with_escape = "../../secrets.png"
    try:
        build_logo_filename(with_escape)
    except Exception as exc:  # noqa: BLE001
        assert exc.__class__.__name__ == "UploadError"
    else:
        # If it resolves, it must stay inside the logo directory.
        import os

        assert os.path.commonpath(
            [os.path.abspath(build_logo_filename(with_escape)), os.path.abspath(settings.logo_dir)]
        ) == os.path.abspath(settings.logo_dir)


# --- Filename sanitising -----------------------------------------------


def test_safe_download_filename_strips_traversal():
    assert "/" not in safe_download_filename("../../../etc/passwd", ".pdf")
    assert ".." not in safe_download_filename("../../../etc/passwd", ".pdf")


def test_safe_download_filename_is_ascii():
    result = safe_download_filename("Ünïcödé 契約 Agreement", ".docx")
    assert result.isascii()
    assert result.endswith(".docx")


def test_safe_download_filename_falls_back():
    assert safe_download_filename("///", ".txt").endswith(".txt")
    assert safe_download_filename("", ".txt") == "document.txt"


def test_safe_download_filename_is_length_bounded():
    result = safe_download_filename("A" * 500, ".pdf")
    assert len(result) <= 90


# --- Magic byte sniffing -----------------------------------------------


def test_sniff_image_type():
    assert sniff_image_type(b"\x89PNG\r\n\x1a\nrest") == "image/png"
    assert sniff_image_type(b"\xff\xd8\xff\xe0rest") == "image/jpeg"
    assert sniff_image_type(b"GIF89a") is None
    assert sniff_image_type(b"") is None
