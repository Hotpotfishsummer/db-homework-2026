# 架构概述

## 系统组件

```
┌─────────────────────────────────────────────────────────────┐
│                    Vue 3 SPA (frontend/)                    │
│  Pinia stores + Vue Router + AI 搭配 / AI 推荐              │
│  + 用户自带 LLM 配置 (localStorage, X-User-LLM-* 头)       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP JSON (+ 可选 X-User-LLM-* 头)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI (backend/)                        │
│  app/api/v1/ (outfit, recommendation, garments, user,       │
│               user_llm test 端点)                           │
│  app/services/ (BaseAgent + StylingAgent +                  │
│                  RecommendationAgent + VisionService)       │
│  app/core/user_llm.py (UserLLMConfig + apply_user_llm)       │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
┌──────────────┐  ┌──────────┐  ┌──────────┐
│  和风天气 API  │  │DeepSeek  │  │PostgreSQL│
│              │  │  LLM     │  │  (db/)   │
└──────────────┘  └──────────┘  └──────────┘
```

## AI 双轨架构

> 系统刻意区分了 **AI 搭配 (Outfit)** 与 **AI 推荐 (Recommendation)** 两种能力，避免概念混淆。

| 维度 | AI 搭配 (Outfit) | AI 推荐 (Recommendation) |
|------|------------------|--------------------------|
| 业务问题 | "今天穿什么" | "我还缺什么 / 要买什么" |
| 数据源 | 严格限于 `Clothes` 表 | 衣橱现状 + 风格/天气推理 |
| 输出物 | 1 套搭配 (slot = 用户已有单品) | 1) 购买单品列表 2) 嵌入"需购"的搭配 3) 衣橱缺口报告 |
| Service | `StylingAgentService` | `RecommendationAgentService` |
| 路由前缀 | `/api/v1/outfit` | `/api/v1/recommend` |
| 持久化 | `outfit_recommendations` | `shopping_recommendations` |
| 入口页 | `OutfitMatchView` + HomeView "AI 搭配" Tab | HomeView "AI 推荐" Tab |
| 共用层 | `BaseAgentService` (`_build_llm` / `_run_agent` / 通用 tool) |  ← 继承 |
| 差异化层 | outfit 专属工具 + 提示词 + 输出 JSON schema | recommendation 专属工具 + 提示词 + 输出 JSON schema |

```
            ┌───────────────────────────┐
            │   BaseAgentService        │  ← _build_llm / _run_agent / _extract_output_and_steps
            │   (app/services/base.py)  │     通用 tool: get_weather / get_user_profile / search_wardrobe
            └───────────┬───────────────┘
                        │
        ┌───────────────┴────────────────┐
        ▼                                ▼
┌────────────────────┐         ┌──────────────────────────┐
│ StylingAgentService│         │ RecommendationAgentService│
│  (outfit 专属)      │         │  (recommend 专属)         │
├────────────────────┤         ├──────────────────────────┤
│ _outfit_tools      │         │ _recommendation_tools    │
│ _outfit_prompts    │         │ _recommendation_prompts  │
│ recommend_outfit() │         │ recommend_items()        │
│ _fallback_outfit() │         │ recommend_with_wardrobe()│
│                    │         │ analyze_wardrobe_gap()   │
└────────────────────┘         └──────────────────────────┘
```

## 模块职责

| 模块 | 职责 | 入口文件 |
|------|------|----------|
| `frontend/` | UI、状态管理、AI 搭配/推荐双 Tab | `src/main.js` |
| `backend/` | REST API、双轨 AI 服务编排、图片处理 | `main.py` |
| `db/` | ORM 模型、Repository 查询、Alembic 迁移 | `session.py` |

## 关键架构决策

### AI 双轨隔离

- **数据契约不同**:`outfit.recommend` 必须只能选 `wardrobe_items` 表中真实存在的单品；`recommend.items` 允许推荐"尚未购买"的新单品
- **DB 隔离**:`outfit_recommendations` 与 `shopping_recommendations` 两张表职责互不重叠
- **共享 LLM 基础设施**:基类 `BaseAgentService` 集中处理 LLM 配置 / agent 执行 / 结果归一化，子类只关心业务差异
- **独立 fallback 链**:每个 service 都有自己的 `_fallback_*` 函数，前端调用无需感知

### 异步 SQLAlchemy 2.0

所有数据库操作均为 `async def`，使用 `asyncpg` 驱动。

## 前端状态管理

5 个 Pinia stores + 1 个新 store：

| Store | 职责 |
|-------|------|
| `auth` | 用户认证（JWT + localStorage） |
| `wardrobe` | 衣橱数据 |
| `outfit` | AI 搭配三阶段状态机 |
| `user` | 用户档案、收藏、历史 |
| `theme` | 亮/暗主题切换 |
| `recommendation` | **新**: AI 推荐三态 (单品列表 / 嵌入搭配 / 缺口报告) |

`HomeView` 顶部 Tab 切换"AI 搭配"和"AI 推荐"，分别走 `outfit` 与 `recommendation` 两个 store。

## 用户自带 LLM (User-Supplied LLM)

> 用户可配置自己的 OpenAI 兼容 LLM (base_url + api_key + model),覆盖所有 LLM 调用 — Agent 流程 (搭配 / 推荐 / 每日贴士) + 衣物打标签 (multimodal vision)。

### 关键约束

- **不持久化 server-side**:用户 key 仅在请求作用域内使用,绝不写入 DB / 日志 / 配置文件
- **仅存前端设备**:localStorage key 为 l-wardrobe.user_llm,设备本地,不跨设备同步
- **每个 LLM 请求都传头**:fetch 拦截器在 main.js 启动时安装,自动注入 3 个 X-User-LLM-* 头
- **服务端安全白名单**:is_http_url_safe() 限制 base_url 为 https:// 或任意 IPv4 (含 RFC 1918 私网),防止误传到公网第三方

### Header 协议

`
X-User-LLM-Enabled: 1              # 显式 opt-in, 防止误传头导致静默覆盖
X-User-LLM-Key:    sk-...         # 用户 key
X-User-LLM-Base:   https://...    # OpenAI 兼容端点
X-User-LLM-Model:  gpt-4o-mini    # 模型名
`

### 3 步验证流程 (前端)

1. **POST /user/llm/test-key** — 用 (api_key, base_url) 调上游 /v1/models,确认连通
2. **POST /user/llm/test-vision** — 上传客户端生成的 1x1 PNG,确认模型支持 multimodal (衣物打标场景必需)
3. **保存** — 通过验证后写入 localStorage

### 服务端处理

`
请求进入 → parse_user_llm_headers() → UserLLMConfig (含 enabled 标志)
                                ↓
                    apply_user_llm(config) context manager
                                ↓
        ┌─────────────────────┴─────────────────────┐
        │ 临时覆盖 settings.llm_api_key/base/model │
        │ (退出时自动恢复)                          │
        ↓                                           ↓
BaseAgentService._build_llm(user_llm)    VisionService.analyze_garment(user_llm)
                ↓                                       ↓
        优先 user_llm,缺则用 .env             优先 user_llm,缺则用 .env
`

### 数据流

`
HomeView (未配置)
  ↓ 💡 紫色提示卡
  ↓ '去设置' 按钮
ProfileView
  ↓ 展开 '🔑 LLM 配置' 折叠面板
  ↓ 输入 key + base URL + model
  ↓ '🔍 测试连接' → 拉取 /v1/models → 下拉菜单
  ↓ '🖼️ 测试多模态' → 上传 1x1 PNG → OK/失败
  ↓ '💾 保存' → 写入 localStorage
  ↓ 开启 '使用我自己的 LLM' 开关 → status 变 '已启用'
↓
下次任何 LLM 请求 (outfit / recommend / daily-tips / garment upload)
  ↓ fetch 拦截器读 localStorage
  ↓ 注入 X-User-LLM-* 头
  ↓ 后端识别后,LLM 调用走用户配置
  ↓ 后端日志: 'Applying user-supplied LLM for request: base_url=... model=...' (不记 key)
`

### Test 端点 (无需认证)

| 端点 | 用途 |
|------|------|
| POST /api/v1/user/llm/test-key | 用 (api_key, base_url) 调上游 /v1/models |
| POST /api/v1/user/llm/test-vision | multipart 上传 1x1 PNG, 验证多模态 |
| POST /api/v1/user/llm/models | 返回上游模型列表 (POST 非 GET 避免 key 进 uvicorn URL log) |

### 重要文件

- ackend/app/core/user_llm.py — UserLLMConfig + parse + apply context manager + is_http_url_safe
- ackend/app/api/v1/user_llm.py — 3 个 test 端点
- rontend/src/services/user_llm.js — buildUserLlmHeaders / testUserKey / testUserVision
- rontend/src/services/fetch_interceptor.js — 全局 fetch 包装,自动注入头
- rontend/src/stores/user_llm.js — Pinia store,localStorage 持久化
- rontend/src/components/profile/UserLLMSettings.vue — 折叠配置面板
- rontend/src/components/HomeViewUserLLMHint.vue — 首次引导提示卡

