# L-Wardrobe 后端服务

FastAPI 驱动的异步后端，为 AI 穿搭推荐应用提供 REST API。核心亮点是通过 **LangChain Agent + 动态数据库工具** 实现智能穿搭推理，token 消耗降低 60-80%。

---

## 技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.12+ | |
| FastAPI | ≥0.110 | 异步 Web 框架 |
| SQLAlchemy | ≥2.0 | 异步 ORM |
| asyncpg | ≥0.29 | PostgreSQL 异步驱动 |
| Alembic | ≥1.13 | 数据库迁移 |
| LangChain | ≥0.2 | Agent 编排框架 |
| langchain-openai | ≥0.1 | OpenAI-compatible LLM 适配 |
| rembg | ≥2.0 | 图片背景去除 |
| Pillow | ≥10.2 | 图像处理 |

---

## 目录结构

```
backend/
├── app/
│   ├── api/v1/              # API 路由层
│   │   ├── auth.py          # 注册 / 登录（JWT）
│   │   ├── garments.py      # 衣服上传 / 列表 / 检测
│   │   ├── outfit.py        # AI 穿搭推荐（LangChain Agent）
│   │   ├── daily_tips.py    # 每日穿搭小贴士（LangChain Agent）
│   │   └── user.py          # 用户资料获取 / 更新
│   ├── core/
│   │   ├── config.py        # pydantic-settings 配置
│   │   ├── security.py      # HMAC JWT + 密码哈希
│   │   └── logging.py       # 结构化日志（console + 文件）
│   ├── models/
│   │   └── schemas.py       # Pydantic 请求/响应模型
│   ├── services/
│   │   ├── styling_agent.py # ⭐ LangChain Agent 核心（见下方）
│   │   ├── garment_vision.py # 图片 AI 检测 + rembg 去背景
│   │   ├── weather.py       # 和风天气 API 封装
│   │   └── llm_health.py    # LLM API 可用性探测
│   └── static/              # 图片存储（raw + processed）
├── main.py                  # FastAPI 入口 + lifespan
├── requirements.txt
├── environment.yml          # Conda 环境定义
├── .env                     # 本地环境变量（gitignore）
└── .env.example             # 环境变量模板
```

---

## 环境变量

复制 `.env.example` 为 `.env` 并填写：

```bash
# 和风天气（https://dev.qweather.com/）
HEFENG_API_KEY=your_key
HEFENG_API_HOST=your_host.re.qweatherapi.com

# LLM（二选一即可）
## 方案 A：DeepSeek
DEEPSEEK_API_KEY=your_key

## 方案 B：任意 OpenAI-compatible API
LLM_API_KEY=your_key
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# 数据库
DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/l_wardrobe

# 应用
APP_NAME=L-Wardrobe
DEBUG=true
SECRET_KEY=change-me-in-production
```

> 数据库 URL 支持自动驱动转换：`sqlite://` → `sqlite+aiosqlite://`，`postgresql://` → `postgresql+asyncpg://`。

---

## 启动方式

### 1. Conda 环境（推荐本地开发）

```bash
conda activate l-wardrobe   # 或 conda env create -f environment.yml
python main.py --port 8080
```

- API 文档：`http://localhost:8080/docs`
- `DEBUG=true` 时自动热重载

### 2. Docker Compose

```bash
docker compose up --build backend
```

---

## AI 层架构（LangChain Agent）

**核心文件**:
- `app/services/base_agent.py` — `BaseAgentService` 基类（LLM 配置 / Agent 执行 / 结果归一化）
- `app/services/styling_agent.py` — `StylingAgentService`（AI 搭配：衣橱内组合）
- `app/services/recommendation_agent.py` — `RecommendationAgentService`（AI 推荐：新购单品 + 嵌入搭配 + 缺口报告）

### 双轨职责划分

| Service | 业务问题 | 输出 | 工具数 |
|---------|----------|------|--------|
| `StylingAgentService` | 今天穿什么 | 1 套搭配 (slot=衣橱已有) | 8 |
| `RecommendationAgentService` | 还缺什么 / 要买什么 | 5-8 件新单品 / 嵌入搭配 / 缺口报告 | 7 |

两个 service 都继承 `BaseAgentService`，共享 `_build_llm` / `_run_agent` / `_extract_output_and_steps` / `_prompt_callable` 等基础设施，只在工具集、系统提示词、输出 JSON schema 三个维度差异化。

### 为什么用 Agent？

旧方案把整份衣橱 dump 进 prompt 直接调用 LLM，问题是：
- Token 浪费：无关单品也塞进上下文
- 无推理步骤：LLM 一次性输出，容易 hallucinate 单品 ID
- 无上下文感知：天气、用户偏好、历史推荐无法动态获取

新方案让 LLM **按需调用工具**，先查天气 → 再查衣橱 → 最后推理，精准控制上下文长度。

### Agent 类型

`create_tool_calling_agent` + `AgentExecutor`（LangChain）
- DeepSeek / 任意 OpenAI-compatible API 均兼容 function calling
- Token 消耗远低于 ReAct（无 "Thought/Action/Observation" 文本循环）
- `max_iterations=3`，超时可控

### 8 个动态工具（outfit 专属）

每个工具都是 `@tool` 装饰的 async 函数，绑定同一个 `AsyncSession`：

| 工具名 | 查询目标 | 说明 |
|--------|----------|------|
| `get_weather` | 和风天气 API | 当前温度、天气状况、风力 |
| `search_wardrobe` | `ClothesRepository.list_by_user()` | JSONB 筛选：category/season/color/status |
| `get_wardrobe_items_by_ids` | `ClothesRepository.get_by_ids()` | 批量精确查询 |
| `count_wardrobe_items` | `ClothesRepository.count_by_user()` | 衣橱总量统计 |
| `get_user_profile` | `UserRepository.get_by_id()` | 位置、风格偏好 |
| `get_history_recommendations` | `RecommendationRepository.list_by_user()` | 避免重复推荐 |
| `get_style_rules` | 静态规则 | 场景化搭配原则 |
| `save_recommendation` | `RecommendationRepository.create()` | 持久化推荐结果 |

### Agent 执行流程

```
POST /api/v1/outfit/recommend
  │
  ├─ 实例化 StylingAgentService(db)
  │
  ├─ _can_use_agent() 检查 LLM API key
  │     └─ 缺失 → 立即 fallback（不调用 LLM）
  │
  ├─ _build_outfit_tools() 组装 8 个工具
  │
  ├─ AgentExecutor.ainvoke()
  │     ├─ LLM → get_user_profile → 获取 location
  │     ├─ LLM → get_weather → 查询天气
  │     ├─ LLM → search_wardrobe(category="top", season="summer", limit=5)
  │     ├─ LLM → get_wardrobe_items_by_ids([...])
  │     ├─ LLM → get_history_recommendations → 去重
  │     └─ LLM → save_recommendation → 写入数据库
  │
  ├─ _normalize_outfit_result() 解析 JSON + 兜底
  │
  └─ 返回 {code, data, msg}
```

### Token 优化效果

| 场景 | 旧方案 | 新方案 | 节省 |
|------|--------|--------|------|
| 50 件衣橱 | 全部 50 件进 prompt | 只查 5-10 件相关单品 | ~70% |
| 空衣橱 | 全部 dump | count=0 即返回 | ~90% |

### 降级链

```
API key 缺失？         → 立即 fallback（模板数据）
Agent 返回无效 JSON？   → Pydantic 解析失败 → fallback
工具执行失败？          → error 进入 scratchpad → LLM 重试 / fallback
超过 max_iterations？   → fallback
```

所有 fallback 输出格式与成功响应完全一致，前端无感知。

### 7 个动态工具（recommendation 专属）

`RecommendationAgentService` 复用通用 6 个工具 + 1 个专属工具 `analyze_wardrobe_gap`：

| 工具名 | 查询目标 | 说明 |
|--------|----------|------|
| `get_weather` | 和风天气 API | 复用通用工具 |
| `search_wardrobe` | `ClothesRepository.list_by_user()` | 复用, 查重 + 风格匹配 |
| `get_wardrobe_items_by_ids` | `ClothesRepository.get_by_ids()` | 复用 |
| `count_wardrobe_items` | `ClothesRepository.count_by_user()` | 复用 |
| `get_user_profile` | `UserRepository.get_by_id()` | 复用 |
| `get_history_recommendations` | `RecommendationRepository.list_by_user()` | 复用 |
| `analyze_wardrobe_gap` | `ClothesRepository.list_by_user()` 按 category 聚合 | 🆕 recommendation 专属, 输出"缺什么 / 缺几件 / 建议补什么" |

### Recommendation Agent 流程

```
POST /api/v1/recommend/items
  │
  ├─ 实例化 RecommendationAgentService(db)
  │
  ├─ _can_use_agent() → 失败则 _fallback_items()
  │
  ├─ _build_recommendation_tools() 组装 7 个工具
  │
  ├─ create_react_agent(llm, tools, prompt=_prompt_callable).ainvoke()
  │     ├─ LLM → get_user_profile → style_preference
  │     ├─ LLM → get_weather
  │     ├─ LLM → analyze_wardrobe_gap → 衣橱分类缺口
  │     ├─ LLM → search_wardrobe (查重 + 风格对齐)
  │     └─ LLM 输出 5-8 件新单品 (name/category/color/style_tags/price_range/reason/priority)
  │
  ├─ ShoppingRecommendationRepository.create_batch() 持久化
  │
  ├─ _normalize_items_result() 解析 JSON
  │
  └─ 返回 {code, data: {items, scene, weatherSummary, generatedBy}, msg}
```

`recommend_with_wardrobe` 与 `analyze_wardrobe_gap` 走同一个 service,提示词不同,流程类似。

---

## API 文档

### 通用响应格式

| 状态 | 格式 |
|------|------|
| 成功 | `{"code": 200, "data": {...}, "msg": "success"}` |
| 失败 | `{"code": 400/401/500, "msg": "错误描述"}` |

### 1. AI 穿搭推荐（衣橱内组合）

**POST** `/api/v1/outfit/recommend`

```bash
curl -X POST http://localhost:8080/api/v1/outfit/recommend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"scene": "commute", "wardrobeIds": [1, 2, 4]}'
```

**Request:**
```json
{
  "scene": "commute",
  "wardrobeIds": [1, 2, 4]
}
```

场景枚举：`commute` | `date` | `casual` | `sports` | `party`

**Response:**
```json
{
  "code": 200,
  "data": {
    "id": "uuid",
    "name": "简约通勤风",
    "description": "白色衬衫搭配卡其色休闲裤...",
    "scene": "通勤",
    "matchRate": 92,
    "reason": "阴天24°C通勤场景下...",
    "image": "",
    "selectedItems": [1, 2],
    "weatherSummary": "阴，24°C",
    "toolSummary": ["get_weather: ...", "search_wardrobe: ..."],
    "generatedBy": "langchain-agent"
  },
  "msg": "success"
}
```

### 1.1 AI 单品推荐 (新购) 🆕

**POST** `/api/v1/recommend/items`

```bash
curl -X POST http://localhost:8080/api/v1/recommend/items \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"scene": "commute", "gapFocus": "outerwear"}'
```

**Request:**
```json
{ "scene": "commute", "gapFocus": "outerwear" }
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `scene` | 是 | commute / date / casual / sports / party |
| `gapFocus` | 否 | top / bottom / outerwear / shoes / accessory, 重点补的品类 |

**Response:**
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
        "priority": 92,
        "status": "pending"
      }
    ],
    "scene": "通勤",
    "weatherSummary": "阴，24°C",
    "generatedBy": "langchain-agent"
  },
  "msg": "success"
}
```

**持久化**：所有推荐自动写入 `shopping_recommendations` (status=pending)。

### 1.2 AI 推荐 + 嵌入搭配 🆕

**POST** `/api/v1/recommend/items/with-outfit`

**Request:**
```json
{ "scene": "date" }
```

**Response (节选):**
```json
{
  "code": 200,
  "data": {
    "outfit": {
      "name": "约会清新搭配",
      "matchRate": 88,
      "slots": [
        { "category": "top", "name": "白T恤", "need_buy": false, "wardrobe_id": 1, "image": "/static/garments/xxx.webp" },
        { "category": "shoes", "name": "小白鞋", "need_buy": true, "reason": "衣橱没有白色板鞋" }
      ]
    },
    "generatedBy": "langchain-agent"
  },
  "msg": "success"
}
```

`slot.need_buy=true` 的项是 AI 建议新购的单品；`false` 是衣橱已有。

### 1.3 推荐状态管理 🆕

**PATCH** `/api/v1/recommend/items/{id}`

```bash
curl -X PATCH http://localhost:8080/api/v1/recommend/items/{id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"status": "bought"}'
```

`status` 枚举：`pending` | `bought` | `dismissed` | `wishlist`

### 1.4 推荐历史列表 🆕

**GET** `/api/v1/recommend/items?status=pending&limit=20&offset=0`

返回当前用户的历史推荐，按 created_at desc 排序。

### 1.5 衣橱缺口报告 🆕

**POST** `/api/v1/recommend/gap-analysis`

**Response:**
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

### 2. 每日穿搭小贴士

**GET** `/api/v1/daily-tips/`

```bash
curl http://localhost:8080/api/v1/daily-tips/ \
  -H "Authorization: Bearer {token}"
```

**Response:**
```json
{
  "tip": {
    "tip": "今天多云22°C，建议穿轻薄外套...",
    "weather_summary": "多云，22°C",
    "wardrobe_items_considered": 5,
    "generated_by": "langchain-agent",
    "tool_summary": ["get_weather: ..."]
  },
  "user_id": 1
}
```

### 3. 衣服上传

**POST** `/api/v1/garments/upload`

Multipart form，支持 AI 检测 + 自动标签 + rembg 去背景。

### 4. 衣服列表

**GET** `/api/v1/garments/`

返回用户真实衣橱数据（数据库查询）。

### 5. 用户认证

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/auth/register` | POST | 注册，自动创建用户档案 |
| `/api/v1/auth/login` | POST | 登录，返回 HMAC JWT |

### 6. 用户资料

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/user/me` | GET | 获取资料（含衣橱数量） |
| `/api/v1/user/me` | PATCH | 更新资料（display_name, style_preference, location） |

---

## 认证机制

使用自定义 HMAC-signed token（非标准 JWT）：
- `create_access_token(user_id, username)` → base64 payload + HMAC-SHA256
- `decode_access_token(token)` → 验证签名和过期时间
- `get_current_user` / `require_user` 依赖项注入到路由

---

## 开发指南

### 添加新工具

在 `StylingAgentService` 中新增方法：

```python
def _my_tool(self, user_id: int):
    @tool
    async def my_tool(query: str) -> str:
        """Tool description for LLM."""
        result = await self.some_repo.query(user_id, query)
        return json.dumps({"result": result}, ensure_ascii=False)
    return my_tool
```

然后在 `_build_outfit_tools()` 或 `_build_daily_tip_tools()` 中注册即可。

### 调试 Agent

设置 `DEBUG=true` 后，AgentExecutor 会以 `verbose=True` 运行，在控制台输出完整推理链：

```
> Entering new AgentExecutor chain...
> Invoking: `get_weather` with `{"city": "深圳"}`
> Finished chain.
```

### 切换 LLM 提供商

- 填 `DEEPSEEK_API_KEY` → 自动使用 DeepSeek
- 不填 DeepSeek 但填 `LLM_API_KEY` + `LLM_API_BASE` → 使用 generic OpenAI-compatible
- 两者都不填 → 所有 Agent 调用自动 fallback

---

## 与数据库模块的关系

后端通过 `db` 包（项目根目录的 `db/`）访问数据库，不直接操作 SQLAlchemy：

```python
from db import get_db, UserRepository, ClothesRepository
```

- `get_db()` 是 FastAPI 依赖，yield `AsyncSession`，自动 commit/rollback
- 所有 Repository 接收 `AsyncSession` 作为构造参数

详见 [db/README.md](../db/README.md)。
