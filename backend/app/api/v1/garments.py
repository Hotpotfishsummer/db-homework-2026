from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_user
from app.models.schemas import GarmentDetectionResponse, GarmentUploadResponse
from app.services.garment_vision import VisionService
from db import get_db, ClothesRepository, UserRepository

router = APIRouter(prefix="/garments", tags=["garments"])
vision = VisionService()


async def _resolve_user_id(user: dict, db: AsyncSession) -> int:
    raw_user_id = user.get("user_id")
    if isinstance(raw_user_id, int):
        return raw_user_id
    if isinstance(raw_user_id, str) and raw_user_id.isdigit():
        return int(raw_user_id)

    username = str(raw_user_id)
    user_repository = UserRepository(db)
    existing = await user_repository.get_by_username(username)
    if existing is not None:
        return existing.user_id

    created = await user_repository.create(username=username, password_hash="placeholder-password")
    return created.user_id


@router.post("/upload")
async def upload_garment(
    image: UploadFile = File(...),
    user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a garment image, tag it, and persist it to the clothes table."""
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    content = await image.read()
    detection = await vision.analyze_garment(content)

    if not detection["contains_garment"]:
        return GarmentDetectionResponse(**detection)

    processed = await vision.process_image(content, image.filename)
    tags = await vision.tag_garment(content, detection_description=detection["description"])

    resolved_user_id = await _resolve_user_id(user, db)
    repository = ClothesRepository(db)
    item = await repository.create(
        user_id=resolved_user_id,
        image_url=processed["raw_path"],
        category=tags.get("category"),
        attributes={
            "source_filename": image.filename,
            "detection": detection,
            "tags": tags,
            "processed_path": processed["processed_path"],
            "bg_removed": processed["bg_removed"],
        },
    )

    return GarmentUploadResponse(
        contains_garment=True,
        detection=GarmentDetectionResponse(**detection),
        analysis=tags,
        garment={
            "id": item.item_id,
            "item_id": item.item_id,
            "user_id": item.user_id,
            "image_url": item.image_url,
            "category": item.category,
            "attributes": item.attributes,
            "created_at": item.created_at,
        },
    )


@router.get("/")
async def list_garments(
    user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's garment collection."""
    resolved_user_id = await _resolve_user_id(user, db)
    repository = ClothesRepository(db)
    items = await repository.list_by_user(resolved_user_id)
    return {
        "garments": [
            {
                "id": item.item_id,
                "item_id": item.item_id,
                "user_id": item.user_id,
                "image_url": item.image_url,
                "category": item.category,
                "attributes": item.attributes,
                "created_at": item.created_at,
            }
            for item in items
        ],
        "user_id": user["user_id"],
    }


@router.post("/detect")
async def detect_garment(
    image: UploadFile = File(...),
    user: dict = Depends(require_user),
):
    """Analyze if uploaded image contains a garment."""
    if not image.content_type or not image.content_type.startswith("image/"):
        return {
            "contains_garment": False,
            "confidence": 0.0,
            "description": "Invalid file type, only images are accepted",
        }

    content = await image.read()
    result = await vision.analyze_garment(content)
    return result
