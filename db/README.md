# AI穿搭助手 — 数据库模块

独立的 PostgreSQL 异步数据库层，提供 ORM 模型、连接管理、Repository 查询封装和 Alembic 迁移。可直接通过文件夹导入使用，无需 `pip install`。

## 环境要求

```bash
pip install sqlalchemy[asyncio]>=2.0 asyncpg>=0.29 alembic>=1.13 pydantic-settings>=2.0
```

在 `db/.env` 中配置数据库连接（文件已创建，直接修改即可）。

### Neon 云数据库配置

1. 注册 [Neon](https://neon.tech)，创建项目后会得到一个数据库
2. 在 Neon 控制台 → **Dashboard** → 点击你的项目 → **Connection Details**
3. 复制连接字符串，填入 `db/.env`：

```
DATABASE_URL=postgresql://<user>:<password>@<host>/<dbname>?sslmode=require
```

注意 Neon 连接字符串中的 `&channel_binding=require` 可以保留（`session.py` 会自动去除），`sslmode=require` 会自动转换为 asyncpg 兼容的 `ssl=require`，无需手动修改。

**Neon 免费版限制**：
- 计算时间 / 存储空间 / 分支数均有配额
- 连接池已按免费版调优（`pool_size=10, max_overflow=5`），避免超出连接数上限
- 长时间无请求后数据库会自动休眠，首次连接会有几秒冷启动延迟

### 其他 PostgreSQL（本地 / 自建 / Docker）

```
# 本地默认
DATABASE_URL=postgresql://postgres:password@localhost:5432/dbname
# Docker
DATABASE_URL=postgresql://postgres:password@host.docker.internal:5432/dbname
```

## 首次部署 / 换数据库初始化

项目不会在启动时自动建表。部署到新数据库时，跑一条命令即可完成所有建表工作：

```bash
alembic -c db/alembic.ini upgrade head
```

这会将已有迁移按顺序全部应用，得到完整的当前表结构。唯一的前提是 **目标 database 已存在**——迁移只管理表和字段，不会自动创建 database 本身。Neon 等云数据库通常已经在控制台创建好了 database，所以直接运行命令就行。

## 目录结构

```
db/
├── __init__.py                     # 公开 API 入口
├── base.py                         # SQLAlchemy DeclarativeBase 基类
├── session.py                      # 异步引擎 + 连接池 + get_db 依赖
├── alembic.ini                     # Alembic 配置文件
├── alembic                         # → 指向 alembic 的符号链接
├── README.md                       # 本文件
├── models/                         # ORM 模型（4 张表）
│   ├── user.py                     # users 表
│   ├── wardrobe_item.py            # wardrobe_items 表（支持 JSONB）
│   ├── outfit_recommendation.py    # outfit_recommendations 表（双 JSONB）
│   └── tryon_result.py             # tryon_results 表
├── repositories/                   # Repository 查询层（21 个方法）
│   ├── user_repo.py                # UserRepository（6 个方法）
│   ├── wardrobe_repo.py            # WardrobeRepository（7 个方法）
│   ├── recommendation_repo.py      # RecommendationRepository（4 个方法）
│   └── tryon_repo.py               # TryonRepository（4 个方法）
└── migrations/                     # 数据库迁移
    ├── env.py                      # 异步迁移环境配置
    ├── script.py.mako              # 迁移脚本模板
    └── versions/                   # 已应用的迁移
        ├── c0fd52f978c6_init_schema.py          # 初始建表
        └── 2557e79f733a_add_user_profile_fields.py  # 新增用户资料字段
```

---

## 数据表详解

### 1. users — 用户信息表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `user_id` | INT | PK, 自增 | 用户唯一 ID |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL | 登录用户名 |
| `password_hash` | VARCHAR(255) | NOT NULL | 加密后的密码 |
| `display_name` | VARCHAR(100) | 可选 | 用户昵称 / 显示名 |
| `style_preference` | VARCHAR(200) | 可选 | 穿搭风格偏好，如"休闲""商务" |
| `location` | VARCHAR(100) | 可选 | 所在城市，用于天气 API 查询 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 注册时间 |

关联关系：一个用户拥有多个衣橱物品、多条穿搭推荐、多条试穿记录。删除用户时联级删除所有关联数据。

### 2. wardrobe_items — 衣橱表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `item_id` | INT | PK, 自增 | 衣物唯一 ID |
| `user_id` | INT | FK → users, CASCADE | 归属用户 |
| `image_url` | VARCHAR(255) | NOT NULL | 图片在服务器上的路径 |
| `category` | VARCHAR(50) | 可选 | 分类：top（上装）、bottom（下装）、dress（连衣裙）、shoes（鞋子）等 |
| `attributes` | JSONB | 可选 | 灵活属性，如 `{"color":"red","season":"summer","style":"casual"}` |
| `created_at` | TIMESTAMPTZ | NOT NULL | 上传时间 |

### 3. outfit_recommendations — 穿搭推荐表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `recommend_id` | INT | PK, 自增 | 推荐唯一 ID |
| `user_id` | INT | FK → users, CASCADE | 归属用户 |
| `weather_context` | JSONB | 可选 | 生成推荐时的天气快照，如 `{"temp":28,"condition":"晴天","humidity":65}` |
| `analysis_doc` | TEXT | NOT NULL | LLM 生成的穿搭建议文本 |
| `selected_items` | JSONB | 可选 | 推荐搭配的衣物 ID 数组，如 `[1,3,7]` |
| `created_at` | TIMESTAMPTZ | NOT NULL | 生成时间 |

### 4. tryon_results — 虚拟试穿结果表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `tryon_id` | INT | PK, 自增 | 记录唯一 ID |
| `user_id` | INT | FK → users, CASCADE | 归属用户 |
| `base_image_url` | VARCHAR(255) | NOT NULL | 用户原始照片路径 |
| `result_image_url` | VARCHAR(255) | NOT NULL | AI 合成后的效果图路径 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 生成时间 |

> 所有外键均设置 `ON DELETE CASCADE`，删除用户时自动清理其全部衣橱、推荐和试穿数据。

---

## Repository API 参考

所有 Repository 方法均为异步（`async def`），接收 `AsyncSession` 作为构造参数。以下用 `→` 标注返回值类型。

### UserRepository — 用户管理

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `create` | `username: str, password_hash: str` | `→ User` | 注册新用户 |
| `get_by_id` | `user_id: int` | `→ User \| None` | 按 ID 查找用户 |
| `get_by_username` | `username: str` | `→ User \| None` | 按用户名查找用户 |
| `update` | `user_id: int, **fields` | `→ User \| None` | 更新用户任意字段，如 `display_name="小明"` |
| `delete` | `user_id: int` | `→ None` | 删除用户及全部关联数据 |
| `exists` | `user_id: int` | `→ bool` | 检查用户是否存在 |

### WardrobeRepository — 衣橱管理

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `create` | `user_id, image_url, category=None, attributes=None` | `→ WardrobeItem` | 添加一件衣物 |
| `get_by_id` | `item_id: int` | `→ WardrobeItem \| None` | 按 ID 查询单件 |
| `get_by_ids` | `user_id: int, ids: list[int]` | `→ list[WardrobeItem]` | 批量查询，SQL: `WHERE item_id IN (...)` |
| `list_by_user` | `user_id, *, category, season, color, limit=20, offset=0` | `→ list[WardrobeItem]` | 列表查询 + JSONB 筛选，按创建时间倒序 |
| `get_image_path` | `item_id: int` | `→ str \| None` | 只取图片路径，不加载全部字段 |
| `delete` | `item_id: int` | `→ str \| None` | 删除衣物，返回图片路径供调用方删文件 |
| `count_by_user` | `user_id: int` | `→ int` | 统计用户衣橱总数 |

### RecommendationRepository — 推荐管理

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `create` | `user_id, weather_context, analysis_doc, selected_items=None` | `→ OutfitRecommendation` | 保存一条穿搭推荐 |
| `get_by_id` | `rec_id: int` | `→ OutfitRecommendation \| None` | 按 ID 查询 |
| `list_by_user` | `user_id, *, limit=20, offset=0` | `→ list[OutfitRecommendation]` | 推荐历史，按时间倒序 |
| `delete` | `rec_id: int` | `→ None` | 删除一条推荐 |

### TryonRepository — 试穿管理

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `create` | `user_id, base_image_url, result_image_url` | `→ TryonResult` | 保存试穿结果 |
| `get_by_id` | `tryon_id: int` | `→ TryonResult \| None` | 按 ID 查询 |
| `list_by_user` | `user_id, *, limit=20, offset=0` | `→ list[TryonResult]` | 试穿历史，按时间倒序 |
| `delete` | `tryon_id: int` | `→ tuple[str, str] \| None` | 删除记录，返回 `(base图路径, 结果图路径)` 供清理 |

---

## 使用示例

### 导入

```python
from db import (User, WardrobeItem, get_db, async_session,
                UserRepository, WardrobeRepository)
```

### FastAPI 路由中使用

```python
from fastapi import APIRouter, Depends
from db import get_db, UserRepository, WardrobeRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/wardrobe", tags=["衣橱"])

@router.get("/")
async def my_wardrobe(user=Depends(require_user), db: AsyncSession = Depends(get_db)):
    """获取我的衣橱列表"""
    repo = WardrobeRepository(db)
    items = await repo.list_by_user(int(user["user_id"]))
    return {"garments": items, "count": len(items)}

@router.get("/filter")
async def filter_wardrobe(category: str | None = None, season: str | None = None,
                          color: str | None = None, user=Depends(require_user),
                          db: AsyncSession = Depends(get_db)):
    """按条件筛选衣橱"""
    repo = WardrobeRepository(db)
    items = await repo.list_by_user(int(user["user_id"]),
                                     category=category, season=season, color=color)
    return {"garments": items, "count": len(items)}

@router.patch("/me")
async def update_profile(body: dict, user=Depends(require_user),
                         db: AsyncSession = Depends(get_db)):
    """更新用户资料"""
    repo = UserRepository(db)
    updated = await repo.update(int(user["user_id"]), **body)
    return {"user_id": updated.user_id, "display_name": updated.display_name}
```

### 独立脚本中使用（非 FastAPI）

```python
import asyncio
from db.session import async_session
from db.repositories import UserRepository, WardrobeRepository

async def main():
    async with async_session() as s:
        ur = UserRepository(s)
        wr = WardrobeRepository(s)

        # 创建用户
        u = await ur.create("alice", "hashed_password_here")
        await ur.update(u.user_id, display_name="Alice", location="深圳")

        # 添加入衣物
        await wr.create(u.user_id, "/static/images/shirt_no_bg.png",
                        category="top",
                        attributes={"color": "white", "season": "summer", "style": "casual"})

        # 查询夏季衣物
        items = await wr.list_by_user(u.user_id, season="summer")
        print(f"Alice 的夏季衣物: {len(items)} 件")

        await s.commit()

asyncio.run(main())
```

### JSONB 灵活查询

```python
# 按季节筛选
items = await repo.list_by_user(user_id, season="summer")
# SQL: WHERE attributes @> '{"season":"summer"}'

# 按颜色筛选
items = await repo.list_by_user(user_id, color="red")

# 组合筛选：红色 + 夏季 + 上装
items = await repo.list_by_user(user_id, category="top", season="summer", color="red")

# 批量按 ID 查询
items = await repo.get_by_ids(user_id, [1, 5, 12])
# SQL: WHERE user_id = ? AND item_id IN (1, 5, 12)
```

### 删除衣物并清理图片文件

```python
import os

path = await wardrobe_repo.delete(item_id)
if path and os.path.exists(path):
    os.remove(path)
```

---

## 数据库迁移

### 已有迁移

| 迁移 ID | 说明 |
|---------|------|
| `c0fd52f978c6` | 初始建表 — 创建 users / wardrobe_items / outfit_recommendations / tryon_results 四张表 |
| `2557e79f733a` | 新增用户资料字段 — 添加 display_name / style_preference / location |

### 日常操作

```bash
# 生成新迁移（自动检测模型变化）
alembic -c db/alembic.ini revision --autogenerate -m "描述你的改动"

# 应用迁移到最新版本
alembic -c db/alembic.ini upgrade head

# 回滚一个版本
alembic -c db/alembic.ini downgrade -1

# 查看当前版本
alembic -c db/alembic.ini current

# 查看迁移历史
alembic -c db/alembic.ini history
```

### 工作流示例

```bash
# 1. 修改模型文件（如给 users 表加一个字段）
# 2. 生成迁移脚本
alembic -c db/alembic.ini revision --autogenerate -m "add avatar_url to users"
# 3. 检查生成的脚本是否正确
# 4. 应用到数据库
alembic -c db/alembic.ini upgrade head
# 5. 如果出问题，回滚
alembic -c db/alembic.ini downgrade -1
```

---

## 图片存储说明

数据库只存储图片路径字符串，不存二进制文件。图片文件由后端 Service 层管理：

```
app/static/
├── raw/            # 用户原始上传照片
└── processed/      # 去背景处理后的图片
```

删除记录时，Repository 的 `delete()` 方法返回图片路径，调用方负责删除物理文件：

```python
# wardrobe_repo.delete() 返回 image_url 字符串
# tryon_repo.delete() 返回 (base_image_url, result_image_url) 元组
```

---

## 连接池配置

当前配置适配 Neon 云数据库免费版：

| 参数 | 值 | 说明 |
|------|-----|------|
| `pool_size` | 10 | 常驻连接数 |
| `max_overflow` | 5 | 峰值额外连接数 |
| `echo` | False | 不打印 SQL 日志 |

URL 自动转换规则（`session.py` 中的 `_build_async_url`）：
- `postgresql://` → `postgresql+asyncpg://`
- `sslmode=require` → `ssl=require`
- 移除 `channel_binding=require`（asyncpg 不支持）

---

## 项目依赖关系

```
                          ┌──────────────┐
                          │  db/.env 文件  │
                          │ DATABASE_URL │
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │ db/session.py│  ← 读取配置, 创建引擎
                          └──────┬───────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
       ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
       │   models/   │   │repositories/│   │ migrations/ │
       │  4 张表定义  │   │ 21 个查询方法 │   │  版本管理    │
       └─────────────┘   └─────────────┘   └─────────────┘
```

数据库模块与前后端代码完全解耦，任何模块只需 `from db import ...` 即可使用。
