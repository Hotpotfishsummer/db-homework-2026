# L-Wardrobe — AI 穿搭推荐系统

前后端分离的 AI 穿搭推荐应用，核心功能是根据天气 + 用户衣橱生成场景化穿搭方案。

- **前端**：Vue 3 + Pinia + Vue Router + Vite
- **后端**：FastAPI + 和风天气 API + DeepSeek API
- **数据库**：待接入（当前为 stub/mock）

---

## 目录结构

```text
.
├── backend/
│   ├── app/
│   │   ├── api/v1/         # API 路由
│   │   ├── core/           # 配置（pydantic-settings）+ 认证占位
│   │   ├── models/         # Pydantic schemas
│   │   ├── services/       # 业务逻辑
│   │   │   ├── weather.py      # 和风天气 API
│   │   │   ├── outfit_ai.py    # DeepSeek 穿搭推荐
│   │   │   ├── wardrobe_stub.py # 衣橱查询接口（待接入数据库）
│   │   │   ├── vision.py       # 图片上传 + rembg 背景去除
│   │   │   └── ai.py           # 每日小贴士（stub）
│   │   └── static/         # 图片存储（raw + processed）
│   ├── tests/
│   ├── main.py             # FastAPI 入口
│   ├── .env                # 环境变量（API key 等）
│   ├── .env.example
│   ├── requirements.txt
│   └── environment.yml
└── frontend/
    ├── src/
    │   ├── views/          # 页面级组件
    │   ├── components/     # 复用组件
    │   ├── stores/         # Pinia 状态管理
    │   ├── services/       # API 客户端
    │   └── router/         # Vue Router
    ├── vite.config.js
    └── package.json
```

---

## 环境变量

复制 `backend/.env.example` 为 `backend/.env`，填入以下内容：

```bash
# 和风天气（必填，否则天气 fallback）
HEFENG_API_KEY=your_hefeng_api_key
HEFENG_API_HOST=your_host.re.qweatherapi.com

# DeepSeek（必填，否则 AI fallback）
DEEPSEEK_API_KEY=sk-your_key

# 数据库（待接入）
DATABASE_URL=sqlite:///./wardrobe.db

# 应用
DEBUG=true
```

---

## 启动方式

### 后端

```bash
cd backend
conda activate l-wardrobe      # 或 conda create -f environment.yml
python main.py --port 8080
```

- API 文档：`http://localhost:8080/docs`
- DEBUG=true 时自动热重载

### 前端

```bash
cd frontend
npm install
npm run dev
```

- 默认端口 5173（Vite）
- API 基地址：`http://localhost:8080/api`（在 `src/services/api.js` 中配置）

---

## 后端 API 文档

### 通用响应格式

| 状态 | 格式 |
|------|------|
| 成功 | `{"code": 200, "data": {...}, "msg": "success"}` |
| 失败 | `{"code": 400/401/500, "msg": "错误描述"}`（待统一） |

### 1. AI 穿搭推荐（核心）

**POST** `/api/v1/outfit/recommend`

**Headers：**
```
Content-Type: application/json
Authorization: Bearer {token}
```

**Request Body：**
```json
{
  "scene": "commute",       // 场景: commute/date/casual/sports/party
  "wardrobeIds": [1, 2, 4]  // 可用衣服 ID 列表
}
```

**Response：**
```json
{
  "code": 200,
  "data": {
    "id": "uuid",
    "name": "简约通勤风",
    "description": "白色衬衫搭配卡其色休闲裤...",
    "scene": "通勤",
    "matchRate": 92,
    "reason": "阴天24°C通勤场景下，白色衬衫清爽透气...",
    "image": ""
  },
  "msg": "success"
}
```

**流程：**
1. 根据 `wardrobeIds` 查询衣橱（目前 stub，见下方数据库待办）
2. 查询天气（深圳，目前写死，待从用户 profile 读取）
3. 调用 DeepSeek 生成推荐
4. 返回 `{code, data, msg}` 格式

**Fallback：** 若 API key 未填或调用失败，返回模板化数据，不抛异常。

---

### 2. 衣服图片上传

**POST** `/api/v1/garments/upload`

**Headers：**
```
Content-Type: multipart/form-data
Authorization: Bearer {token}
```

**Form Data：**
```
image: <文件>
```

**Response：**
```json
{
  "user_id": "...",
  "filename": "...",
  "processed": {
    "raw_path": "app/static/raw/xxx.jpg",
    "processed_path": "app/static/processed/no_bg_xxx.jpg",
    "bg_removed": true
  }
}
```

---

### 3. 衣服列表

**GET** `/api/v1/garments/`

**Headers：**
```
Authorization: Bearer {token}
```

**Response：**
```json
{
  "garments": [],
  "user_id": "..."
}
```

> **TODO：** 当前返回空数组，待接入数据库查询。

---

### 4. 用户信息

**GET** `/api/v1/user/me`

**Response：**
```json
{
  "user_id": "...",
  "role": "member",
  "wardrobe_count": 0
}
```

> **TODO：** `wardrobe_count` 硬编码为 0，待从数据库统计。

**PATCH** `/api/v1/user/me`

> **TODO：** 当前不接收 body、不更新数据，仅返回 `{"status": "ok"}`。

---

### 5. 每日小贴士

**GET** `/api/v1/daily-tips/`

**Response：**
```json
{
  "tip": {
    "tip": "Layer a light cardigan...",
    "weather_summary": null,
    "wardrobe_items_considered": 0,
    "generated_by": "stub"
  },
  "user_id": "..."
}
```

> **TODO：** 当前为随机 demo tip，待接入天气 + 衣橱 + LLM。

---

## 前端对接指南

### API 地址

`frontend/src/services/api.js` 中默认基地址：
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'
```

### 认证

当前阶段：后端 `security.py` 为 placeholder，任意 Bearer token 都返回 `user_001`。前端传 `localStorage.getItem('token')` 即可。

### 场景枚举（前后端必须一致）

| 前端值 | 后端值 | 中文 |
|--------|--------|------|
| commute | commute | 通勤 |
| date | date | 约会 |
| casual | casual | 休闲 |
| sports | sports | 运动 |
| party | party | 派对 |

### 当前前端调用的后端接口

| 前端文件 | 调用接口 | 状态 |
|----------|----------|------|
| `services/outfit.js` | `POST /outfit/recommend` | 已对接 |
| `services/outfit.js` | `GET /outfit/{id}/reason` | 死代码，未调用 |

### 前端本地 Mock（暂未调后端）

以下功能目前纯前端实现，后续需逐步对接后端：

| 功能 | 前端实现 | 需后端接口 |
|------|----------|-----------|
| 登录/注册 | `stores/auth.js` + localStorage | `POST /auth/login`, `POST /auth/register` |
| 衣橱 CRUD | `stores/wardrobe.js` | `GET/POST/DELETE /garments` |
| 用户资料 | `stores/user.js` + localStorage | `GET/PATCH /user/me` |
| 收藏/历史 | `stores/user.js`（内存，刷新丢失）| 持久化接口 |
| 每日小贴士 | 未调用 | `GET /daily-tips` |

---

## 数据库开发者指南（TODO 清单）

以下位置标注了数据库接入点，替换 stub 即可：

### 1. 衣橱查询

**文件：** `backend/app/services/wardrobe_stub.py`

**接口：**
```python
async def get_by_ids(self, user_id: str, ids: list[int]) -> list[dict]:
```

**当前：** 返回 6 件 demo 衣服。

**期望：** 接入 ORM 后，根据 `user_id` + `ids` 查询数据库，返回：
```python
[
  {"id": 1, "name": "白色衬衫", "category": "上装", "color": "#FFFFFF", "image_url": "..."},
  ...
]
```

### 2. 用户位置

**文件：** `backend/app/api/v1/outfit.py:24`

**当前：**
```python
weather = await weather_svc.get_current(location="深圳")
```

**期望：** 从数据库读取用户 profile 中的 `location` 字段，动态传入。

### 3. 衣服列表

**文件：** `backend/app/api/v1/garments.py:26`

**当前：** 返回 `{"garments": [], "user_id": ...}`

**期望：** 查询数据库返回该用户的所有衣服。

### 4. 用户资料

**文件：** `backend/app/api/v1/user.py`

**当前：** `GET /me` 硬编码，`PATCH /me` 不接收 body。

**期望：** `GET` 查数据库返回完整 profile；`PATCH` 接收 body 并更新。

### 5. 每日小贴士

**文件：** `backend/app/services/ai.py`

**当前：** 随机返回 demo tip。

**期望：** 调用天气 API + 查询衣橱 + LLM 生成真实推荐。

---

## 技术栈版本

| 组件 | 版本 |
|------|------|
| Python | 3.12 |
| FastAPI | >=0.110.0 |
| Vue | 3.2.13 |
| Vite | 最新 |
| Pinia | 3.0.4 |
| rembg | >=2.0.50 |

---

## Git 工作流

详见 `CONTRIBUTING.md`。核心规范：

- 分支命名：`features/xxx`, `bug-fix/xxx`
- Commit 格式：`type: subject`（feat/fix/docs/style/refactor/test/chore）
- PR 合并：Squash and merge
- 同步：`git rebase main`
