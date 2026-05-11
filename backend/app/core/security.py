from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, status, Depends

security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict:
    """Placeholder auth dependency — integrate JWT or OAuth later."""
    if credentials is None:
        return {"user_id": "anonymous", "role": "guest"}

    # TODO: validate JWT token
    return {"user_id": "user_001", "role": "member"}


def require_user(user: dict = Depends(get_current_user)) -> dict:
    if user.get("user_id") == "anonymous":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user
