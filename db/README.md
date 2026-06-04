# AI 穿搭系统数据库模块

本目录是项目的独立 PostgreSQL 数据层，使用 SQLAlchemy 2.0、`asyncpg` 和 Alembic。

## 数据结构概览

当前基线包含 8 张表：

| 表名 | 中文含义 | 作用 |
|---|---|---|
| `users` | 用户账号表 | 保存认证信息和账号时间 |
| `user_profiles` | 用户档案表 | 保存轻量展示信息、位置和偏好数据 |
| `clothes` | 衣橱表 | 保存用户衣物和推荐筛选字段 |
| `outfit_recommendations` | 搭配推荐表 | 保存最终可回看的推荐结果 |
| `recommendation_items` | 推荐衣物关联表 | 保存推荐与衣物的关联关系及快照 |
| `outfit_favorites` | 搭配收藏表 | 保存用户收藏的推荐 |
| `outfit_history` | 搭配浏览历史表 | 保存聚合后的浏览和操作记录 |
| `daily_tips` | 每日贴士表 | 保存每日穿搭或养护建议 |

关系概览：

```text
users 1 --- 1 user_profiles
users 1 --- N clothes
users 1 --- N outfit_recommendations
outfit_recommendations N --- M clothes       (通过 recommendation_items)
users N --- M outfit_recommendations         (通过 outfit_favorites)
users N --- M outfit_recommendations         (通过 outfit_history)
users 1 --- N daily_tips
```

## 表字段说明

### `users`

| 字段名 | 中文说明 | 类型说明 |
|---|---|---|
| `user_id` | 用户主键 ID | `INTEGER`，主键，自增 |
| `username` | 用户名 | `VARCHAR(50)`，唯一，非空 |
| `password_hash` | 密码哈希 | `VARCHAR(255)`，非空 |
| `created_at` | 创建时间 | `TIMESTAMP WITH TIME ZONE`，非空 |
| `updated_at` | 更新时间 | `TIMESTAMP WITH TIME ZONE`，非空 |

### `user_profiles`

`user_profiles` 采用轻量设计，只保留当前项目真正需要长期持久化的数据。

| 字段名 | 中文说明 | 类型说明 |
|---|---|---|
| `user_id` | 用户 ID，同时作为档案主键 | `INTEGER`，主键，外键关联 `users.user_id` |
| `display_name` | 展示昵称 | `VARCHAR(100)`，可空 |
| `avatar_url` | 头像地址 | `VARCHAR(500)`，可空 |
| `bio` | 个人简介 | `VARCHAR(255)`，可空 |
| `location` | 所在地/城市 | `VARCHAR(100)`，可空 |
| `skin_tone` | 肤色信息 | `VARCHAR(50)`，可空 |
| `body_shape` | 身形信息 | `VARCHAR(50)`，可空 |
| `preferences` | 偏好聚合字段 | `JSONB`，非空，默认 `{}` |
| `updated_at` | 档案修改时间 | `TIMESTAMP WITH TIME ZONE`，非空 |

`preferences` 用于统一保存风格和颜色偏好，例如：

```json
{
  "style_preference": "casual",
  "style_axes": {
    "formalCasual": 80
  },
  "style_tags": ["clean_fit"],
  "favorite_colors": ["white", "blue"],
  "avoid_colors": ["orange"],
  "fit_preference": "regular"
}
```

兼容策略：

- `db` 层仍然接受旧字段名：`style_preference`、`style_axes`、`style_tags`、`favorite_colors`、`avoid_colors`、`fit_preference`
- 写入时会自动折叠进 `preferences`

### `clothes`

`clothes` 是 AI 推荐时的高频读取表，因此保留结构化筛选字段。

| 字段名 | 中文说明 | 类型说明 |
|---|---|---|
| `item_id` | 衣物主键 ID | `INTEGER`，主键，自增 |
| `user_id` | 所属用户 ID | `INTEGER`，外键关联 `users.user_id`，非空 |
| `name` | 衣物名称 | `VARCHAR(100)`，非空 |
| `image_url` | 衣物图片地址 | `VARCHAR(500)`，非空 |
| `category` | 衣物分类 | `VARCHAR(32)`，非空，受检查约束限制 |
| `color` | 主颜色 | `VARCHAR(50)`，可空 |
| `seasons` | 适用季节列表 | `JSONB`，非空，默认 `[]` |
| `status` | 衣物状态 | `VARCHAR(20)`，非空，默认 `available` |
| `attributes` | 扩展属性 | `JSONB`，非空，默认 `{}` |
| `created_at` | 上传时间 | `TIMESTAMP WITH TIME ZONE`，非空 |
| `deleted_at` | 软删除时间 | `TIMESTAMP WITH TIME ZONE`，可空 |

设计取舍：

- 保留 `created_at`，用于列表排序和上传时间
- 删除 `updated_at`
- 保留 `deleted_at`，用于软删除

字段策略：

- 高频筛选列：`category`、`color`、`seasons`、`status`
- 扩展属性：统一放入 `attributes` JSONB

允许的分类：

```text
top, bottom, outerwear, shoes, accessory, bag, other
```

允许的状态：

```text
available, washing
```

### `outfit_recommendations`

推荐结果属于低频回看数据，因此只保存最终结果，不保存中间推理结构。

| 字段名 | 中文说明 | 类型说明 |
|---|---|---|
| `recommend_id` | 推荐主键 ID | `UUID`，主键 |
| `user_id` | 推荐所属用户 ID | `INTEGER`，外键关联 `users.user_id`，非空 |
| `scene` | 推荐场景 | `VARCHAR(20)`，非空，受检查约束限制 |
| `weather_snapshot` | 天气快照 | `JSONB`，非空，默认 `{}` |
| `title` | 推荐标题 | `VARCHAR(150)`，非空 |
| `content` | 推荐正文/说明文案 | `TEXT`，非空，默认空字符串 |
| `match_rate` | 搭配匹配度 | `SMALLINT`，非空，默认 `0`，范围 `0-100` |
| `image_url` | 推荐结果图地址 | `VARCHAR(500)`，可空 |
| `created_at` | 创建时间 | `TIMESTAMP WITH TIME ZONE`，非空 |

允许的场景：

```text
commute, date, casual, sports, party
```

### `recommendation_items`

`recommendation_items` 用于保存一套搭配包含哪些衣物，并保留展示快照。

| 字段名 | 中文说明 | 类型说明 |
|---|---|---|
| `recommend_id` | 推荐 ID | `UUID`，联合主键，外键关联 `outfit_recommendations.recommend_id` |
| `item_id` | 衣物 ID | `INTEGER`，联合主键，外键关联 `clothes.item_id` |
| `slot` | 搭配槽位 | `VARCHAR(20)`，可空 |
| `sort_order` | 排序值 | `SMALLINT`，非空，默认 `0` |
| `item_snapshot` | 衣物快照 | `JSONB`，非空，默认 `{}` |

`item_snapshot` 通常保存：

- `name`
- `category`
- `image_url`
- `color`

这样即使衣物后续被修改或软删除，历史搭配仍然可以正确展示。

兼容策略：

- `RecommendationRepository` 仍接受旧参数 `description` 和 `reason`
- 写入时会自动合并为 `content`
- `match_rate` 写入时会限制在 `0-100`；批量写入兼容 `matchRate`

### `outfit_favorites`

| 字段名 | 中文说明 | 类型说明 |
|---|---|---|
| `user_id` | 收藏用户 ID | `INTEGER`，联合主键，外键关联 `users.user_id` |
| `recommend_id` | 被收藏推荐 ID | `UUID`，联合主键，外键关联 `outfit_recommendations.recommend_id` |
| `favorited_at` | 收藏时间 | `TIMESTAMP WITH TIME ZONE`，非空 |

### `outfit_history`

| 字段名 | 中文说明 | 类型说明 |
|---|---|---|
| `user_id` | 用户 ID | `INTEGER`，联合主键，外键关联 `users.user_id` |
| `recommend_id` | 推荐 ID | `UUID`，联合主键，外键关联 `outfit_recommendations.recommend_id` |
| `first_viewed_at` | 首次浏览时间 | `TIMESTAMP WITH TIME ZONE`，非空 |
| `last_viewed_at` | 最近浏览时间 | `TIMESTAMP WITH TIME ZONE`，非空 |
| `view_count` | 浏览次数 | `INTEGER`，非空，默认 `1` |
| `last_action` | 最近一次操作 | `VARCHAR(20)`，非空，受检查约束限制 |

允许的操作值：

```text
detail, liked, skipped
```

### `daily_tips`

`daily_tips` 用于保存用户每天的一条最终贴士，不保存额外调试字段。

| 字段名 | 中文说明 | 类型说明 |
|---|---|---|
| `tip_id` | 贴士主键 ID | `INTEGER`，主键，自增 |
| `user_id` | 用户 ID | `INTEGER`，外键关联 `users.user_id`，非空 |
| `tip_date` | 贴士日期 | `DATE`，非空 |
| `tip_type` | 贴士类型 | `VARCHAR(20)`，非空，默认 `outfit` |
| `content` | 贴士内容 | `TEXT`，非空 |
| `created_at` | 创建时间 | `TIMESTAMP WITH TIME ZONE`，非空 |

约束：

- `UNIQUE(user_id, tip_date)`，表示同一用户同一天最多只有一条贴士

允许的贴士类型：

```text
outfit, care
```

## 数据库初始化

数据库连接从 `backend/.env` 读取：

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/l_wardrobe
```

执行迁移：

```bash
alembic -c db/alembic.ini upgrade head
```

回滚到初始状态：

```bash
alembic -c db/alembic.ini downgrade base
```

当前迁移为单一基线，适合开发阶段重建数据库。

## Repository 说明

统一从 `db` 导入：

```python
from db import (
    UserRepository,
    UserProfileRepository,
    ClothesRepository,
    RecommendationRepository,
    FavoriteRepository,
    HistoryRepository,
    DailyTipRepository,
)
```

后端可调用方法：

| Repository | 方法 | 用途 |
|---|---|---|
| `UserRepository` | `create(username, password_hash, display_name=None, style_preference=None, location=None)` | 创建用户，并自动创建用户档案 |
| `UserRepository` | `get_by_id(user_id)` / `get_by_username(username)` | 查询用户 |
| `UserRepository` | `update(user_id, **fields)` | 更新账号字段或档案字段 |
| `UserRepository` | `delete(user_id)` / `exists(user_id)` | 删除用户或判断用户是否存在 |
| `UserProfileRepository` | `get_by_user_id(user_id)` / `get_or_create(user_id)` | 查询或创建用户档案 |
| `UserProfileRepository` | `update(user_id, **fields)` | 更新档案字段，偏好字段会写入 `preferences` |
| `ClothesRepository` | `create(user_id, image_url, category=None, attributes=None, ...)` | 新增衣橱单品 |
| `ClothesRepository` | `get_by_id(user_id, item_id)` / `get_by_ids(user_id, ids)` | 查询单件或多件衣物 |
| `ClothesRepository` | `list_by_user(user_id, category=None, season=None, color=None, status=None, limit=20, offset=0)` | 分页查询用户衣橱 |
| `ClothesRepository` | `update(user_id, item_id, **fields)` | 更新衣物信息 |
| `ClothesRepository` | `delete(user_id, item_id)` | 软删除衣物 |
| `ClothesRepository` | `count_by_user(user_id)` | 统计用户衣橱数量 |
| `RecommendationRepository` | `create(user_id, scene, title, content=None, description="", reason="", match_rate=0, ...)` | 保存一条最终搭配推荐 |
| `RecommendationRepository` | `create_many(user_id, scene, recommendations, weather_snapshot=None)` | 批量保存推荐 |
| `RecommendationRepository` | `get_by_id(user_id, recommend_id)` / `list_by_user(user_id, limit=20, offset=0)` | 查询推荐详情或列表 |
| `FavoriteRepository` | `add(user_id, recommend_id)` / `remove(user_id, recommend_id)` | 收藏或取消收藏推荐 |
| `FavoriteRepository` | `list_by_user(user_id, limit=20, offset=0)` | 查询用户收藏列表 |
| `HistoryRepository` | `record_action(user_id, recommend_id, action)` | 记录浏览、喜欢或跳过行为 |
| `HistoryRepository` | `list_by_user(user_id, limit=20, offset=0)` / `clear(user_id)` | 查询或清空历史记录 |
| `DailyTipRepository` | `get_for_date(user_id, tip_date)` / `get_today(user_id)` | 查询指定日期或今日贴士 |
| `DailyTipRepository` | `create_or_get(user_id, tip_date, content, tip_type="outfit")` | 创建或复用当天贴士 |
| `DailyTipRepository` | `list_by_user(user_id, limit=20, offset=0)` | 查询贴士列表 |

主要约定：

- `UserRepository.create()` 注册时自动创建空档案
- `UserRepository` 和 `UserProfileRepository` 会自动把旧偏好字段映射到 `preferences`
- `ClothesRepository` 的查询、更新和软删除都必须带 `user_id`
- `ClothesRepository.get_by_ids()` 默认只返回未删除且状态为 `available` 的衣物
- `RecommendationRepository` 只保存最终搭配结果和衣物快照
- `FavoriteRepository.add()` 自动去重
- `HistoryRepository.record_action()` 使用 PostgreSQL upsert 聚合历史记录
- `DailyTipRepository.create_or_get()` 保证同一用户同一天只保存一条贴士

## 图片存储

PostgreSQL 只保存图片 URL 和必要元数据，不保存图片二进制内容。图片文件仍由静态目录或对象存储管理。
