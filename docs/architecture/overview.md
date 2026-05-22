# 架构概述

## 系统组件

```
┌─────────────────────────────────────────────────────────────┐
│                    Vue 3 SPA (frontend/)                    │
│                  Pinia stores + Vue Router                   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP JSON
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI (backend/)                        │
│              app/api/v1/    app/services/                   │
│                   weather_svc + outfit_ai_svc                │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
┌──────────────┐  ┌──────────┐  ┌──────────┐
│  和风天气 API  │  │DeepSeek  │  │PostgreSQL│
│              │  │   LLM    │  │  (db/)   │
└──────────────┘  └──────────┘  └──────────┘
```

## 模块职责

| 模块 | 职责 | 入口文件 |
|------|------|----------|
| `frontend/` | UI、状态管理、Mock/真实 API 切换 | `src/main.js` |
| `backend/` | REST API、AI 服务编排、图片处理 | `main.py` |
| `db/` | ORM 模型、Repository 查询、Alembic 迁移 | `session.py` |

## 关键架构决策

### USE_MOCK 切换

前端 `services/outfit.js` 中的 `USE_MOCK` 标志控制 API 来源：

- `true` — 使用本地 Mock 函数，2.5s 延迟，返回 15 套预设搭配
- `false` — 调用真实后端 `POST /api/v1/outfit/recommend`

### db/ 作为 Python 包

`db/` 目录可直接导入，无需 `pip install`：

```python
from db import get_db, UserRepository, WardrobeRepository
```

### 异步 SQLAlchemy 2.0

所有数据库操作均为 `async def`，使用 `asyncpg` 驱动。

## 前端状态管理

5 个 Pinia stores：

| Store | 职责 |
|-------|------|
| `auth` | 用户认证（localStorage Mock） |
| `wardrobe` | 衣橱数据 |
| `outfit` | AI 搭配三阶段状态机 |
| `user` | 用户档案、收藏、历史 |
| `theme` | 亮/暗主题切换 |