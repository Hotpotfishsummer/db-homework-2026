# Backend 模块

## 概述

FastAPI 异步 Web 服务,提供 AI 搭配 (Outfit) 和 AI 推荐 (Recommendation) 两条独立业务线,以及用户认证、衣物上传与管理、每日穿搭小贴士等基础能力。
FastAPI 默认暴露 Swagger UI 于 `/docs`,本地启动后可直接查看接口与调试请求。

## 目录结构

```
backend/
├── main.py                      # FastAPI 入口,注册所有 v1 路由
├── app/
│   ├── api/v1/                  # API 路由
│   │   ├── auth.py              # 注册/登录 (JWT)
│   │   ├── garments.py          # 衣物上传/列表/检测/删除
│   │   ├── outfit.py            # 🆕 AI 搭配 (衣橱内组合)
│   │   ├── recommendation.py    # 🆕 AI 推荐 (新购单品 + 嵌入搭配 + 缺口报告)
│   │   ├── daily_tips.py        # 每日穿搭小贴士
│   │   └── user.py              # 用户资料获取/更新
│   ├── core/                    # 配置 (pydantic-settings) + 安全 (HMAC JWT) + 日志
│   ├── models/                  # Pydantic schemas
│   ├── services/                # 业务逻辑
│   │   ├── base_agent.py        # 🆕 BaseAgentService (LLM + AgentExecutor 复用基类)
│   │   ├── styling_agent.py     # 🆕 继承 BaseAgent,只保留 outfit 专属逻辑
│   │   ├── recommendation_agent.py # 🆕 继承 BaseAgent,recommend 专属逻辑
│   │   ├── garment_vision.py    # 图片上传 + rembg 背景去除 + AI 检测打标
│   │   ├── weather.py           # 和风天气 API 封装
│   │   └── llm_health.py        # LLM API 可用性探测
│   └── static/                  # 图片存储 (raw + processed + garments)
├── requirements.txt
└── .env
```

## AI 双 Service 架构

详见 [架构概述](../architecture/overview.md#ai-双轨架构)。

`BaseAgentService` 集中处理:
- LLM 配置 (`_build_llm`, 支持 DeepSeek / OpenAI-compatible)
- Agent 执行 (`_run_agent`, 包装 `langgraph.prebuilt.create_react_agent`)
- 结果归一化 (`_extract_output_and_steps`, 适配 v0.x `{"output", "intermediate_steps"}` 契约)
- 系统提示词注入 (callable prompt, 避免 ChatPromptTemplate 把 `{name}` 解析成模板变量)
- 中间步骤摘要 (`_summarize_intermediate_steps`)

子类只需关注:
- 自己的工具集 (`_build_*_tools`)
- 自己的系统提示词 + 用户提示词 (`_*_system_prompt` / `_*_user_prompt`)
- 自己的输出归一化与 fallback (`_normalize_*_result` / `_fallback_*`)

## 服务层说明

| 文件 | 职责 | 状态 |
|------|------|------|
| `BaseAgentService` | LLM/Agent 基础设施 | 🆕 已完成 |
| `StylingAgentService` | AI 搭配: 衣橱内组合 | ✅ 已完成 |
| `RecommendationAgentService` | AI 推荐: 新购单品 + 嵌入搭配 + 缺口 | 🆕 已完成 |
| `ClothesRepository` | 衣物查询 (DB 已接入) | ✅ 已完成 |
| `garment_vision.py` | 图片上传 + rembg 背景去除 | ✅ 已完成 |
| `weather.py` | 和风天气 API | ✅ 已完成 |
| `llm_health.py` | LLM API 健康探测 | ✅ 已完成 |

## API 路由

| 端点 | 方法 | Service | 说明 |
|------|------|---------|------|
| `/api/v1/auth/register` | POST | - | 用户注册 |
| `/api/v1/auth/login` | POST | - | 用户登录 |
| `/api/v1/user/me` | GET/PATCH | - | 用户信息 |
| `/api/v1/garments/upload` | POST | `garment_vision` | 图片上传 |
| `/api/v1/garments/detect` | POST | `garment_vision` | 图片中是否包含衣物 |
| `/api/v1/garments/` | GET | `ClothesRepository` | 衣物列表 |
| `/api/v1/garments/{id}` | DELETE | `ClothesRepository` | 删除衣物 |
| `/api/v1/outfit/recommend` | POST | `StylingAgentService` | 🆕 AI 搭配 (衣橱内组合) |
| `/api/v1/recommend/items` | POST | `RecommendationAgentService` | 🆕 AI 单品推荐 (新购) |
| `/api/v1/recommend/items` | GET | `RecommendationAgentService` | 🆕 历史推荐列表 |
| `/api/v1/recommend/items/{id}` | PATCH | `RecommendationAgentService` | 🆕 更新推荐状态 |
| `/api/v1/recommend/items/with-outfit` | POST | `RecommendationAgentService` | 🆕 嵌入"需购"搭配 |
| `/api/v1/recommend/gap-analysis` | POST | `RecommendationAgentService` | 🆕 衣橱缺口报告 |
| `/api/v1/daily-tips/` | GET | `StylingAgentService` | 每日穿搭小贴士 |

## 详细文档

完整后端 API 文档见 [根目录 README](../../README.md#后端-api-文档)。本地开发时也可直接访问 `http://localhost:8000/docs`。
