"""User-supplied LLM test endpoints.

These endpoints let the frontend verify a user-supplied LLM credential
*before* persisting it in localStorage and using it for real requests.

Three endpoints:

- ``POST /user/llm/test-key``   — verify ``api_key`` + ``base_url`` by
  calling the upstream's ``/v1/models`` listing.
- ``POST /user/llm/test-vision`` — verify the chosen *model* supports
  multimodal input by uploading a tiny test image and asking the model
  to describe it.
- ``GET  /user/llm/models``      — return the upstream's model list so
  the frontend can populate a dropdown.

The user-supplied credentials are passed through these endpoints only for
the duration of the request; they are never written to disk or logs.
"""

from __future__ import annotations

import base64
import io
import logging
import re

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from PIL import Image

from app.core.user_llm import is_http_url_safe
from app.models.schemas import (
    ListModelsResponse,
    TestKeyRequest,
    TestKeyResponse,
    TestVisionResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user/llm", tags=["user_llm"])


# ------------------------------------------------------------------
# POST /user/llm/test-key
# ------------------------------------------------------------------
@router.post("/test-key", response_model=TestKeyResponse)
async def test_key(body: TestKeyRequest):
    """Verify a user-supplied API key by listing models on the upstream."""
    api_key = body.api_key.strip()
    base_url = body.base_url.strip().rstrip("/")
    if not is_http_url_safe(base_url):
        raise HTTPException(
            status_code=400,
            detail="base_url must be an https:// or http://localhost URL",
        )
    models_url = f"{base_url}/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    logger.info("User LLM test-key: probing %s", models_url)
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(models_url, headers=headers)
        if response.status_code == 401 or response.status_code == 403:
            return TestKeyResponse(
                available=False,
                message=f"Authentication failed (HTTP {response.status_code})",
            )
        response.raise_for_status()
        data = response.json()
        # OpenAI-style: {"data": [{"id": "..."}, ...]}
        models: list[str] = []
        if isinstance(data, dict) and isinstance(data.get("data"), list):
            for entry in data["data"]:
                if isinstance(entry, dict) and entry.get("id"):
                    models.append(str(entry["id"]))
        elif isinstance(data, list):
            # Some proxies return a bare list
            for entry in data:
                if isinstance(entry, dict) and entry.get("id"):
                    models.append(str(entry["id"]))
                elif isinstance(entry, str):
                    models.append(entry)
        return TestKeyResponse(
            available=True,
            model_count=len(models),
            models_sample=models[:20],
            message=f"OK — {len(models)} models",
        )
    except httpx.HTTPStatusError as exc:
        return TestKeyResponse(
            available=False,
            message=f"Upstream returned HTTP {exc.response.status_code}",
        )
    except Exception as exc:
        logger.warning("User LLM test-key failed: %s", exc)
        return TestKeyResponse(
            available=False,
            message=f"Connection error: {exc}",
        )


# ------------------------------------------------------------------
# POST /user/llm/models
# ------------------------------------------------------------------
@router.post("/models", response_model=ListModelsResponse)
async def list_models(body: TestKeyRequest):
    """Return the upstream model list for the dropdown.

    Note: this is a POST (not GET) so the API key travels in the
    request body, not the URL. GET with query parameters would log
    the key in uvicorn's access log.
    """
    api_key = body.api_key.strip()
    base_url = body.base_url.strip().rstrip("/")
    if not is_http_url_safe(base_url):
        raise HTTPException(
            status_code=400,
            detail="base_url must be an https:// or http://localhost URL",
        )
    models_url = f"{base_url}/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(models_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        models: list[str] = []
        if isinstance(data, dict) and isinstance(data.get("data"), list):
            for entry in data["data"]:
                if isinstance(entry, dict) and entry.get("id"):
                    models.append(str(entry["id"]))
        elif isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict) and entry.get("id"):
                    models.append(str(entry["id"]))
                elif isinstance(entry, str):
                    models.append(entry)
        return ListModelsResponse(available=True, models=models, message="OK")
    except Exception as exc:
        logger.warning("list_models failed: %s", exc)
        return ListModelsResponse(available=False, models=[], message=str(exc))


# ------------------------------------------------------------------
# POST /user/llm/test-vision
# ------------------------------------------------------------------
_VISION_PROMPT = (
    "Reply with exactly one word: 'ok'. Do not add punctuation or explanation."
)


@router.post("/test-vision", response_model=TestVisionResponse)
async def test_vision(
    api_key: str = Form(...),
    base_url: str = Form(...),
    model: str = Form(...),
    image: UploadFile = File(...),
):
    """Verify the chosen model supports multimodal input by asking it to
    describe a tiny test image. The test image is generated server-side
    if the upload is too large, but in practice the frontend sends a
    1x1 (or 32x32) PNG."""
    api_key = api_key.strip()
    base_url = base_url.strip().rstrip("/")
    model = model.strip()
    if not is_http_url_safe(base_url):
        raise HTTPException(
            status_code=400,
            detail="base_url must be an https:// or http://localhost URL",
        )
    if not model:
        raise HTTPException(status_code=400, detail="model is required")

    # Read + normalize the uploaded image: cap size, ensure valid format
    raw = await image.read()
    if len(raw) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 5MB)")
    try:
        img = Image.open(io.BytesIO(raw))
        # Resize to 32x32 to keep the test small and fast
        img = img.convert("RGB").resize((32, 32))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        normalized_bytes = buf.getvalue()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid image: {exc}")

    base64_image = base64.b64encode(normalized_bytes).decode("ascii")
    chat_url = f"{base_url}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _VISION_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                ],
            }
        ],
        "max_tokens": 16,
        "temperature": 0,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    logger.info(
        "User LLM test-vision: probing %s model=%s image_bytes=%s",
        chat_url, model, len(normalized_bytes),
    )
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(chat_url, json=payload, headers=headers)
        if response.status_code == 401 or response.status_code == 403:
            return TestVisionResponse(
                multimodal_ok=False,
                error=f"Authentication failed (HTTP {response.status_code})",
            )
        if response.status_code == 404:
            return TestVisionResponse(
                multimodal_ok=False,
                error=f"Model or endpoint not found (HTTP 404). Check the model name.",
            )
        response.raise_for_status()
        data = response.json()
        text = ""
        try:
            text = str(data["choices"][0]["message"]["content"] or "").strip()
        except (KeyError, IndexError, TypeError):
            text = ""
        # A successful response (any text or even empty content) means the
        # model accepted multimodal input. An explicit refusal / safety
        # block is still considered a working multimodal channel.
        return TestVisionResponse(
            multimodal_ok=True,
            response_text=text[:200],
        )
    except httpx.HTTPStatusError as exc:
        body = exc.response.text[:500] if exc.response else ""
        return TestVisionResponse(
            multimodal_ok=False,
            error=f"HTTP {exc.response.status_code}: {body}",
        )
    except Exception as exc:
        logger.warning("User LLM test-vision failed: %s", exc)
        return TestVisionResponse(
            multimodal_ok=False,
            error=f"Connection error: {exc}",
        )
