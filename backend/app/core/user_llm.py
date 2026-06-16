"""User-supplied LLM configuration.

This module lets a user bring their own OpenAI-compatible LLM (base_url +
api_key + model) via HTTP headers on each request. The user's key is
*never* persisted server-side: it lives only on the user's device
(frontend localStorage) and is transmitted per-request, used in request
scope, then discarded.

Header contract (all optional):

    X-User-LLM-Key:   sk-...
    X-User-LLM-Base:  https://api.example.com/v1
    X-User-LLM-Model: gpt-4o-mini

If all three are present *and* a sentinel ``X-User-LLM-Enabled: 1`` is
set, the user-supplied config takes precedence over the server's
.env-configured LLM for the duration of the request.

Why a separate "enabled" header?
    We don't want a request that *happens* to forward some other
    ``X-User-LLM-*`` header (e.g. a misconfigured proxy) to silently
    override the backend LLM. The enabled flag is an explicit opt-in.
"""

from __future__ import annotations

import contextlib
import logging
from dataclasses import dataclass
from typing import Iterator, Optional

from fastapi import Request

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


@dataclass
class UserLLMConfig:
    """User-supplied LLM credentials. Treat as sensitive — never log the key."""
    api_key: str
    base_url: str
    model: str
    enabled: bool = True

    def is_usable(self) -> bool:
        return bool(
            self.enabled
            and self.api_key.strip()
            and self.base_url.strip()
            and self.model.strip()
        )


def parse_user_llm_headers(request: Request) -> Optional[UserLLMConfig]:
    """Extract user-LLM config from request headers. Returns None if disabled or incomplete."""
    headers = request.headers
    enabled = headers.get("X-User-LLM-Enabled", "").strip().lower() in ("1", "true", "yes")
    if not enabled:
        return None
    api_key = headers.get("X-User-LLM-Key", "").strip()
    base_url = headers.get("X-User-LLM-Base", "").strip()
    model = headers.get("X-User-LLM-Model", "").strip()
    if not (api_key and base_url and model):
        return None
    # Normalize base_url: strip trailing slashes
    base_url = base_url.rstrip("/")
    return UserLLMConfig(api_key=api_key, base_url=base_url, model=model, enabled=True)


@contextlib.contextmanager
def apply_user_llm(config: Optional[UserLLMConfig]) -> Iterator[None]:
    """Temporarily override the global settings with a user-supplied LLM config.

    The original values are restored on context exit, so concurrent requests
    using the same process do not pollute each other's LLM credentials.

    WARNING: the keys in the config are *not* logged. We only log the base_url
    and model so operators can confirm which endpoint was used.
    """
    if config is None or not config.is_usable():
        yield
        return

    settings: Settings = get_settings()
    original_key = settings.llm_api_key
    original_base = settings.llm_api_base
    original_model = settings.llm_model
    settings.llm_api_key = config.api_key
    settings.llm_api_base = config.base_url
    settings.llm_model = config.model
    logger.info(
        "Applying user-supplied LLM for request: base_url=%s model=%s",
        config.base_url,
        config.model,
    )
    try:
        yield
    finally:
        settings.llm_api_key = original_key
        settings.llm_api_base = original_base
        settings.llm_model = original_model
        logger.debug("Restored server-default LLM after request")


def is_http_url_safe(url: str) -> bool:
    """Allow only http(s) URLs to known-safe hosts.

    Accepts:
    - https://*
    - http://localhost* or http://127.0.0.1* (loopback)
    - http://<ipv4>:*  (any IPv4 address — covers LAN setups that
      aren't strictly RFC 1918)
    - http://10.* / http://192.168.* / http://172.16-31.* / http://169.254.*
      (RFC 1918 + link-local) — fast-path so common LAN setups don't
      hit the IP-parsing branch above

    Rejects http://<public-dns-hostname> to discourage accidentally
    forwarding user keys to arbitrary third-party hosts.
    """
    lowered = url.lower()
    if lowered.startswith("https://"):
        return True
    if not lowered.startswith("http://"):
        return False
    # Strip the scheme for host checks
    rest = lowered[len("http://"):]
    host = rest.split("/", 1)[0].split(":", 1)[0]
    # Loopback
    if host in ("localhost", "127.0.0.1", "::1"):
        return True
    # Any IPv4 address (covers LANs and private networks)
    parts = host.split(".")
    if len(parts) == 4:
        try:
            octets = [int(p) for p in parts]
        except ValueError:
            return False
        if all(0 <= o <= 255 for o in octets):
            return True
    return False
