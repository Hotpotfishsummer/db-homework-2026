from fastapi import FastAPI
from app.core.config import get_settings
from app.api.v1 import garments, user, daily_tips, outfit

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AI-powered wardrobe management backend",
    version="0.1.0",
    debug=settings.debug,
)

# Register API v1 routers
app.include_router(garments.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(daily_tips.router, prefix="/api/v1")
app.include_router(outfit.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name}


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name}"}


if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host")
    args = parser.parse_args()

    uvicorn.run("main:app", host=args.host, port=args.port, reload=settings.debug)
