from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.schemas import AuthLoginRequest, AuthRegisterRequest, AuthResponse, AuthUserResponse
from db import get_db, UserRepository, ClothesRepository

router = APIRouter(prefix="/auth", tags=["auth"])


def _serialize_user(user, wardrobe_count: int) -> AuthUserResponse:
    return AuthUserResponse(
        user_id=user.user_id,
        username=user.username,
        display_name=user.display_name,
        style_preference=user.style_preference,
        location=user.location,
        wardrobe_count=wardrobe_count,
        created_at=user.created_at,
    )


async def _build_auth_response(user, db: AsyncSession) -> AuthResponse:
    wardrobe_count = await ClothesRepository(db).count_by_user(user.user_id)
    return AuthResponse(
        access_token=create_access_token(user.user_id, user.username),
        user=_serialize_user(user, wardrobe_count),
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: AuthRegisterRequest, db: AsyncSession = Depends(get_db)):
    user_repository = UserRepository(db)
    existing = await user_repository.get_by_username(payload.username)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    user = await user_repository.create(
        username=payload.username,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        style_preference=payload.style_preference,
        location=payload.location,
    )
    return await _build_auth_response(user, db)


@router.post("/login", response_model=AuthResponse)
async def login(payload: AuthLoginRequest, db: AsyncSession = Depends(get_db)):
    user_repository = UserRepository(db)
    user = await user_repository.get_by_username(payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")

    return await _build_auth_response(user, db)