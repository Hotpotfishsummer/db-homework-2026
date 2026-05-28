import io
from pathlib import Path
from fastapi import UploadFile
from PIL import Image

RAW_DIR = Path("app/static/raw")
PROCESSED_DIR = Path("app/static/processed")


class VisionService:
    """Handles garment image ingestion: background removal and persistence."""

    def __init__(self):
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    async def process_image(self, upload: UploadFile) -> dict:
        """Save raw upload and run background removal via rembg if available."""
        raw_path = RAW_DIR / (upload.filename or "unknown")
        content = await upload.read()
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
