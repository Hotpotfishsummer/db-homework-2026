# Backend 模块

## 概述

FastAPI 异步 Web 服务，提供 AI 穿搭推荐、天气查询、图片处理等 REST API。

## 目录结构

```
backend/
├── main.py                  # FastAPI 入口，4 个 v1 路由
├── app/
│   ├── api/v1/              # API 路由
│   │   ├── garments.py      # 衣橱 CRUD
│   │   ├── user.py          # 用户管理
│   │   ├── daily_tips.py     # 每日小贴士
│   │   └── outfit.py        # AI 穿搭推荐
│   ├── core/
│   │   ├── config.py        # Pydantic 设置
│   │   └── security.py      # 认证占位
│   ├── models/
│   │   └── schemas.py       # Pydantic 请求/响应模型
│   ├── services/            # 业务逻辑
│   │   ├── weather.py       # 和风天气 API
│   │   ├── outfit_ai.py     # DeepSeek 穿搭推荐
│   │   ├── wardrobe_stub.py # 衣橱查询（待接入 DB）
│   │   ├── vision.py        # 图片处理 + rembg
│   │   └── ai.py            # 每日小贴士
│   └── static/              # 图片存储
│       ├── raw/             # 原始上传
│       └── processed/       # 去背景处理
├── requirements.txt
└── .env
```

## 服务层说明

| 文件 | 职责 | 状态 |
|------|------|------|
| `weather.py` | 和风天气 API 调用 | 已完成 |
| `outfit_ai.py` | DeepSeek LLM 穿搭生成 | 已完成 |
| `wardrobe_stub.py` | 衣橱查询（返回 demo 数据） | 待接入 DB |
| `vision.py` | 图片上传 + rembg 背景去除 | 已完成 |
| `ai.py` | 每日小贴士（随机 demo） | 待接入 DB |

## API 路由

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/outfit/recommend` | POST | AI 穿搭推荐 |
| `/api/v1/garments/upload` | POST | 图片上传 |
| `/api/v1/garments/` | GET | 衣橱列表 |
| `/api/v1/user/me` | GET/PATCH | 用户信息 |
| `/api/v1/daily-tips/` | GET | 每日小贴士 |

## 后端接入待办

详见 [根目录 README](../README.md#后端接入待办)：

1. `wardrobe_stub.py` → `WardrobeRepository`
2. 用户位置从 DB 读取（当前写死"深圳"）
3. `garments.py` → `WardrobeRepository.list_by_user()`
4. `user.py` → `UserRepository`

## 详细文档

完整后端 API 文档见 [根目录 README](../README.md#后端-api-文档)。