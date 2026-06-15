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
## 4. AI 搭配流程 (现有)

```
HomeView "AI 搭配" Tab / OutfitMatchView
        │  { scene, weather, wardrobeIds }
        ▼
POST /api/v1/outfit/recommend
        │
        ▼
StylingAgentService.recommend_outfit()
        │
        ├─ _can_use_agent() 检查 LLM API key
        │     └─ 缺失 → 立即 _fallback_outfit()
        │
        ├─ _build_outfit_tools() 组装 8 个工具
        │     └─ get_weather / search_wardrobe / get_wardrobe_items_by_ids
        │        count_wardrobe_items / get_user_profile / get_history_recommendations
        │        get_style_rules / save_recommendation
        │
        ├─ create_react_agent(llm, tools, prompt=_prompt_callable).ainvoke()
        │     ├─ LLM → get_user_profile → 获取 location
        │     ├─ LLM → get_weather → 查询天气
        │     ├─ LLM → search_wardrobe(category="top", season="summer")
        │     ├─ LLM → get_wardrobe_items_by_ids([...])
        │     ├─ LLM → get_history_recommendations → 去重
        │     └─ LLM → save_recommendation → 写入 outfit_recommendations
        │
        ├─ _normalize_outfit_result() 解析 JSON + enrich selectedItems
        │
        └─ 返回 {code, data: {id, name, matchRate, selectedItems, ...}, msg}
```

**约束**:`selectedItems` 中的 item_id 必须是用户 `wardrobe_items` 表中真实存在的 ID。

## 5. AI 推荐流程 (新增)

### 5.1 单品推荐 (新购)

```
HomeView "AI 推荐" Tab → 选择 "🛍️ 单品推荐" 模式
        │  { scene, weather, gapFocus? }
        ▼
POST /api/v1/recommend/items
        │
        ▼
RecommendationAgentService.recommend_items()
        │
        ├─ _can_use_agent() 检查
        │     └─ 缺失 → _fallback_items() 模板返回
        │
        ├─ _build_recommendation_tools() 组装 7 个工具
        │     └─ 通用 6 个 + analyze_wardrobe_gap (recommend 专属)
        │
        ├─ create_react_agent().ainvoke()
        │     ├─ LLM → get_user_profile (位置 + style_preference)
        │     ├─ LLM → get_weather
        │     ├─ LLM → analyze_wardrobe_gap (衣橱分类统计)
        │     ├─ LLM → count_wardrobe_items / search_wardrobe (查重 + 风格匹配)
        │     └─ LLM 输出 5-8 件新单品
        │
        ├─ 持久化到 shopping_recommendations (status=pending)
        │
        └─ 返回 {code, data: {items: [...], scene, weatherSummary, generatedBy}, msg}
```

**新表字段**:`name / category / color / style_tags / price_range / purchase_url / reason / priority / status / created_at`

### 5.2 嵌入"需购"的搭配

```
HomeView "AI 推荐" Tab → 选择 "👔 搭配方案" 模式
        │  { scene, weather }
        ▼
POST /api/v1/recommend/items/with-outfit
        │
        ▼
RecommendationAgentService.recommend_with_wardrobe()
        │
        ├─ 步骤同 5.1, 但提示词要求输出完整 outfit (4-5 slot)
        │     └─ slot.need_buy = true 表示该单品不在用户衣橱中, 需新购
        │     └─ slot.need_buy = false 表示是衣橱已有单品
        │
        ├─ 前端在 ShoppingOutfitCard 中:
        │     └─ need_buy=true 的 slot 虚线边框 + 🛒 角标
        │
        └─ 返回 {code, data: {outfit: {slots: [...]}, scene, ...}, msg}
```

### 5.3 衣橱缺口报告

```
HomeView "AI 推荐" Tab → 选择 "📊 衣橱体检" 模式
        │
        ▼
POST /api/v1/recommend/gap-analysis
        │
        ▼
RecommendationAgentService.analyze_wardrobe_gap()
        │
        ├─ 直接调用 internal 工具 (不通过 LLM ReAct 循环):
        │     └─ 按 category 维度统计: 数量 / 主色 / 风格覆盖
        │     └─ 与场景需求对比, 找出"缺什么 / 缺几件 / 建议补什么"
        │
        ├─ LLM 二次润色: 提示词要求输出结构化报告
        │
        └─ 返回 {code, data: {report: {gaps: [{category, current, suggested, advice}], summary, generatedBy}}, msg}
```

### 5.4 推荐状态管理

```
用户操作 ShoppingItemCard 按钮
        │
        ├─ ✅ 已买 → PATCH /api/v1/recommend/items/{id}  body={status: "bought"}
        ├─ ❌ 不需要 → PATCH /api/v1/recommend/items/{id}  body={status: "dismissed"}
        └─ 📌 心愿单 → (后续) PATCH /api/v1/recommend/items/{id}  body={status: "wishlist"}
        │
        ▼
ShoppingRecommendationRepository.update_status()
        │
        ▼
shopping_recommendations.status 字段更新
```
