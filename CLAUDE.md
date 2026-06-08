# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

L-Wardrobe is an AI-powered wardrobe management app with a Vue 3 frontend and FastAPI backend.
- **Frontend**: Vue 3 + Pinia + Vue Router + Vite
- **Backend**: FastAPI + LangChain Agent + PostgreSQL (or SQLite for dev)
- **AI**: LangChain `create_tool_calling_agent` with DeepSeek / OpenAI-compatible LLM
- **Database**: SQLAlchemy 2.0 async ORM + Alembic migrations
- **Auth**: Custom JWT (HMAC-signed, not standard JWT) via `Authorization: Bearer <token>`
- **Image Processing**: rembg background removal + AI garment detection/tagging

## Development Commands

### Backend
```bash
cd backend
conda activate l-wardrobe
python main.py --port 8080        # runs uvicorn with reload when DEBUG=true
```
- API docs: `http://localhost:8080/docs`
- Settings loaded from `backend/.env` (see `.env.example` for required keys)

### Frontend
```bash
cd frontend
npm install
npm run dev                       # Vite dev server on port 5173
```

### Database
```bash
alembic -c db/alembic.ini upgrade head   # apply migrations
```

## Repository Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/         # API routers (auth, garments, user, outfit, daily-tips)
│   │   ├── core/           # Config (pydantic-settings), security (HMAC JWT), logging
│   │   ├── models/         # Pydantic schemas
│   │   ├── services/       # Business logic:
│   │   │   ├── styling_agent.py    # LangChain Agent (outfit recommend + daily tips)
│   │   │   ├── garment_vision.py   # Image upload + AI detection + tagging + rembg
│   │   │   ├── weather.py          # 和风天气 API wrapper
│   │   │   └── llm_health.py       # LLM API health check
│   │   └── static/         # Image storage (raw + processed)
│   ├── main.py             # FastAPI entrypoint
│   ├── requirements.txt
│   └── environment.yml     # Conda env: l-wardrobe (Python 3.12)
├── db/                     # Database module (independent Python package)
│   ├── models/             # ORM models: User, UserProfile, Clothes, OutfitRecommendation, DailyTip, etc.
│   ├── repositories/       # Repository pattern: UserRepository, ClothesRepository, RecommendationRepository, etc.
│   ├── migrations/         # Alembic migration scripts
│   └── session.py          # Async engine + session factory
├── frontend/
│   ├── src/
│   │   ├── views/          # Page-level Vue components
│   │   ├── components/     # Reusable + business components (AIThinking, OutfitCard, SceneSelector, etc.)
│   │   ├── stores/         # Pinia stores: auth, user, wardrobe, outfit, theme
│   │   ├── services/       # API clients (auth.js, garment.js, outfit.js)
│   │   └── router/         # Vue Router with auth guard
│   └── vite.config.js
├── docs/                   # Project documentation (architecture, setup, deployment)
└── docker-compose.yml      # Docker orchestration
```

## Architecture Notes

### AI Layer (LangChain Agent)

**Core file**: `backend/app/services/styling_agent.py` — `StylingAgentService`

- **Agent type**: `create_tool_calling_agent` + `AgentExecutor` (LangChain)
- **LLM backend**: DeepSeek via `langchain-openai` (OpenAI-compatible), or any generic OpenAI-compatible API
- **Config keys**: `DEEPSEEK_API_KEY` / `DEEPSEEK_BASE_URL`, or `LLM_API_KEY` / `LLM_API_BASE` / `LLM_MODEL`

**Dynamic Tools** (all `@tool` async functions, bound to a shared `AsyncSession`):

| Tool | Function | Description |
|------|----------|-------------|
| `get_weather` | `_weather_tool` | Calls `WeatherService.get_current(city)` dynamically |
| `search_wardrobe` | `_search_wardrobe_tool` | Queries `ClothesRepository.list_by_user()` with category/season/color/status filters |
| `get_wardrobe_items_by_ids` | `_get_wardrobe_items_tool` | Batch fetch clothes by IDs via `ClothesRepository.get_by_ids()` |
| `count_wardrobe_items` | `_count_wardrobe_tool` | Total wardrobe count |
| `get_user_profile` | `_user_profile_tool` | Reads `UserRepository.get_by_id()` for location, style_preference |
| `get_history_recommendations` | `_history_tool` | Reads past recommendations via `RecommendationRepository.list_by_user()` |
| `get_style_rules` | `_style_rules_tool` | Static styling principles per scene |
| `save_recommendation` | `_save_recommendation_tool` | Persists recommendation to DB with selected items |

**Agent flow** (`POST /api/v1/outfit/recommend`):
1. Route receives `{scene, wardrobeIds}` + authenticated user
2. `StylingAgentService(db)` instantiated with request DB session
3. Agent executor runs with system prompt + user input
4. LLM calls tools dynamically: `get_user_profile` → `get_weather` → `search_wardrobe` / `get_wardrobe_items_by_ids` → `save_recommendation`
5. Structured JSON output parsed and normalized
6. Route wraps in `{code, data, msg}` envelope

**Token optimization**: Agent only fetches relevant wardrobe items via filtered `search_wardrobe` instead of dumping entire wardrobe into prompt. This reduces prompt tokens by 60-80% compared to the old direct-API approach.

**Fallback chain**: If LLM API key missing → immediate fallback. If agent returns invalid JSON → fallback. If tools fail → error enters scratchpad, agent may retry, else fallback. All fallback outputs match success response shape.

### Database Layer

**Key models** (see `db/models/`):
- `User` / `UserProfile` — split model: `User` has auth fields, `UserProfile` has display_name, location, style_preference, etc.
- `Clothes` (alias `WardrobeItem`) — wardrobe items with `category`, `color`, `seasons` (JSONB list), `status`, `attributes` (JSONB dict)
- `OutfitRecommendation` — stored recommendations with `weather_snapshot` (JSONB), `match_rate`, linked `RecommendationItem`s
- `DailyTip` — daily advice records
- `OutfitFavorite` / `OutfitHistory` — user interactions

**Repositories** (see `db/repositories/`):
- `ClothesRepository` — `list_by_user(user_id, category, season, color, status, limit, offset)` with JSONB `seasons.contains([season])` filtering
- `UserRepository` — `get_by_id` eagerly loads `profile` via `selectinload`
- `RecommendationRepository` — `create()` accepts `items` as `Clothes` objects or dicts with `{"item": Clothes, "slot": str}`

**Session management**: `get_db()` is a FastAPI dependency that yields `AsyncSession`, auto-commits on success, rolls back on exception. `db/session.py` auto-converts URLs: `sqlite://` → `sqlite+aiosqlite://`, `postgresql://` → `postgresql+asyncpg://`.

### Auth

Custom HMAC-signed token (not standard JWT):
- `create_access_token(user_id, username)` → base64-encoded JSON payload + HMAC-SHA256 signature
- `decode_access_token(token)` → verifies signature and expiry
- `get_current_user` dependency resolves token → DB user lookup
- `require_user` raises 401 for anonymous users

### Image Processing

`GarmentVisionService` (`backend/app/services/garment_vision.py`):
1. `analyze_garment(image_bytes)` — AI detection (contains garment? category?)
2. `process_image(image_bytes, filename)` — background removal via rembg, save to `app/static/`
3. `tag_garment(image_bytes, detection_description)` — AI tagging for color, style, season

### API Contracts

- `POST /api/v1/outfit/recommend` — AI outfit recommendation. Body: `{scene, wardrobeIds}`. Returns `{code, data: {id, name, description, scene, matchRate, reason, image, selectedItems, ...}, msg}`
- `GET /api/v1/daily-tips/` — Daily styling tip. Returns `{tip: {...}, user_id}`
- `POST /api/v1/garments/upload` — Multipart image upload with AI detection/tagging
- `GET /api/v1/garments/` — List user's clothes from DB
- `GET /api/v1/user/me` — User profile with wardrobe count
- `PATCH /api/v1/user/me` — Update profile
- `POST /api/v1/auth/register` / `/auth/login` — JWT auth

## Git Workflow

See `CONTRIBUTING.md` for full details. Key conventions:
- Branch naming: `features/<name>`, `bug-fix/<name>`, `issue/<number>-<desc>`
- Commit format: `<type>: <subject>` where type is `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Merge to `main` via **Squash and merge**
- Sync feature branches with `git rebase main` before PR
