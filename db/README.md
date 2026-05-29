# AI穿搭助手 — 数据库模块

当前版本只保留数据库启动、环境变量、迁移初始化的主干说明。模型、Repository 和更细的实现细节会继续调整，所以这里不展开，以免和代码同步成本过高。

## 环境要求

```bash
pip install sqlalchemy[asyncio]>=2.0 asyncpg>=0.29 alembic>=1.13 pydantic-settings>=2.0
```

数据库连接统一放在 `backend/.env`。

## 运行时配置

复制 `backend/.env.example` 为 `backend/.env`，然后配置数据库连接：

```bash
# 本地 PostgreSQL（推荐）
DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/l_wardrobe

# Neon / 云数据库（兼容保留）
# DATABASE_URL=postgresql://<user>:<password>@<host>/<dbname>?sslmode=require&channel_binding=require
```

如果使用 Neon 或其他云 PostgreSQL，保留原始连接串即可，代码会做 asyncpg 兼容转换。

## 数据库初始化

目标数据库需要先存在，然后再执行迁移完成建表与初始化：

```bash
alembic -c db/alembic.ini upgrade head
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

## 说明

- `db/session.py` 负责读取 `backend/.env` 中的 `DATABASE_URL` 并创建异步连接。
- `db/migrations/env.py` 负责 Alembic 的异步迁移执行。
- 模型和 Repository 会继续随业务调整，这部分文档会在代码稳定后再补齐。
