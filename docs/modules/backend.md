# Backend 模块

## 概述

FastAPI 异步 Web 服务，当前只保留用户、衣物上传与图片处理相关 REST API。旧的穿搭推荐和每日小贴士接口已退役。
FastAPI 默认暴露 Swagger UI 于 `/docs`，本地启动后可直接查看接口与调试请求。

## 目录结构

```
backend/
├── main.py                  # FastAPI 入口，当前只注册 garments 和 user 两个 v1 路由
├── app/
│   ├── api/v1/              # API 路由
│   │   ├── garments.py      # 衣物上传与查询
│   │   └── user.py          # 用户管理
│   ├── core/
│   │   ├── config.py        # Pydantic 设置
│   │   └── security.py      # 认证占位
│   ├── models/
│   │   └── schemas.py       # Pydantic 请求/响应模型
│   ├── services/            # 业务逻辑
│   │   ├── garment_vision.py # 图片处理 + rembg
│   └── static/              # 图片存储
│       ├── raw/             # 原始上传
│       └── processed/       # 去背景处理
├── requirements.txt
└── .env
```

## 服务层说明

| 文件 | 职责 | 状态 |
|------|------|------|
| `ClothesRepository` | 衣物查询（DB 已接入） | 已完成 |
| `garment_vision.py` | 图片上传 + rembg 背景去除 | 已完成 |

## API 路由

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/garments/upload` | POST | 图片上传 |
| `/api/v1/garments/detect` | POST | 图片中是否包含衣物 |
| `/api/v1/garments/` | GET | 衣物列表 |
| `/api/v1/user/me` | GET/PATCH | 用户信息 |

## 后端接入待办

1. `wardrobe_stub.py` 已移除 → 使用 `ClothesRepository`（DB）
2. `garments.py` → `ClothesRepository.list_by_user()`
3. `user.py` → `UserRepository`

## 详细文档

完整后端 API 文档见 [根目录 README](../README.md#后端-api-文档)。本地开发时也可直接访问 `http://localhost:8000/docs`。