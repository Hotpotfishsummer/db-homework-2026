# Database 模块

## 概述

独立的 PostgreSQL 异步数据库层，当前主线以本地 PostgreSQL 为默认接入方式，Neon 等云数据库方案仅作为兼容保留。数据库连接、迁移和运行时配置统一围绕 `backend/.env` 管理。

## 环境配置

建议先复制 `backend/.env.example` 为 `backend/.env`，然后配置数据库连接：

```bash
# 本地 PostgreSQL（推荐）
DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/l_wardrobe

# Neon / 云数据库（兼容保留）
# DATABASE_URL=postgresql://<user>:<password>@<host>/<dbname>?sslmode=require&channel_binding=require
```

数据库相关依赖已统一放入 [backend/environment.yml](../../backend/environment.yml)。

## 数据库初始化

目标数据库需要先存在，然后执行迁移完成建表与初始化：

```bash
alembic -c db/alembic.ini upgrade head
```

如果需要查看当前迁移版本，可以执行：

```bash
alembic -c db/alembic.ini current
```

## 日常迁移

```bash
# 生成新迁移
alembic -c db/alembic.ini revision --autogenerate -m "describe change"

# 应用迁移
alembic -c db/alembic.ini upgrade head

# 回滚一个版本
alembic -c db/alembic.ini downgrade -1
```

## 详细说明

模型、Repository、迁移环境和连接兼容逻辑的后续细节，统一参考 [db/README.md](../../db/README.md)。