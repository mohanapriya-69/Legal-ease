"""Thin, defensive HTTP client for Groq's OpenAI-compatible chat API.

Groq is called over plain ``httpx`` rather than the vendor SDK: the endpoint is
stable, it keeps the dependency surface small, and it means the application
still boots and serves every read-only route when no API key is configured.

Every failure mode is translated into a typed :class:`AppError` subclass, so an
HTTP status from the provider never reaches the client verbatim.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from app.config import settings
from app.utils.errors import (
    AIAuthError,
    AINotConfiguredError,
    AIQuotaError,
    AITimeoutError,
    AIInvalidResponseError,
)

logger = logging.getLogger("legalease.ai")

_JSON_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)

# Keywords that carry no meaning for a constrained decoder and are rejected or
# ignored by strict structured-output implementations.
_SCHEMA_NOISE = frozenset({"default", "$comment", "examples", "discriminator"})


def normalize_json_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Adapt a Pydantic JSON schema to what strict structured outputs require.

    Pydantic emits ``$defs`` + ``$ref``, omits ``additionalProperties``, and
    lists only genuinely required keys in ``required``. A strict decoder wants
    all three done its way: every reference inlined, every object closed, and
    every property listed as required. Optionality is preserved by keeping the
    ``anyOf: [..., null]`` unions Pydantic already generates, so a nullable
    field can still be absent in meaning while being present in the payload.
    """
    defs = schema.get("$defs", {}) or {}

    def resolve(node: Any, seen: frozenset[str]) -> Any:
        if isinstance(node, list):
            return [resolve(item, seen) for item in node]
        if not isinstance(node, dict):
            return node

        # Inline a reference, guarding against a self-referential cycle.
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/$defs/"):
            name = ref.split("/")[-1]
            if name in seen or name not in defs:
                return {"type": "object"}
            return resolve(defs[name], seen | {name})

        out: dict[str, Any] = {}
        for key, value in node.items():
            if key in _SCHEMA_NOISE or key == "$defs":
                continue
            out[key] = resolve(value, seen)

        properties = out.get("properties")
        if out.get("type") == "object" and isinstance(properties, dict):
            # Close the object, and require every declared key.
            out["additionalProperties"] = False
            out["required"] = list(properties.keys())
        return out

    normalized = resolve({k: v for k, v in schema.items() if k != "$defs"}, frozenset())
    if normalized.get("type") == "object":
        normalized["additionalProperties"] = False
        if isinstance(normalized.get("properties"), dict):
            normalized["required"] = list(normalized["properties"].keys())
    return normalized


class GroqClient:
    """Structured-JSON text generation against Groq."""

    def __init__(self) -> None:
        self._client: httpx.Client | None = None

    # -- lifecycle ----------------------------------------------------

    def _ensure_client(self) -> httpx.Client:
        if not settings.ai_configured:
            raise AINotConfiguredError()

        if self._client is not None:
            return self._client

        # The model name always comes from configuration, never a literal here.
        self._client = httpx.Client(
            base_url=settings.groq_base_url,
            timeout=httpx.Timeout(settings.groq_timeout_seconds),
            headers={
                "Authorization": f"Bearer {settings.groq_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        logger.info("Groq client initialised (model=%s)", settings.groq_model)
        return self._client

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:  # pragma: no cover - best effort
                pass
            self._client = None

    # -- generation ---------------------------------------------------

    def generate_structured(
        self,
        *,
        system_instruction: str,
        prompt: str,
        response_model: type[BaseModel],
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> BaseModel:
        """Call Groq and return the reply parsed as ``response_model``.

        A reply cut short by the token budget is the most common recoverable
        failure, so it is retried once with a larger budget before giving up.
        """
        client = self._ensure_client()
        model = settings.groq_model
        budget = max_output_tokens or settings.groq_max_tokens
        attempts = max(1, settings.groq_max_retries)

        raw_text = ""
        for attempt in range(attempts):
            try:
                payload = self._post(
                    client,
                    model=model,
                    system_instruction=system_instruction,
                    prompt=prompt,
                    schema=response_model.model_json_schema(),                    temperature=(
                        settings.groq_temperature if temperature is None else temperature
                    ),
                    max_tokens=budget,
                )
            except httpx.HTTPError as exc:
                self._raise_mapped_error(exc)
                raise  # pragma: no cover - _raise_mapped_error always raises

            raw_text, truncated = self._extract(payload)

            if raw_text and not truncated:
                break

            if truncated and attempt < attempts - 1:
                logger.warning(
                    "Groq reply truncated at %s tokens; retrying with a larger budget",
                    budget,
                )
                budget = min(budget * 2, 32768)
                continue
            break

        return self._parse(raw_text, response_model)

    # -- transport ----------------------------------------------------

    @staticmethod
    def _post(
        client: httpx.Client,
        *,
        model: str,
        system_instruction: str,
        prompt: str,
        schema: dict[str, Any],
        temperature: float,
        max_tokens: int,
    ) -> dict[str, Any]:
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            # Structured outputs: the model is constrained to this schema, so
            # the reply is parseable by construction rather than by luck.
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema.get("title") or "Response",
                    "strict": True,
                    "schema": normalize_json_schema(schema),
                },
            },
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = client.post("/chat/completions", json=body)
        return GroqClient._handle_response(response)

    @staticmethod
    def _handle_response(response: httpx.Response) -> dict[str, Any]:
        if response.status_code >= 400:
            GroqClient._raise_for_status(response)
        try:
            data = response.json()
        except ValueError as exc:
            logger.error("Groq returned a non-JSON body: %.200s", response.text)
            raise AIInvalidResponseError(
                "The AI service returned an unreadable response. Please try again."
            ) from exc
        if not isinstance(data, dict):
            raise AIInvalidResponseError(
                "The AI service returned an unexpected response shape. Please try again."
            )
        return data

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        """Translate a provider HTTP status into a typed, client-safe error."""
        status = response.status_code
        detail = f"{status} {response.text}".lower()
        logger.warning("Groq call failed (status=%s) %s", status, detail[:400])

        if status in (401, 403):
            raise AIAuthError(
                "The AI service rejected the configured API key. Check GROQ_API_KEY "
                "in backend/.env."
            )
        if status == 429:
            raise AIQuotaError()
        if status in (408, 504):
            raise AITimeoutError()
        if status >= 500:
            raise AITimeoutError(
                "The AI service is temporarily unavailable. Please try again shortly."
            )
        if status == 400 and ("model" in detail or "json_schema" in detail):
            # A bad model name or an unsupported schema is a configuration
            # problem, not a transient failure, so say so plainly.
            raise AIAuthError(
                f"The AI service rejected the request (model={settings.groq_model}). "
                "Check GROQ_MODEL in backend/.env."
            )
        raise AIInvalidResponseError(
            "The AI service could not complete the request. Please try again."
        )

    @staticmethod
    def _raise_mapped_error(exc: Exception) -> None:
        """Translate a transport-level failure into a typed error."""
        detail = f"{type(exc).__name__}: {exc}".lower()
        logger.warning("Groq transport failure: %s", detail[:400])
        raise AITimeoutError() from exc

    # -- response handling --------------------------------------------

    @staticmethod
    def _extract(payload: dict[str, Any]) -> tuple[str, bool]:
        """Return ``(text, truncated)`` from an OpenAI-shaped completion."""
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise AIInvalidResponseError(
                "The AI service returned an empty response. Please try again."
            )

        choice = choices[0] or {}
        message = choice.get("message") or {}
        content = message.get("content")

        # Some providers return a list of content blocks instead of a string.
        if isinstance(content, list):
            content = "".join(
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and block.get("text")
            )

        text = content.strip() if isinstance(content, str) else ""
        finish_reason = str(choice.get("finish_reason") or "")
        truncated = finish_reason.upper() in {"LENGTH", "MAX_TOKENS", "MAX_OUTPUT_TOKENS"}

        if not text and not truncated:
            raise AIInvalidResponseError(
                "The AI service returned an empty response. Please try again."
            )
        return text, truncated

    @staticmethod
    def _parse(raw_text: str, response_model: type[BaseModel]) -> BaseModel:
        cleaned = GroqClient._strip_fences(raw_text)
        if not cleaned:
            raise AIInvalidResponseError(
                "The AI service returned an empty response. Please try again."
            )

        try:
            payload = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error("AI returned non-JSON payload: %.200s", cleaned)
            raise AIInvalidResponseError(
                "The AI service returned an unreadable response. Please try again."
            ) from exc

        if not isinstance(payload, dict):
            raise AIInvalidResponseError(
                "The AI service returned an unexpected response shape. Please try again."
            )

        try:
            return response_model.model_validate(payload)
        except ValidationError as exc:
            missing = sorted({".".join(str(p) for p in e["loc"]) for e in exc.errors()})
            logger.error("AI response failed schema validation: %s", missing)
            raise AIInvalidResponseError(
                "The AI response did not match the expected document structure. "
                "Please try again."
            ) from exc

    @staticmethod
    def _strip_fences(text: str) -> str:
        match = _JSON_FENCE.search(text)
        if match:
            return match.group(1).strip()
        return text.strip()


_client: GroqClient | None = None


def get_ai_client() -> GroqClient:
    global _client
    if _client is None:
        _client = GroqClient()
    return _client
