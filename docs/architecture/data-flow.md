# 数据流

## 1. AI 穿搭推荐流程

```
用户选择场景 + 衣物
        │
        ▼
前端 POST /api/v1/outfit/recommend
        │
        ▼
后端查询天气（和风 API，写死"深圳"）
        │
        ▼
后端调用 DeepSeek LLM 生成搭配
        │
        ▼
存储到 outfit_recommendations 表
        │
        ▼
返回搭配结果给前端
        │
        ▼
前端展示 OutfitCard 卡片
```

**API 请求体：**
```json
{
  "scene": "commute",
  "wardrobeIds": [1, 2, 3]
}
```

**API 响应体：**
```json
{
  "code": 200,
  "data": {
    "id": "uuid",
    "name": "简约通勤风",
    "description": "白色衬衫搭配卡其色休闲裤...",
    "scene": "通勤",
    "matchRate": 92,
    "reason": "阴天24°C通勤场景下..."
  }
}
```

## 2. 衣橱 CRUD 流程

```
用户上传图片
        │
        ▼
后端 rembg 去背景
        │
        ▼
存储到 app/static/processed/
        │
        ▼
写入 wardrobe_items 表（image_url 路径）
        │
        ▼
返回上传结果给前端
```

## 3. 数据库连接路径

```
backend/app/api/v1/xxx.py
        │
        ▼
Depends(get_db)
        │
        ▼
db/session.py → create_async_engine(DATABASE_URL)
        │
        ▼
AsyncSession (asyncpg 驱动)
        │
        ▼
PostgreSQL (Neon 云)
```

### 连接 URL 转换规则

`db/session.py` 自动转换：
- `postgresql://` → `postgresql+asyncpg://`
- `sslmode=require` → `ssl=require`
- 移除 `channel_binding=require`