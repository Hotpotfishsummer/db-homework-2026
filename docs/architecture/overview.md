# 架构概述

## 系统组件

```
┌─────────────────────────────────────────────────────────────┐
│                    Vue 3 SPA (frontend/)                    │
│        Pinia stores + Vue Router + AI 搭配 / AI 推荐        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP JSON
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI (backend/)                        │
│  app/api/v1/ (outfit, recommendation, garments, user)       │
│  app/services/ (StylingAgent + RecommendationAgent)         │
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
