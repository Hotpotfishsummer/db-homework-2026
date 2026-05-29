# 数据流

## 1. 衣物上传与打标流程

```
用户上传图片
        │
        ▼
前端 POST /api/v1/garments/upload
        │
        ▼
后端先做衣物存在性识别
        │
        ├── 不包含衣物 → 直接返回识别结果，不落库
        │
        ▼
包含衣物
        │
        ▼
后端再次调用 AI，附加首次识别文字描述，生成标签
        │
        ▼
保存原始图片文件与标签 JSON 到 clothes 表
        │
        ▼
返回识别结果、标签和落库信息给前端
```

**API 请求体：**
```http
multipart/form-data
image=<file>
```

**API 响应体（识别到衣物并落库）：**
```json
{
  "contains_garment": true,
  "detection": {
    "contains_garment": true,
    "confidence": 0.98,
    "description": "A white short-sleeve shirt"
  },
  "analysis": {
    "category": "top",
    "color": "white",
    "thickness": "thin",
    "style_features": ["minimal", "casual"],
    "warmth": 0.2,
    "cooling": 0.8,
    "season": ["summer"],
    "materials": ["cotton"],
    "pattern": "solid",
    "fit": "regular",
    "tags": ["basic", "daily"],
    "summary": "A lightweight white cotton shirt"
  },
  "garment": {
    "id": 1,
    "item_id": 1,
    "user_id": 1,
    "image_url": "app/static/raw/example.jpg",
    "category": "top",
    "attributes": {
      "source_filename": "example.jpg",
      "detection": {
        "contains_garment": true,
        "confidence": 0.98,
        "description": "A white short-sleeve shirt"
      },
      "tags": {
        "category": "top",
        "color": "white",
        "thickness": "thin"
      },
      "processed_path": "app/static/processed/no_bg_example.jpg",
      "bg_removed": true
    },
    "created_at": "2026-05-29T12:00:00Z"
  }
}
```

## 2. 仅识别不落库的情况

```
用户上传图片
        │
        ▼
后端识别出图片中不包含衣物
        │
        ▼
直接返回 contains_garment=false、confidence、description
```

## 3. 数据库连接路径

```
backend/app/api/v1/garments.py
        │
        ▼
Depends(get_db)
        │
        ▼
db/session.py → create_async_engine(DATABASE_URL)
        │
        ▼
AsyncSession (asyncpg 驱动)
```