import io
import base64
import json
import logging
import re
import time
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageOps

from app.core.config import get_settings

if TYPE_CHECKING:
    from app.core.user_llm import UserLLMConfig

# Anchor the storage path to the location of THIS source file, not the process
# CWD. The Docker image runs with CWD=/app but the code lives in
# /app/backend/app/..., so a relative path like "app/static/garments" would
# resolve to /app/app/static/garments (one level too high) and the uploaded
# files would never be reachable by the StaticFiles mount.
_APP_DIR = Path(__file__).resolve().parent.parent  # /app/backend/app
GARMENT_DIR = _APP_DIR / "static" / "garments"
settings = get_settings()
logger = logging.getLogger(__name__)


def _vision_api_key() -> str:
    if settings.user_llm_only:
        return ""
    return settings.vision_api_key or settings.llm_api_key


def _vision_api_base() -> str:
    if settings.user_llm_only:
        return ""
    return settings.vision_api_base or settings.llm_api_base


def _vision_model() -> str:
    if settings.user_llm_only:
        return ""
    return settings.vision_model or settings.llm_model


class VisionService:
    """Handles garment image ingestion: background removal and persistence."""

    def __init__(self):
        GARMENT_DIR.mkdir(parents=True, exist_ok=True)

    async def process_image(self, content: bytes, filename: str | None = None) -> dict:
        """Convert the upload to a single webp file and optionally remove its background."""
        started_at = time.perf_counter()
        original_name = Path(filename or "unknown").stem
        # Sanitize the stem so URL-unsafe / filesystem-unsafe characters
        # (notably '!' from Huawei Cloud OBS thumbnail directives like
        # '008.jpg!list1x.webp') don't leak into the stored filename.
        safe_stem = self._sanitize_stem(original_name)
        stored_name = f"{safe_stem}-{uuid.uuid4().hex[:8]}.webp"
        stored_path = GARMENT_DIR / stored_name
        logger.info(
            "Vision image ingestion started: filename=%s size_bytes=%s target=%s",
            original_name,
            len(content),
            stored_path,
        )

        image = Image.open(io.BytesIO(content))
        image = self._prepare_image(image)

        # Import rembg lazily so backend startup is not blocked by optional runtime deps.
        remove_fn = None
        try:
            from rembg import remove as remove_fn
        except BaseException:
            remove_fn = None

        bg_removed = False
        if remove_fn is not None:
            removed = remove_fn(image)
            image = self._coerce_image(removed)
            bg_removed = True
            logger.info("Background removal completed for %s", original_name)
        else:
            logger.warning("Background removal skipped for %s because rembg is unavailable", original_name)

        image = self._ensure_webp_mode(image)
        image.save(stored_path, format="WEBP", quality=82, method=6, optimize=True)

        logger.info(
            "Vision image ingestion finished: filename=%s stored_path=%s public_url=%s bg_removed=%s elapsed_ms=%.2f",
            original_name,
            stored_path,
            f"/static/garments/{stored_name}",
            bg_removed,
            (time.perf_counter() - started_at) * 1000,
        )

        return {
            "stored_path": str(stored_path),
            "public_url": f"/static/garments/{stored_name}",
            "format": "webp",
            "bg_removed": bg_removed,
            "original_name": original_name,
        }

    def _coerce_image(self, value: bytes | Image.Image) -> Image.Image:
        if isinstance(value, Image.Image):
            value.load()
            return value

        if isinstance(value, (bytes, bytearray)):
            image = Image.open(io.BytesIO(value))
            image.load()
            return image

        raise TypeError(f"Unsupported image type: {type(value)!r}")

    @staticmethod
    def _sanitize_stem(stem: str) -> str:
        """Make a stem safe to use as a static-file name.

        Strips Huawei Cloud / Aliyun OSS thumbnail transform suffixes
        (e.g. ``!list1x``) and replaces any character that is not
        [A-Za-z0-9_-] with '_'. Also caps the length to keep URLs short.
        """
        # Drop the first '!' and everything after it — that's the
        # CDN thumbnail transform directive we don't need on disk.
        if "!" in stem:
            stem = stem.split("!", 1)[0]
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", stem).strip("_")
        if not safe:
            safe = "garment"
        return safe[:48]

    def _prepare_image(self, image: Image.Image) -> Image.Image:
        image = ImageOps.exif_transpose(image)
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
        return image

    def _ensure_webp_mode(self, image: Image.Image) -> Image.Image:
        if image.mode not in ("RGB", "RGBA"):
            return image.convert("RGBA" if "A" in image.getbands() else "RGB")
        return image

    async def analyze_garment(
        self,
        image_bytes: bytes,
        user_llm: "UserLLMConfig | None" = None,
    ) -> dict:
        """Analyze if image contains a garment using multimodal LLM."""
        started_at = time.perf_counter()
        logger.info("Vision garment analysis started: size_bytes=%s", len(image_bytes))
        if not self._can_use_vision(user_llm=user_llm):
            logger.warning("Vision garment analysis skipped because vision config is unavailable")
            return {
                "contains_garment": False,
                "confidence": 0.0,
                "description": "AI service unavailable",
            }

        try:
            from openai import AsyncOpenAI
            if user_llm is not None and user_llm.is_usable():
                client = AsyncOpenAI(
                    api_key=user_llm.api_key,
                    base_url=user_llm.base_url,
                )
                model_name = user_llm.model
                logger.debug(
                    "Vision using user-supplied LLM: base_url=%s model=%s",
                    user_llm.base_url, user_llm.model,
                )
            else:
                client = AsyncOpenAI(
                    api_key=_vision_api_key(),
                    base_url=_vision_api_base(),
                )
                model_name = _vision_model()
                logger.debug(
                    "Vision using server vision LLM: base_url=%s model=%s",
                    _vision_api_base(), model_name,
                )

            base64_image = base64.b64encode(image_bytes).decode("utf-8")

            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "You are a garment detection assistant. "
                                    "Analyze this image and determine if it contains a garment (clothing item). "
                                    "Respond with ONLY a JSON object with this exact format, no markdown or extra text: "
                                    '{"contains_garment": true/false, "confidence": 0.0-1.0, "description": "brief description of the garment if present"}'
                                ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                            },
                        ],
                    }
                ],
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
            )

            import json
            result_text = response.choices[0].message.content.strip()
            logger.debug("Vision garment analysis raw response: %s", result_text)
            result = self._parse_json_result(result_text)
            logger.info(
                "Vision garment analysis parsed result: contains_garment=%s confidence=%s elapsed_ms=%.2f",
                result.get("contains_garment", False),
                result.get("confidence", 0.0),
                (time.perf_counter() - started_at) * 1000,
            )
            return {
                "contains_garment": result.get("contains_garment", False),
                "confidence": float(result.get("confidence", 0.0)),
                "description": result.get("description", ""),
            }

        except Exception as e:
            logger.exception("Vision garment analysis failed")
            return {
                "contains_garment": False,
                "confidence": 0.0,
                "description": f"Analysis failed: {str(e)}",
            }

    async def tag_garment(
        self,
        image_bytes: bytes,
        detection_description: str,
        user_llm: "UserLLMConfig | None" = None,
    ) -> dict:
        """Generate structured clothing tags from the image and detector description."""
        started_at = time.perf_counter()
        logger.info(
            "Vision garment tagging started: size_bytes=%s detection_description=%s",
            len(image_bytes),
            detection_description or "<empty>",
        )
        fallback = self._fallback_garment_tags(detection_description)

        if not self._can_use_vision(user_llm=user_llm):
            logger.warning("Vision garment tagging skipped because vision config is unavailable")
            return fallback

        try:
            from openai import AsyncOpenAI

            if user_llm is not None and user_llm.is_usable():
                client = AsyncOpenAI(
                    api_key=user_llm.api_key,
                    base_url=user_llm.base_url,
                )
                model_name = user_llm.model
            else:
                client = AsyncOpenAI(
                    api_key=_vision_api_key(),
                    base_url=_vision_api_base(),
                )
                model_name = _vision_model()
                logger.debug(
                    "Vision tagging using server vision LLM: base_url=%s model=%s",
                    _vision_api_base(), model_name,
                )

            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "You are a fashion tagging assistant. "
                                    f"A previous detector described this image as: {detection_description or 'unknown garment'}. "
                                    "Inspect the image and return ONLY a JSON object. "
                                    "Use these fields: "
                                    '{"category": "top|bottom|outerwear|shoes|accessory", "color": "string", "thickness": "thin|medium|thick", "style_features": ["string"], "warmth": 0.0-1.0, "cooling": 0.0-1.0, "season": ["spring|summer|autumn|winter|all"], "materials": ["string"], "pattern": "string", "fit": "string", "tags": ["string"], "summary": "string"}'
                                ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                            },
                        ],
                    }
                ],
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
            )

            result_text = response.choices[0].message.content.strip()
            logger.debug("Vision garment tagging raw response: %s", result_text)
            result = self._parse_json_result(result_text)
            normalized = self._normalize_tag_result(result, fallback, detection_description)
            logger.info(
                "Vision garment tagging finished: category=%s colors=%s tags=%s elapsed_ms=%.2f",
                normalized.get("category"),
                normalized.get("color"),
                normalized.get("tags"),
                (time.perf_counter() - started_at) * 1000,
            )
            return normalized

        except Exception:
            logger.exception("Vision garment tagging failed, returning fallback tags")
            return fallback

    def _can_use_vision(self, user_llm: "UserLLMConfig | None" = None) -> bool:
        if user_llm is not None and user_llm.is_usable():
            return True
        return bool(_vision_api_key() and _vision_api_base() and _vision_model())

    def _parse_json_result(self, raw_text: str) -> dict:
        content = raw_text.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content
            content = content.rsplit("\n", 1)[0] if "\n" in content else content
            content = content.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(content)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}

    def _fallback_garment_tags(self, detection_description: str) -> dict:
        return {
            "category": "outerwear",
            "color": None,
            "thickness": "medium",
            "style_features": [],
            "warmth": 0.5,
            "cooling": 0.5,
            "season": ["all"],
            "materials": [],
            "pattern": None,
            "fit": None,
            "tags": ["auto-tagged"],
            "summary": detection_description or "AI tagging unavailable",
        }

    def _normalize_tag_result(self, result: dict, fallback: dict, detection_description: str) -> dict:
        merged = {**fallback, **result}
        merged.setdefault("summary", detection_description or fallback.get("summary", ""))
        if isinstance(merged.get("style_features"), str):
            merged["style_features"] = [merged["style_features"]]
        if isinstance(merged.get("materials"), str):
            merged["materials"] = [merged["materials"]]
        if isinstance(merged.get("tags"), str):
            merged["tags"] = [merged["tags"]]
        if isinstance(merged.get("season"), str):
            merged["season"] = [merged["season"]]
        return merged
