"""AI generation behaviour, including failure and malformed-response paths."""

from __future__ import annotations

import copy

import pytest
from pydantic import BaseModel

from app.schemas.ai import GenerateDocumentRequest
from app.utils import errors


# --- Demo mode ---------------------------------------------------------


def test_demo_mode_generates_without_an_api_key(client, payload, monkeypatch):
    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "groq_api_key", None)
    monkeypatch.setattr(settings, "demo_mode", True)

    response = client.post("/api/documents/generate", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["generation_source"] == "demo"
    assert body["model"] == "demo"
    assert body["document"]["content"]["generation"]["source"] == "demo"
    # The user is told the output is not a live model response.
    assert any("Demo" in w for w in body["warnings"])


def test_demo_output_is_deterministic(client, payload, monkeypatch):
    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "groq_api_key", None)
    monkeypatch.setattr(settings, "demo_mode", True)

    first = client.post("/api/documents/generate", json=payload).json()
    second = client.post("/api/documents/generate", json=payload).json()

    def normalise(body: dict) -> list[str]:
        return [
            f"{s['heading']}::{s['content']}"
            for s in body["document"]["content"]["sections"]
        ]

    assert normalise(first) == normalise(second)


def test_demo_output_is_labelled_not_real(client, payload, monkeypatch):
    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "groq_api_key", None)
    monkeypatch.setattr(settings, "demo_mode", True)

    body = client.post("/api/documents/generate", json=payload).json()
    joined = " ".join(s["content"] for s in body["document"]["content"]["sections"])
    assert "DEMO" in joined.upper()


# --- Missing configuration ---------------------------------------------


def test_generate_without_key_or_demo_mode_is_503(client, payload, monkeypatch):
    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "groq_api_key", None)
    monkeypatch.setattr(settings, "demo_mode", False)

    response = client.post("/api/documents/generate", json=payload)
    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "AI_NOT_CONFIGURED"
    assert body["error"]["message"] == (
        "AI configuration is missing. Add GROQ_API_KEY to backend/.env."
    )


def test_app_does_not_crash_without_a_key(client, monkeypatch):
    """The service must stay fully usable; only generation is blocked."""
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "groq_api_key", None)
    monkeypatch.setattr(get_settings(), "demo_mode", False)

    assert client.get("/api/health").status_code == 200
    assert client.get("/api/documents").status_code == 200
    assert client.get("/api/templates").status_code == 200


# --- Section rewriting -------------------------------------------------


def test_rewrite_section_replaces_only_the_target(client, generated_document):
    document_id = generated_document["id"]
    before = generated_document["content"]["sections"]

    response = client.post(
        f"/api/documents/{document_id}/rewrite-section",
        json={"section_index": 1, "action": "simplify"},
    )
    assert response.status_code == 200
    body = response.json()
    after = body["document"]["content"]["sections"]

    assert after[1]["content"] != before[1]["content"]
    assert after[0]["content"] == before[0]["content"]
    assert after[2]["content"] == before[2]["content"]


@pytest.mark.parametrize(
    "action",
    [
        "rewrite_professional",
        "simplify",
        "more_formal",
        "expand",
        "shorten",
        "fix_grammar",
        "add_protection",
    ],
)
def test_every_rewrite_action_is_accepted(client, generated_document, action):
    response = client.post(
        f"/api/documents/{generated_document['id']}/rewrite-section",
        json={"section_index": 0, "action": action},
    )
    assert response.status_code == 200, response.text
    assert response.json()["action"] == action


def test_rewrite_rejects_unknown_action(client, generated_document):
    response = client.post(
        f"/api/documents/{generated_document['id']}/rewrite-section",
        json={"section_index": 0, "action": "make_it_better"},
    )
    assert response.status_code == 422


def test_rewrite_rejects_out_of_range_index(client, generated_document):
    response = client.post(
        f"/api/documents/{generated_document['id']}/rewrite-section",
        json={"section_index": 150, "action": "shorten"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_rewrite_creates_a_version(client, generated_document):
    document_id = generated_document["id"]
    client.post(
        f"/api/documents/{document_id}/rewrite-section",
        json={"section_index": 0, "action": "expand"},
    )
    versions = client.get(f"/api/documents/{document_id}/versions").json()
    assert len(versions) >= 3
    assert any("AI rewrite" in (v["label"] or "") for v in versions)


def test_rewrite_is_reversible(client, generated_document):
    document_id = generated_document["id"]
    original = generated_document["content"]["sections"][1]["content"]

    client.post(
        f"/api/documents/{document_id}/rewrite-section",
        json={"section_index": 1, "action": "shorten"},
    )
    client.post(f"/api/documents/{document_id}/versions/1/restore")
    restored = client.get(f"/api/documents/{document_id}").json()
    assert restored["content"]["sections"][1]["content"] == original


# --- Malformed / failed model responses --------------------------------


def test_malformed_json_becomes_a_clean_502(client, payload, monkeypatch):
    from app.ai import client as ai_client
    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "groq_api_key", "test-key")
    monkeypatch.setattr(settings, "demo_mode", False)

    monkeypatch.setattr(
        ai_client.GroqClient,
        "generate_structured",
        lambda self, **kwargs: ai_client.GroqClient._parse(
            "this is definitely not json {", kwargs["response_model"]
        ),
    )

    response = client.post("/api/documents/generate", json=payload)
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "AI_INVALID_RESPONSE"
    assert "Traceback" not in response.text


def test_schema_mismatch_becomes_a_clean_502(client, payload, monkeypatch):
    from app.ai import client as ai_client
    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "groq_api_key", "test-key")
    monkeypatch.setattr(settings, "demo_mode", False)

    monkeypatch.setattr(
        ai_client.GroqClient,
        "generate_structured",
        lambda self, **kwargs: ai_client.GroqClient._parse(
            '{"unexpected": "shape"}', kwargs["response_model"]
        ),
    )

    response = client.post("/api/documents/generate", json=payload)
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "AI_INVALID_RESPONSE"


def test_fenced_json_is_tolerated():
    from app.ai.client import GroqClient
    from app.schemas.ai import DocumentDraft

    fenced = '```json\n{"title": "Test", "sections": [{"id": "a", "heading": "1. X", "content": "y"}], "signature_blocks": [], "disclaimer": "d"}\n```'
    parsed = GroqClient._parse(fenced, DocumentDraft)
    assert parsed.title == "Test"
    assert parsed.sections[0].heading == "1. X"


@pytest.mark.parametrize(
    "status_code,expected",
    [
        (401, 502),
        (403, 502),
        (429, 429),
        (500, 504),
        (503, 504),
    ],
)
def test_provider_errors_map_to_safe_http_codes(
    client, payload, monkeypatch, status_code, expected
):
    """Provider failures are translated; nothing internal leaks out."""
    import httpx

    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "groq_api_key", "test-key")
    monkeypatch.setattr(settings, "demo_mode", False)

    # Only the network call is faked, so the real status mapping still runs.
    def _fake_post(self, *args, **kwargs):
        return httpx.Response(
            status_code,
            json={"error": {"message": f"provider responded {status_code}"}},
            request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        )

    monkeypatch.setattr(httpx.Client, "post", _fake_post)

    response = client.post("/api/documents/generate", json=payload)
    assert response.status_code == expected, response.text
    body = response.json()
    assert body["error"]["code"] in (
        "AI_AUTH_FAILED",
        "AI_QUOTA_EXCEEDED",
        "AI_TIMEOUT",
        "AI_INVALID_RESPONSE",
    )
    assert "Traceback" not in response.text
    assert "test-key" not in response.text


def test_unknown_model_is_reported_as_a_config_error(client, payload, monkeypatch):
    import httpx

    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "groq_api_key", "test-key")
    monkeypatch.setattr(settings, "groq_model", "not-a-real-model")
    monkeypatch.setattr(settings, "demo_mode", False)

    def _fake_post(self, *args, **kwargs):
        return httpx.Response(
            400,
            json={"error": {"message": "model not found"}},
            request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        )

    monkeypatch.setattr(httpx.Client, "post", _fake_post)

    response = client.post("/api/documents/generate", json=payload)
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "AI_AUTH_FAILED"
    assert "GROQ_MODEL" in response.json()["error"]["message"]


def test_timeout_maps_to_504(client, payload, monkeypatch):
    import httpx

    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "groq_api_key", "test-key")
    monkeypatch.setattr(settings, "demo_mode", False)

    def _fake_post(self, *args, **kwargs):
        raise httpx.ReadTimeout("read timed out")

    monkeypatch.setattr(httpx.Client, "post", _fake_post)

    response = client.post("/api/documents/generate", json=payload)
    assert response.status_code == 504
    assert response.json()["error"]["code"] == "AI_TIMEOUT"


def test_truncated_reply_is_retried_with_a_larger_budget(monkeypatch):
    """A reply cut short by the token budget is retried, not surfaced raw."""
    import httpx

    from app.ai.client import GroqClient
    from app.ai.legal_generator import SectionRevision
    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "groq_api_key", "test-key")
    monkeypatch.setattr(settings, "groq_max_retries", 2)

    budgets: list[int] = []
    replies = [
        ("", "length"),
        ('{"revised_text": "Recovered clause text."}', "stop"),
    ]

    def _fake_post(client, *, model, system_instruction, prompt, schema, temperature, max_tokens):
        budgets.append(max_tokens)
        text, finish = replies.pop(0)
        return {
            "choices": [{"message": {"content": text}, "finish_reason": finish}]
        }

    monkeypatch.setattr(GroqClient, "_post", staticmethod(_fake_post))

    result = GroqClient().generate_structured(
        system_instruction="s",
        prompt="p",
        response_model=SectionRevision,
        max_output_tokens=100,
    )

    assert result.revised_text == "Recovered clause text."
    assert budgets == [100, 200]
    GroqClient().close()


def test_empty_reply_without_a_finish_reason_is_rejected():
    from app.ai.client import GroqClient
    from app.utils.errors import AIInvalidResponseError

    with pytest.raises(AIInvalidResponseError):
        GroqClient._extract({"choices": []})


def test_block_style_content_is_joined():
    """Some providers return content blocks instead of a plain string."""
    from app.ai.client import GroqClient

    text, truncated = GroqClient._extract(
        {
            "choices": [
                {
                    "message": {
                        "content": [
                            {"type": "text", "text": "part one "},
                            {"type": "text", "text": "part two"},
                        ]
                    },
                    "finish_reason": "stop",
                }
            ]
        }
    )
    assert text == "part one part two"
    assert truncated is False


# --- Schema normalisation -------------------------------------------------


def _assert_strict(schema: dict, path: str = "root") -> None:
    """Every object must be closed and list all of its keys as required."""
    if isinstance(schema, dict):
        properties = schema.get("properties")
        if schema.get("type") == "object" and isinstance(properties, dict):
            assert schema.get("additionalProperties") is False, path
            assert schema.get("required") == list(properties.keys()), path
        for key, value in schema.items():
            _assert_strict(value, f"{path}.{key}")
    elif isinstance(schema, list):
        for index, value in enumerate(schema):
            _assert_strict(value, f"{path}[{index}]")


def test_normalized_schema_is_accepted_by_strict_decoders():
    """The real draft schema must satisfy every strict-mode constraint."""
    import json

    from app.ai.client import normalize_json_schema
    from app.schemas.ai import DocumentDraft

    normalized = normalize_json_schema(DocumentDraft.model_json_schema())

    # References are inlined, so no provider-specific $defs support is needed.
    dumped = json.dumps(normalized)
    assert "$ref" not in dumped
    assert "$defs" not in dumped

    _assert_strict(normalized)


def test_normalized_rewrite_schema_is_also_strict():
    from app.ai.client import normalize_json_schema
    from app.ai.legal_generator import SectionRevision

    _assert_strict(normalize_json_schema(SectionRevision.model_json_schema()))


def test_normalization_preserves_nullability_of_optional_fields():
    """Optionality survives by keeping Pydantic's nullable unions."""
    import json

    from app.ai.client import normalize_json_schema
    from app.schemas.ai import DocumentDraft

    dumped = json.dumps(normalize_json_schema(DocumentDraft.model_json_schema()))
    assert '"anyOf"' in dumped
    assert '"type": "null"' in dumped


def test_normalization_tolerates_a_self_referential_schema():
    from app.ai.client import normalize_json_schema

    class Node(BaseModel):
        name: str
        child: "Node | None" = None

    Node.model_rebuild()
    # Must terminate rather than recurse forever.
    _assert_strict(normalize_json_schema(Node.model_json_schema()))


def test_normalization_drops_default_metadata():
    import json

    from app.ai.client import normalize_json_schema
    from app.schemas.ai import DocumentDraft

    dumped = json.dumps(normalize_json_schema(DocumentDraft.model_json_schema()))
    assert '"default"' not in dumped



def test_non_configured_error_class_defaults():
    error = errors.AINotConfiguredError()
    assert error.status_code == 503
    assert error.code == "AI_NOT_CONFIGURED"
    assert "GROQ_API_KEY" in error.message


def test_custom_document_type_falls_back_to_generic_template(client, payload):
    custom = copy.deepcopy(payload)
    custom["document_type"] = "custom"
    response = client.post("/api/documents/generate", json=custom)
    assert response.status_code == 201
    assert response.json()["document"]["document_type"] == "custom"


# --- Optional fields ------------------------------------------------------


def test_optional_date_fields_are_omitted_cleanly(payload):
    """A request without dates must not raise, in any AI mode."""
    from app.ai.prompts import build_generation_prompt

    payload.pop("effective_date", None)
    payload.pop("expiry_date", None)
    request = GenerateDocumentRequest.model_validate(payload)

    prompt = build_generation_prompt(
        document_type_title="NDA",
        document_type_description="Confidentiality terms.",
        suggested_sections=["Confidential Information"],
        request=request,
    )
    assert "not supplied" in prompt


def test_generate_without_dates_succeeds_in_demo_mode(client, payload, monkeypatch):
    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "groq_api_key", None)
    monkeypatch.setattr(settings, "demo_mode", True)

    payload.pop("effective_date", None)
    payload.pop("expiry_date", None)

    response = client.post("/api/documents/generate", json=payload)
    assert response.status_code == 201, response.text
    assert response.json()["generation_source"] == "demo"


