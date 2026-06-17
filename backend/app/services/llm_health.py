from __future__ import annotations

import logging

import httpx

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


async def check_llm_api_availability() -> dict:
    result = {
        "checked": True,
        "available": False,
        "message": "LLM API check failed",
    }

    if settings.user_llm_only:
        result["available"] = True
        result["message"] = "USER_LLM_ONLY is enabled; server-side LLM is intentionally disabled"
        logger.info("LLM API availability probe skipped: %s", result["message"])
        return result

    if not settings.llm_api_key or not settings.llm_api_base:
        result["message"] = "LLM API is not configured"
        logger.warning("LLM API availability probe skipped: %s", result["message"])
        return result

    models_url = f"{settings.llm_api_base.rstrip('/')}/models"
    headers = {"Authorization": f"Bearer {settings.llm_api_key}"}

    logger.info("Starting LLM API availability probe against %s", models_url)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(models_url, headers=headers)
            response.raise_for_status()

        result["available"] = True
        result["message"] = "LLM API is reachable"
        logger.info("LLM API availability probe succeeded: %s", models_url)
        return result
    except Exception as exc:
        result["message"] = f"LLM API unavailable: {exc}"
        logger.warning("LLM API availability probe failed: %s", exc)
        return result
