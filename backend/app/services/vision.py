import io
import base64
import json
from pathlib import Path

from fastapi import UploadFile
from PIL import Image

from app.core.config import get_settings

RAW_DIR = Path("app/static/raw")
PROCESSED_DIR = Path("app/static/processed")
settings = get_settings()


class VisionService:
    """Handles garment image ingestion: background removal and persistence."""

    def __init__(self):
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    async def process_image(self, content: bytes, filename: str | None = None) -> dict:
        """Save raw image bytes and run background removal via rembg if available."""
        raw_path = RAW_DIR / Path(filename or "unknown").name
        raw_path.write_bytes(content)

        processed_path = PROCESSED_DIR / f"no_bg_{raw_path.name}"

        # Import rembg lazily so backend startup is not blocked by optional runtime deps.
        remove_fn = None
        try:
            from rembg import remove as remove_fn
        except BaseException:
            remove_fn = None

        if remove_fn is not None:
            input_image = Image.open(io.BytesIO(content))
            output_image = remove_fn(input_image)
            output_image.save(processed_path)
            bg_removed = True
        else:
            # Graceful fallback — just copy raw if rembg isn't ready
            processed_path.write_bytes(content)
            bg_removed = False

        return {
            "raw_path": str(raw_path),
            "processed_path": str(processed_path),
            "bg_removed": bg_removed,
        }

    async def analyze_garment(self, image_bytes: bytes) -> dict:
        """Analyze if image contains a garment using multimodal LLM."""
        if not self._can_use_vision():
            return {
                "contains_garment": False,
                "confidence": 0.0,
                "description": "AI service unavailable",
            }

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_api_base,
            )

            base64_image = base64.b64encode(image_bytes).decode("utf-8")

            response = await client.chat.completions.create(
                model=settings.llm_model,
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
            result = self._parse_json_result(result_text)
            return {
                "contains_garment": result.get("contains_garment", False),
                "confidence": float(result.get("confidence", 0.0)),
                "description": result.get("description", ""),
            }

        except Exception as e:
            return {
                "contains_garment": False,
                "confidence": 0.0,
                "description": f"Analysis failed: {str(e)}",
            }

    async def tag_garment(self, image_bytes: bytes, detection_description: str) -> dict:
        """Generate structured clothing tags from the image and detector description."""
        fallback = self._fallback_garment_tags(detection_description)

        if not self._can_use_vision():
            return fallback

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_api_base,
            )

            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            response = await client.chat.completions.create(
                model=settings.llm_model,
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
            result = self._parse_json_result(result_text)
            return self._normalize_tag_result(result, fallback, detection_description)

        except Exception:
            return fallback

    def _can_use_vision(self) -> bool:
        return bool(settings.llm_api_key and settings.llm_api_base and settings.llm_model)

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
