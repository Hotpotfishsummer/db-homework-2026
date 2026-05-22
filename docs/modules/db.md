# Database 模块

## 概述

独立的 PostgreSQL 异步数据库层，SQLAlchemy 2.0 async ORM，提供 4 张表、21 个 Repository 方法、Alembic 迁移管理。可直接通过文件夹导入使用，无需 `pip install`。

## 快速使用

```python
from db import get_db, UserRepository, WardrobeRepository, async_session

async def example():
    async with async_session() as s:
        ur = UserRepository(s)
        wr = WardrobeRepository(s)
        # 使用...
```

## 数据表

| 表 | 用途 | 主要字段 |
|-----|------|----------|
| `users` | 用户信息 | user_id, username, password_hash, display_name, style_preference, location |
| `wardrobe_items` | 衣橱 | item_id, user_id, image_url, category, attributes (JSONB) |
| `outfit_recommendations` | 穿搭推荐 | recommend_id, user_id, weather_context (JSONB), analysis_doc, selected_items (JSONB) |
| `tryon_results` | 虚拟试穿 | tryon_id, user_id, base_image_url, result_image_url |

## Alembic 迁移

```bash
# 生成新迁移
alembic -c db/alembic.ini revision --autogenerate -m "描述"

# 应用迁移
alembic -c db/alembic.ini upgrade head

# 回滚
alembic -c db/alembic.ini downgrade -1
```

## 详细文档

完整 Repository API 参考、JSONB 查询示例、连接池配置见 [db/README.md](../../db/README.md)。