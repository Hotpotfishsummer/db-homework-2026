from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.security import require_user
from app.services.vision import VisionService

router = APIRouter(prefix="/garments", tags=["garments"])
vision = VisionService()


@router.post("/upload")
async def upload_garment(
    image: UploadFile = File(...),
    user: dict = Depends(require_user),
):
    """Upload a garment image and remove background."""
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    result = await vision.process_image(image)
    return {
        "user_id": user["user_id"],
        "filename": image.filename,
        "processed": result,
    }


@router.get("/")
async def list_garments(user: dict = Depends(require_user)):
    """List user's garment collection — DB integration pending."""
    return {"garments": [], "user_id": user["user_id"]}
