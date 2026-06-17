# AGENTS.md

This file provides guidance to Codex and other coding agents when working in this repository.

## Project Overview

L-Wardrobe is an AI-powered wardrobe management app with a Vue 3 frontend and FastAPI backend.

- **Frontend**: Vue 3 + Pinia + Vue Router + Vite
- **Backend**: FastAPI + LangChain agents + PostgreSQL
- **AI**: LangChain `create_tool_calling_agent` with DeepSeek or another OpenAI-compatible LLM
- **Database**: SQLAlchemy 2.0 async ORM + Alembic migrations
- **Auth**: Custom HMAC-signed token via `Authorization: Bearer <token>`, not standard JWT
- **Image Processing**: `rembg` background removal plus AI garment detection and tagging

## Development Commands

### Backend

```bash
cd backend
conda activate l-wardrobe
python main.py --port 8080
```

- API docs: `http://localhost:8080/docs`
- Settings load from `backend/.env`; see `backend/.env.example` for required keys.
- `python main.py --port 8080` runs uvicorn with reload when `DEBUG=true`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

- Vite serves the frontend on port `5173` by default.

### Database

```bash
alembic -c db/alembic.ini upgrade head
```

## Repository Structure

```text
backend/
  app/
    api/v1/         API routers: auth, garments, user, outfit, daily tips, recommendations
    core/           Config, security, logging, user LLM overrides
    models/         Pydantic schemas
    services/       Business logic and AI services
  main.py           FastAPI entrypoint
  requirements.txt
  environment.yml   Conda env: l-wardrobe, Python 3.12
db/
  models/           ORM models
  repositories/     Repository pattern
  migrations/       Alembic migration scripts
  session.py        Async engine and session factory
frontend/
  src/
    views/          Page-level Vue components
    components/     Reusable and business components
    stores/         Pinia stores
    services/       API clients
    router/         Vue Router with auth guard
docs/               Project documentation
docker-compose.yml  Docker orchestration
```

## Architecture Notes

### AI Layer

Shared agent plumbing lives in `backend/app/services/base_agent.py`.

Outfit/styling agent:

- Core file: `backend/app/services/styling_agent.py`
- Service: `StylingAgentService`
- API: `POST /api/v1/outfit/recommend`
- Purpose: build outfits from the user's existing wardrobe.
- Tools include weather lookup, wardrobe search, item fetch by IDs, wardrobe count, user profile, recommendation history, style rules, and recommendation persistence.

Shopping/recommendation agent:

- Core file: `backend/app/services/recommendation_agent.py`
- Service: `RecommendationAgentService`
- APIs under `/api/v1/recommend`
- Purpose: recommend new shopping items, mix new items into outfit slots, and analyze wardrobe gaps.
- Stores shopping recommendations via `ShoppingRecommendationRepository`.

Fallback output must match the success response shape. Use fallback when the LLM API key is missing, the agent returns invalid JSON, or tool failures cannot be recovered.

### Database Layer

Key models live in `db/models/`:

- `User` / `UserProfile`: auth fields and profile fields are split.
- `Clothes` / `WardrobeItem`: wardrobe items with `category`, `color`, `seasons`, `status`, and `attributes`.
- `OutfitRecommendation`: stored outfit recommendations with weather snapshots, match rate, and linked items.
- `ShoppingRecommendation`: recommended new purchase items and status tracking.
- `DailyTip`: daily advice records.
- `OutfitFavorite` / `OutfitHistory`: user interactions.

Repository conventions:

- `ClothesRepository.list_by_user(...)` supports category, season, color, status, limit, and offset filters.
- `UserRepository.get_by_id(...)` eagerly loads `profile` via `selectinload`.
- `RecommendationRepository.create(...)` accepts item objects or dicts shaped like `{"item": Clothes, "slot": str}`.
- `ShoppingRecommendationRepository` owns recommended-purchase persistence and status changes.

Session management:

- `get_db()` is a FastAPI dependency that yields an `AsyncSession`.
- It commits on success and rolls back on exception.
- `db/session.py` converts common PostgreSQL URLs to asyncpg-compatible URLs.

### Auth

The project uses a custom HMAC-signed token, not standard JWT:

- `create_access_token(user_id, username)` creates a base64 JSON payload plus HMAC-SHA256 signature.
- `decode_access_token(token)` verifies signature and expiry.
- `get_current_user` resolves the token and performs DB lookup.
- `require_user` raises `401` for anonymous users.

### Image Processing

Core file: `backend/app/services/garment_vision.py`

Typical flow:

1. `analyze_garment(image_bytes)` detects whether the image contains a garment and infers category details.
2. `process_image(image_bytes, filename)` removes background with `rembg` and saves raw and processed images.
3. `tag_garment(image_bytes, detection_description)` tags color, style, season, and related attributes.

## API Contracts

- `POST /api/v1/outfit/recommend`: body `{scene, wardrobeIds}`; returns `{code, data, msg}`.
- `GET /api/v1/daily-tips/`: returns daily styling advice.
- `POST /api/v1/recommend/items`: recommends new shopping items.
- `GET /api/v1/recommend/items`: lists shopping recommendation history.
- `PATCH /api/v1/recommend/items/{id}`: updates shopping recommendation status.
- `POST /api/v1/recommend/items/with-outfit`: mixes owned and recommended items into outfit slots.
- `POST /api/v1/recommend/gap-analysis`: returns wardrobe gap analysis.
- `POST /api/v1/garments/upload`: multipart image upload with AI detection and tagging.
- `GET /api/v1/garments/`: lists the authenticated user's clothes.
- `GET /api/v1/user/me`: returns user profile with wardrobe count.
- `PATCH /api/v1/user/me`: updates user profile.
- `POST /api/v1/auth/register` and `POST /api/v1/auth/login`: auth endpoints.

## Working Guidelines

- Prefer existing patterns in `backend/app`, `db/repositories`, and `frontend/src` before adding new abstractions.
- Keep backend responses compatible with the established `{code, data, msg}` envelope where routes already use it.
- Use async SQLAlchemy APIs consistently; do not introduce sync DB access in request paths.
- Avoid committing generated local state, uploaded files, local databases, credentials, or agent cache directories.
- Preserve user changes in the working tree. Do not reset or overwrite unrelated edits.

## Git Workflow

See `CONTRIBUTING.md` for full details.

- Branch naming: `features/<name>`, `bug-fix/<name>`, `issue/<number>-<desc>`
- Commit format: `<type>: <subject>`
- Common types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Merge to `main` via squash merge.
- Sync feature branches with `git rebase main` before opening or updating a PR.
