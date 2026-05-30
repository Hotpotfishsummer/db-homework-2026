import asyncio
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.api.v1 import auth, garments, user
from app.services.llm_health import check_llm_api_availability

settings = get_settings()
setup_logging(level="DEBUG" if settings.debug else "INFO")
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="AI-powered wardrobe management backend",
    version="0.1.0",
    debug=settings.debug,
)

app.state.llm_api_status = {
    "checked": False,
    "available": None,
    "message": "Not checked yet",
}
app.state.llm_api_task = None

# Register API v1 routers
app.include_router(garments.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")


async def _check_llm_api_availability() -> None:
    status = await check_llm_api_availability()
    app.state.llm_api_status = status
    if status.get("available"):
        logger.info("LLM API available")
    else:
        logger.warning(status.get("message", "LLM API unavailable"))


def _log_llm_task_result(task: asyncio.Task) -> None:
    try:
        task.result()
    except asyncio.CancelledError:
        logger.warning("LLM API availability probe task was cancelled")
    except Exception:
        logger.exception("LLM API availability probe task crashed")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Scheduling LLM API availability check")
    task = asyncio.create_task(_check_llm_api_availability())
    task.add_done_callback(_log_llm_task_result)
    app.state.llm_api_task = task
    try:
        yield
    finally:
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


app.router.lifespan_context = lifespan

# Serve uploaded/static images
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "llm_api": app.state.llm_api_status,
    }


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
