# L-Wardrobe — AI 穿搭推荐系统

前后端分离的 AI 穿搭推荐应用，核心功能是根据天气 + 用户衣橱生成场景化穿搭方案。

- **前端**：Vue 3 + Pinia + Vue Router + Vite
- **后端**：FastAPI + LangChain Agent（工具调用）+ DeepSeek / OpenAI-compatible LLM + 和风天气 API
- **数据库**：PostgreSQL（Neon 云）+ SQLAlchemy 2.0 异步 ORM + Alembic 迁移

---

## 目录结构

```text
.
├── db/                          # 数据库模块（独立 Python 包）
│   ├── base.py                  # SQLAlchemy DeclarativeBase
│   ├── session.py               # 异步引擎 + 连接池 + get_db
│   ├── alembic.ini              # Alembic 迁移配置
│   ├── .env.example             # 数据库连接模板
│   ├── models/                  # ORM 模型（4 张表）
│   │   ├── user.py              # users 表
│   │   ├── wardrobe_item.py     # wardrobe_items 表（JSONB）
│   │   ├── outfit_recommendation.py # outfit_recommendations 表
│   │   └── tryon_result.py      # tryon_results 表
│   ├── repositories/            # Repository 查询层（21 个方法）
│   │   ├── user_repo.py
│   │   ├── wardrobe_repo.py
│   │   ├── recommendation_repo.py
│   │   └── tryon_repo.py
│   ├── migrations/              # Alembic 迁移脚本
│   │   ├── env.py               # 异步迁移环境
│   │   └── versions/            # 已应用的迁移
│   └── README.md                # 数据库模块详细文档
├── backend/
│   ├── app/
│   │   ├── api/v1/         # API 路由
│   │   │   ├── auth.py         # 注册/登录（JWT）
│   │   │   ├── garments.py     # 衣服上传/列表/检测
│   │   │   ├── outfit.py       # AI 穿搭推荐（LangChain Agent）
│   │   │   ├── daily_tips.py   # 每日穿搭小贴士（LangChain Agent）
│   │   │   └── user.py         # 用户资料获取/更新
│   │   ├── core/           # 配置（pydantic-settings）+ 安全 + 日志
│   │   ├── models/         # Pydantic schemas
│   │   ├── services/       # 业务逻辑
│   │   │   ├── styling_agent.py  # ⭐ LangChain Agent 核心
│   │   │   ├── weather.py        # 和风天气 API
│   │   │   ├── garment_vision.py # 图片上传 + rembg 背景去除
│   │   │   └── llm_health.py     # LLM API 可用性探测
│   │   └── static/         # 图片存储（raw + processed）
│   ├── tests/
│   ├── main.py             # FastAPI 入口
│   ├── .env                # 本地开发环境变量
│   ├── .env.example
│   ├── requirements.txt
│   └── environment.yml
└── frontend/
    ├── src/
    │   ├── views/             # 页面级组件（9 个页面）
    │   │   ├── HomeView.vue          # AI 推荐首页（滑动卡片）
    │   │   ├── OutfitMatchView.vue   # AI 搭配专页（输入 → 生成 → 结果）
    │   │   ├── OutfitDetailView.vue  # 穿搭详情
    │   │   ├── WardrobeView.vue      # 衣橱管理
    │   │   ├── ProfileView.vue       # 个人中心
    │   │   ├── AddClothView.vue      # 录入新单品
    │   │   ├── LikedView.vue         # 收藏列表
    │   │   ├── HistoryView.vue       # 浏览历史
    │   │   ├── LoginView.vue         # 登录
    │   │   └── RegisterView.vue      # 注册
    │   ├── components/        # 复用组件
    │   │   ├── biz/                  # 业务组件（AI 搭配模块）
    │   │   │   ├── MatchFilter.vue   # 场景/天气选择器
    │   │   │   ├── AIThinking.vue    # 生成动画组件
    │   │   │   └── OutfitCard.vue    # 搭配结果卡片
    │   │   ├── BottomNav.vue         # 底部导航栏
    │   │   ├── BottomSheet.vue       # 底部弹出菜单
    │   │   └── ClothingDetail.vue    # 衣服详情弹窗
    │   ├── stores/            # Pinia 状态管理（5 个模块）
    │   │   ├── auth.js               # 用户认证
    │   │   ├── outfit.js             # AI 搭配状态（新增）
    │   │   ├── wardrobe.js           # 衣橱数据
    │   │   ├── user.js               # 用户档案/收藏/历史
    │   │   └── theme.js              # 主题管理
    │   ├── services/          # API 客户端
    │   │   ├── api.js                # API 基地址 + 超时配置
    │   │   ├── outfit.js             # AI 搭配接口（Mock + 真实，USE_MOCK 一键切换）
    │   │   └── user.js               # 用户头像/档案接口
    │   ├── composables/       # 组合式函数
    │   │   └── useHaptics.js         # 触觉反馈
    │   └── router/            # Vue Router（路由守卫）
    ├── vite.config.js
    └── package.json
```

---

## 环境变量

后端统一使用 [backend/.env](backend/.env) 作为本地运行配置入口，仓库里提供了 [backend/.env.example](backend/.env.example) 作为模板。Docker Compose 启动时也会读取这个文件。

```bash
# 本地 PostgreSQL（推荐，Compose 默认使用）
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/l_wardrobe

# 其他运行时配置
HEFENG_API_KEY=
DEEPSEEK_API_KEY=
LLM_API_KEY=
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

详细配置说明见 [db/README.md](db/README.md)。

---

## Docker Compose 开发环境

仓库根目录提供了统一的 [docker-compose.yml](docker-compose.yml)，包含 `postgres`、`backend`、`frontend` 三个服务。

```bash
docker compose up --build backend
docker compose up --build frontend
docker compose logs -f
docker compose down --remove-orphans
```

默认端口：`8000`（后端）、`5173`（前端）、`5433`（本机映射的 PostgreSQL）。

在 VS Code 中也可以直接使用 `.vscode/tasks.json` 里的 `Frontend: Dev`、`Backend: Compose Up`、`Frontend: Compose Up`、`Compose: Logs`、`Compose: Down`，以及 `.vscode/launch.json` 里的 `Full Stack: Backend + Frontend`。

---

## 启动方式

### 0. Compose 启动（推荐开发联调）

```bash
docker compose up --build backend
docker compose up --build frontend
```

这些命令会分别在当前终端持续输出对应服务的日志，适合调试时直接观察启动过程。

首次启动如果本机没有缓存镜像，需要先能访问 Docker Hub。

### 1. 数据库初始化（首次或换环境时）

```bash
# 在项目根目录执行，应用 Alembic 迁移建表
alembic -c db/alembic.ini upgrade head
```

### 2. 后端

```bash
cd backend
conda activate l-wardrobe      # 或 conda create -f environment.yml
python main.py --port 8080
```

- API 文档：`http://localhost:8080/docs`
- VS Code：运行 `Backend: Open Swagger UI` 可在后端启动后直接打开 Swagger
- `DEBUG=true` 时自动热重载，AgentExecutor 以 `verbose=True` 输出推理链

### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

- 默认端口 5173（Vite）或 8081（vue-cli）
- API 基地址：`/api/v1`，Compose 开发环境下由 Vite 代理到后端容器

---

## 后端 API 文档

### 通用响应格式

| 状态 | 格式 |
|------|------|
| 成功 | `{"code": 200, "data": {...}, "msg": "success"}` |
| 失败 | `{"code": 400/401/500, "msg": "错误描述"}`（待统一） |

### 1. AI 穿搭推荐（核心）

**POST** `/api/v1/outfit/recommend`

**Headers：**
```
Content-Type: application/json
Authorization: Bearer {token}
```

**Request Body：**
```json
{
  "scene": "commute",       // 场景: commute/date/casual/sports/party
  "wardrobeIds": [1, 2, 4]  // 可用衣服 ID 列表
}
```

**Response：**
```json
{
  "code": 200,
  "data": {
    "id": "uuid",
    "name": "简约通勤风",
    "description": "白色衬衫搭配卡其色休闲裤...",
    "scene": "通勤",
    "matchRate": 92,
    "reason": "阴天24°C通勤场景下，白色衬衫清爽透气...",
    "image": ""
  },
  "msg": "success"
}
```

**流程：**
1. 实例化 `StylingAgentService(db)`，注入数据库会话
2. Agent 动态调用工具：先查 `get_user_profile` 获取 location → 再查 `get_weather` → 按需 `search_wardrobe` / `get_wardrobe_items_by_ids` 筛选单品
3. LLM 基于真实数据生成推荐，调用 `save_recommendation` 持久化
4. 返回 `{code, data, msg}` 格式

**Token 优化：** Agent 只查询相关单品，不 dump 全部衣橱，token 消耗降低 60-80%。

**Fallback：** 若 API key 未填、Agent 返回无效 JSON 或工具失败，自动降级为模板数据，前端无感知。

### 1.1 AI 单品推荐（新购）🆕

> 与 AI 搭配严格区分：**搭配** 解决"今天穿什么"（限于衣橱），**推荐** 解决"我还缺什么 / 要买什么"（可以推荐新单品）。

**POST** `/api/v1/recommend/items`

**Headers：**
```
Content-Type: application/json
Authorization: Bearer {token}
```

**Request Body：**
```json
{
  "scene": "commute",
  "weather": { "temp": 24, "text": "阴" },
  "gapFocus": "outerwear"   // 可选, 想重点补的品类
}
```

**Response：**
```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": "uuid-1",
        "name": "米白色羊毛混纺大衣",
        "category": "outerwear",
        "color": "米白",
        "style_tags": ["极简", "通勤", "百搭"],
        "price_range": "500-800元",
        "purchase_url": null,
        "reason": "你已有较多深色内搭，缺一件浅色外搭来提亮通勤造型",
        "priority": 92
      }
    ],
    "scene": "通勤",
    "weatherSummary": "阴，24°C",
    "generatedBy": "langchain-agent"
  },
  "msg": "success"
}
```

**持久化**：所有推荐自动写入 `shopping_recommendations` 表（status=pending），可通过 PATCH `/api/v1/recommend/items/{id}` 标记为 bought / dismissed。

### 1.2 AI 推荐 + 嵌入搭配 🆕

**POST** `/api/v1/recommend/items/with-outfit`

返回完整搭配方案，每个 slot 标记 `need_buy: true/false`，区分衣橱已有 vs 需新购。

**Request Body：**
```json
{ "scene": "date" }
```

**Response（节选）：**
```json
{
  "code": 200,
  "data": {
    "outfit": {
      "name": "约会清新搭配",
      "matchRate": 88,
      "slots": [
        { "category": "top", "name": "白T恤", "need_buy": false, "wardrobe_id": 1, "image": "/static/garments/xxx.webp" },
        { "category": "bottom", "name": "卡其裤", "need_buy": false, "wardrobe_id": 3, "image": "/static/garments/yyy.webp" },
        { "category": "shoes", "name": "小白鞋", "need_buy": true, "purchase_url": null, "reason": "衣橱没有白色板鞋，建议入手基础款" }
      ]
    },
    "generatedBy": "langchain-agent"
  },
  "msg": "success"
}
```

### 1.3 衣橱缺口报告 🆕

**POST** `/api/v1/recommend/gap-analysis`

**Response：**
```json
{
  "code": 200,
  "data": {
    "report": {
      "summary": "衣橱整体以休闲款为主，缺少正式通勤外套和深色鞋履",
      "gaps": [
        { "category": "outerwear", "current": 1, "suggested": 3, "advice": "建议补 1-2 件可跨场景的中性色外套" },
        { "category": "shoes", "current": 2, "suggested": 4, "advice": "缺一双深色乐福鞋通勤用" }
      ],
      "generatedBy": "langchain-agent"
    }
  },
  "msg": "success"
}
```

---

### 2. 衣服图片上传

**POST** `/api/v1/garments/upload`

**Headers：**
```
Content-Type: multipart/form-data
Authorization: Bearer {token}
```

**Form Data：**
```
image: <文件>
```

**Response：**
```json
{
  "user_id": "...",
  "filename": "...",
  "processed": {
    "raw_path": "app/static/raw/xxx.jpg",
    "processed_path": "app/static/processed/no_bg_xxx.jpg",
    "bg_removed": true
  }
}
```

---

### 3. 衣服列表

**GET** `/api/v1/garments/`

**Headers：**
```
Authorization: Bearer {token}
```

**Response：**
```json
{
  "garments": [
    {
      "id": 1,
      "item_id": 1,
      "user_id": 1,
      "image_url": "app/static/processed/xxx.jpg",
      "category": "top",
      "attributes": { ... },
      "created_at": "2024-01-01T00:00:00+00:00"
    }
  ],
  "user_id": "..."
}
```

---

### 4. 用户信息

**GET** `/api/v1/user/me`

**Response：**
```json
{
  "user_id": 1,
  "username": "alice",
  "display_name": "Alice",
  "style_preference": "casual",
  "location": "深圳",
  "wardrobe_count": 12,
  "created_at": "2024-01-01T00:00:00+00:00"
}
```

**PATCH** `/api/v1/user/me`

更新用户资料：`display_name`, `style_preference`, `location`。

---

### 5. 每日小贴士

**GET** `/api/v1/daily-tips/`

**Response：**
```json
{
  "tip": {
    "tip": "Layer a light cardigan...",
    "weather_summary": null,
    "wardrobe_items_considered": 0,
    "generated_by": "stub"
  },
  "user_id": "..."
}
```

> **状态：** 当前为随机 demo tip，数据库已收敛，待接入天气 + LLM。

---

## 前端对接指南

### API 地址

`frontend/src/services/api.js` 中默认基地址：
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
```

### 认证

当前阶段：后端 `security.py` 为 placeholder，任意 Bearer token 都返回 `user_001`。前端传 `localStorage.getItem('token')` 即可。

### 场景枚举（前后端必须一致）

| 前端值 | 后端值 | 中文 |
|--------|--------|------|
| commute | commute | 通勤 |
| date | date | 约会 |
| casual | casual | 休闲 |
| sports | sports | 运动 |
| party | party | 派对 |

### AI 搭配接口架构

前端通过统一入口 `generateOutfit()` 调用搭配服务，当前仅保留本地 Mock 生成：

```
前端 UI (OutfitMatchView)
  → Pinia store (outfit.js)
    → services/outfit.js → generateOutfit({ scene, weather, wardrobeIds })
      └── generateOutfitMock()       [当前]
```

切换方式：无需切换后端接口，当前仅使用本地 Mock 生成。

### 三阶段交互流程

```
  INPUT (场景选择 + 天气)  →  GENERATING (AI 动画 + 文案轮播)  →  RESULTS (卡片叠层 + 滑动)
```

对应组件：`MatchFilter.vue` → `AIThinking.vue` → `OutfitCard.vue`，由 `OutfitMatchView.vue` 统一编排。

### 当前前端调用的后端接口

| 前端文件 | 调用接口 | 状态 |
|----------|----------|------|
| `services/outfit.js` | 本地 Mock 生成搭配 | 不再依赖后端旧推荐接口 |

### 前端本地 Mock（暂未调后端）

以下功能目前纯前端实现，后续需逐步对接后端：

| 功能 | 前端实现 | 需后端接口 |
|------|----------|-----------|
| 登录/注册 | `stores/auth.js` + localStorage | `POST /auth/login`, `POST /auth/register` |
| 衣橱 CRUD | `stores/wardrobe.js` | `GET/POST/DELETE /garments` |
| 用户资料 | `stores/user.js` + localStorage | `GET/PATCH /user/me` |
| 收藏/历史 | `stores/user.js`（内存，刷新丢失）| 持久化接口 |
| 每日小贴士 | 已退役 | 无 |
| AI 搭配生成 | `stores/outfit.js` + `services/outfit.js` (Mock) | 本地生成，不再请求后端旧接口 |

---

## 数据库模块说明

数据库模块（`db/`）已收敛为 2 张核心表，并通过 Repository 与 Alembic 迁移管理。详见 `db/README.md`。

### 已完成的数据库能力

| 能力 | 对应 API | 说明 |
|------|----------|------|
| 用户管理 | `UserRepository` | 注册、查询、更新、删除 |
| 衣橱 CRUD | `ClothesRepository` | 添加衣物、列表查询、JSONB 筛选（颜色/季节/分类）、批量查询、删除 |

### 后端接入待办

以下位置需要后端团队从 stub 切换到真实数据库调用：

#### 1. 衣橱查询

`wardrobe_stub.py` 已移除 — 请直接使用 `ClothesRepository`（DB 已接入）。示例：

```python
from db import ClothesRepository
from db.session import async_session

async def get_by_ids(user_id: int, ids: list[int]) -> list[dict]:
  async with async_session() as s:
    repo = ClothesRepository(s)
    items = await repo.get_by_ids(user_id, ids)
    return [{"id": i.item_id, "category": i.category, "image_url": i.image_url, "attributes": i.attributes} for i in items]
```

#### 2. 衣服列表

**文件：** `backend/app/api/v1/garments.py:26`

**改为：** 调用 `ClothesRepository.list_by_user(user_id)`

#### 3. 用户资料

**文件：** `backend/app/api/v1/user.py`

**改为：** `GET /me` 调用 `UserRepository.get_by_id()`；`PATCH /me` 调用 `UserRepository.update()`

## 技术栈版本

| 组件 | 版本 |
|------|------|
| Python | 3.12+ |
| FastAPI | >=0.110.0 |
| SQLAlchemy | >=2.0（异步） |
| asyncpg | >=0.29 |
| Alembic | >=1.13 |
| PostgreSQL | 15+（Neon 云） |
| Vue | 3.2.13 |
| Vite | 最新 |
| Pinia | 3.0.4 |
| rembg | >=2.0.50 |

---

## Git 工作流

详见 `CONTRIBUTING.md`。核心规范：

- 分支命名：`features/xxx`, `bug-fix/xxx`
- Commit 格式：`type: subject`（feat/fix/docs/style/refactor/test/chore）
- PR 合并：Squash and merge
- 同步：`git rebase main`
