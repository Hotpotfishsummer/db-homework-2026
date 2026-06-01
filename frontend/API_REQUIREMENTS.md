# 前端接口需求文档

> **项目：** WarnMatch AI 穿搭推荐  
> **前端状态：** UI 开发基本完成，所有数据层目前使用 Mock / localStorage  
> **目标：** 对接后端 API，替换 Mock 层，实现真实数据流  
> **基础路径：** `/api/v1`  
> **认证方式：** Bearer Token（JWT），放在 `Authorization` 请求头  
> **统一响应格式：** `{ "code": 200, "msg": "...", "data": { ... } }`

---

## 一、认证模块 `/api/v1/auth`

### 1.1 用户注册

```
POST /api/v1/auth/register
```

**请求体：**
```json
{
  "username": "string",   // 必填，3-20位，字母数字下划线
  "password": "string"    // 必填，6-32位
}
```

**成功响应：**
```json
{
  "code": 200,
  "msg": "注册成功",
  "data": null
}
```

**失败响应：**
```json
{ "code": 400, "msg": "该账号已存在", "data": null }
```

**备注：**
- 注册成功后不自动登录，前端会跳转到登录页
- 用户名唯一性由后端校验

---

### 1.2 用户登录

```
POST /api/v1/auth/login
```

**请求体：**
```json
{
  "username": "string",
  "password": "string"
}
```

**成功响应：**
```json
{
  "code": 200,
  "msg": "登录成功",
  "data": {
    "token": "jwt_token_string"
  }
}
```

**失败响应：**
```json
{ "code": 400, "msg": "账号或密码错误", "data": null }
```

**备注：**
- Token 有过期时间，建议 7 天
- 前端会将 token 存入 localStorage，后续所有请求通过 `Authorization: Bearer <token>` 携带

---

## 二、衣柜模块 `/api/v1/wardrobe`

> 衣柜是 AI 推荐的数据基础。用户需要先添加衣物，才能使用搭配推荐功能。

### 2.1 获取衣物列表

```
GET /api/v1/wardrobe
Authorization: Bearer <token>
```

**成功响应：**
```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "name": "白色基础款T恤",
      "category": "top",
      "color": "#FFFFFF",
      "image": "https://cdn.example.com/cloth/1.jpg",
      "status": "available",
      "createdAt": "2026-05-20T10:00:00Z"
    }
  ]
}
```

**category 枚举值：**
| 值 | 含义 |
|------|------|
| `top` | 上装 |
| `bottom` | 下装 |
| `shoes` | 鞋靴 |
| `accessory` | 配饰 |
| `bag` | 包包 |

**status 枚举值：**
| 值 | 含义 |
|------|------|
| `available` | 可穿 |
| `washing` | 洗涤中 |

---

### 2.2 添加衣物

```
POST /api/v1/wardrobe
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：**
```json
{
  "name": "黑色西装裤",
  "category": "bottom",
  "color": "#000000",
  "image": "https://cdn.example.com/cloth/9.jpg",
  "status": "available"
}
```

**成功响应：**
```json
{
  "code": 200,
  "msg": "添加成功",
  "data": {
    "id": 9,
    "name": "黑色西装裤",
    "category": "bottom",
    "color": "#000000",
    "image": "https://cdn.example.com/cloth/9.jpg",
    "status": "available",
    "createdAt": "2026-05-27T08:30:00Z"
  }
}
```

**备注：**
- `id` 和 `createdAt` 由后端生成
- `image` 字段目前传 URL 字符串，后续可能改为图片上传接口

---

### 2.3 编辑衣物

```
PUT /api/v1/wardrobe/:id
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：** 同添加衣物，字段均为可选（只传需要修改的字段）

**成功响应：**
```json
{
  "code": 200,
  "msg": "更新成功",
  "data": { ... }
}
```

**失败响应：**
```json
{ "code": 404, "msg": "衣物不存在", "data": null }
```

---

### 2.4 删除衣物

```
DELETE /api/v1/wardrobe/:id
Authorization: Bearer <token>
```

**成功响应：**
```json
{ "code": 200, "msg": "删除成功", "data": null }
```

---

## 三、AI 搭配推荐模块 `/api/v1/outfit`

### 3.1 生成搭配推荐（核心接口）

```
POST /api/v1/outfit/recommend
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：**
```json
{
  "scene": "commute",
  "wardrobeIds": [1, 2, 3, 4, 5]
}
```

**scene 枚举值：**
| 值 | 中文含义 |
|------|------|
| `commute` | 通勤 |
| `date` | 约会 |
| `casual` | 休闲 |
| `sports` | 运动 |
| `party` | 派对 |

**成功响应：**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "outfitId": "AI-m1x2k3f0",
    "scene": "通勤",
    "matchRate": 96,
    "top": {
      "id": 1,
      "name": "白色基础款T恤",
      "image": "https://cdn.example.com/cloth/1.jpg",
      "category": "top"
    },
    "bottom": {
      "id": 3,
      "name": "黑色西裤",
      "image": "https://cdn.example.com/cloth/3.jpg",
      "category": "bottom"
    },
    "shoes": {
      "id": 5,
      "name": "白色运动鞋",
      "image": "https://cdn.example.com/cloth/5.jpg",
      "category": "shoes"
    },
    "accessory": {
      "id": 7,
      "name": "黑色公文包",
      "image": "https://cdn.example.com/cloth/7.jpg",
      "category": "bag"
    },
    "reason": "白色T恤搭配黑色西裤经典不出错，运动鞋增添活力感，公文包适合通勤场景。"
  }
}
```

**关键说明：**
- `wardrobeIds` 是用户衣柜中**可穿衣物**（status = available）的 id 列表
- 后端从这些衣物中按场景智能搭配，返回 4 件组合（上装 + 下装 + 鞋 + 配饰/包）
- `matchRate` 范围 0-100，表示搭配匹配度
- `reason` 是搭配理由的文字说明，前端会直接展示给用户
- 前端目前期望返回**单套搭配**，如果后端支持多套，建议用数组包裹

**失败响应：**
```json
{ "code": 400, "msg": "衣柜中衣物不足，无法生成搭配", "data": null }
```

---

### 3.2 获取搭配理由（可选）

```
GET /api/v1/outfit/:outfitId/reason
Authorization: Bearer <token>
```

**成功响应：**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "reason": "详细的搭配理由说明..."
  }
}
```

**备注：** 此接口目前前端未调用，属于预留。如果推荐接口已包含 reason 字段，此接口可不实现。

---

## 四、用户资料模块 `/api/v1/user`

### 4.1 获取用户资料

```
GET /api/v1/user/profile
Authorization: Bearer <token>
```

**成功响应：**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "username": "demo_user",
    "avatar": "https://cdn.example.com/avatar/1.jpg",
    "coverImage": "https://cdn.example.com/cover/1.jpg",
    "nickname": "穿搭达人",
    "bio": "每天都要精致出门",
    "gender": "male",
    "birthday": "1998-06-15",
    "height": 178,
    "weight": 70,
    "bmi": "22.1",
    "skinTone": "fair_warm",
    "bodyShape": "rectangle",
    "faceFeature": null,
    "styleAxes": {
      "minimalComplex": 35,
      "vintageModern": 60,
      "formalCasual": 45
    },
    "styleTags": ["clean_fit", "old_money"],
    "favoriteColors": ["#000000", "#FFFFFF", "#1E3A5F"],
    "avoidColors": ["#FF69B4"],
    "fitPreference": "slim"
  }
}
```

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `skinTone` | enum | `fair_cool` / `fair_warm` / `medium` / `tan` / `dark` |
| `bodyShape` | enum | `inverted_triangle` / `rectangle` / `pear` / `hourglass` / `apple` |
| `styleAxes` | object | 三个维度各 0-100，描述风格偏好 |
| `styleTags` | string[] | 风格标签，如 `old_money` `y2k` `clean_fit` `streetwear` |
| `fitPreference` | string | 版型偏好，如 `slim` / `regular` / `oversized` |

---

### 4.2 更新用户资料

```
PUT /api/v1/user/profile
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：** 与 GET 响应结构一致，只传需要更新的字段

**成功响应：**
```json
{ "code": 200, "msg": "更新成功", "data": { ... } }
```

---

### 4.3 上传头像

```
POST /api/v1/user/avatar
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**请求参数：**
| 字段 | 类型 | 说明 |
|------|------|------|
| `file` | File | JPG/PNG，最大 2MB |

**成功响应：**
```json
{
  "code": 200,
  "msg": "上传成功",
  "data": {
    "url": "https://cdn.example.com/avatar/1.jpg"
  }
}
```

**失败响应：**
```json
{ "code": 400, "msg": "只支持 JPG/PNG 格式", "data": null }
{ "code": 400, "msg": "图片大小不能超过 2MB", "data": null }
```

---

## 五、收藏与历史模块 `/api/v1/user`

### 5.1 获取收藏列表

```
GET /api/v1/user/liked
Authorization: Bearer <token>
```

**成功响应：**
```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "outfitId": "AI-m1x2k3f0",
      "scene": "通勤",
      "matchRate": 96,
      "top": { "id": 1, "name": "...", "image": "...", "category": "top" },
      "bottom": { "id": 3, "name": "...", "image": "...", "category": "bottom" },
      "shoes": { "id": 5, "name": "...", "image": "...", "category": "shoes" },
      "accessory": { "id": 7, "name": "...", "image": "...", "category": "bag" },
      "reason": "...",
      "likedAt": "2026-05-27T10:30:00Z"
    }
  ]
}
```

---

### 5.2 收藏搭配

```
POST /api/v1/user/liked
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：**
```json
{
  "outfitId": "AI-m1x2k3f0"
}
```

**成功响应：**
```json
{ "code": 200, "msg": "收藏成功", "data": null }
```

---

### 5.3 取消收藏

```
DELETE /api/v1/user/liked/:outfitId
Authorization: Bearer <token>
```

**成功响应：**
```json
{ "code": 200, "msg": "已取消收藏", "data": null }
```

---

### 5.4 获取浏览历史

```
GET /api/v1/user/history
Authorization: Bearer <token>
```

**成功响应：** 结构同收藏列表，额外包含 `viewedAt` 字段

---

### 5.5 记录浏览

```
POST /api/v1/user/history
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：**
```json
{
  "outfitId": "AI-m1x2k3f0"
}
```

---

## 六、接口汇总

| 优先级 | 方法 | 路径 | 说明 | 前端状态 |
|:---:|------|------|------|----------|
| **P0** | POST | `/api/v1/auth/register` | 注册 | 纯 Mock |
| **P0** | POST | `/api/v1/auth/login` | 登录 | 纯 Mock |
| **P0** | GET | `/api/v1/wardrobe` | 衣物列表 | 纯内存 |
| **P0** | POST | `/api/v1/wardrobe` | 添加衣物 | 纯内存 |
| **P0** | PUT | `/api/v1/wardrobe/:id` | 编辑衣物 | 纯内存 |
| **P0** | DELETE | `/api/v1/wardrobe/:id` | 删除衣物 | 纯内存 |
| **P0** | POST | `/api/v1/outfit/recommend` | AI 推荐 | 代码已写，Mock 绕过 |
| **P1** | GET | `/api/v1/user/profile` | 获取资料 | localStorage |
| **P1** | PUT | `/api/v1/user/profile` | 更新资料 | localStorage |
| **P1** | POST | `/api/v1/user/avatar` | 上传头像 | FileReader Mock |
| **P2** | GET | `/api/v1/user/liked` | 收藏列表 | 纯内存 |
| **P2** | POST | `/api/v1/user/liked` | 收藏 | 纯内存 |
| **P2** | DELETE | `/api/v1/user/liked/:id` | 取消收藏 | 纯内存 |
| **P2** | GET | `/api/v1/user/history` | 浏览历史 | 纯内存 |
| **P2** | POST | `/api/v1/user/history` | 记录浏览 | 纯内存 |
| **P3** | GET | `/api/v1/outfit/:id/reason` | 搭配理由 | 代码已写，未调用 |

---

## 七、前端对接约定

### 认证流程
1. 登录成功后，前端将 `token` 存入 `localStorage`
2. 所有需鉴权请求头携带 `Authorization: Bearer <token>`
3. 返回 `401` 时，前端清除 token 并跳转登录页

### 错误处理
- 前端统一按 HTTP 状态码 + 响应体 `code` 字段判断成功/失败
- `code === 200` 视为成功，其他为失败
- `msg` 字段直接展示给用户（中文提示）

### 跨域
- 前端开发地址 `http://localhost:5173`（Vite 默认）
- 后端需配置 CORS 允许该 origin

### Content-Type
- JSON 请求：`application/json`
- 文件上传：`multipart/form-data`

### 分页（如需）
当前前端未实现分页，如后端数据量大需要分页，建议格式：
```json
{
  "code": 200,
  "data": {
    "list": [],
    "total": 100,
    "page": 1,
    "pageSize": 20
  }
}
```
前端会按需适配。

---

## 八、后端技术建议（非强制）

| 项目 | 建议 |
|------|------|
| 框架 | FastAPI / Express / NestJS 均可 |
| 数据库 | PostgreSQL 或 MySQL |
| ORM | SQLAlchemy / Prisma / TypeORM |
| 文件存储 | 本地 / OSS / S3，返回可访问 URL |
| JWT | PyJWT / jsonwebtoken，建议 7 天过期 |
| AI 推荐 | 可接 OpenAI / Claude API 或自建模型 |
| 图片处理 | 建议后端做压缩和裁剪，返回统一尺寸 |

---

## 九、对接时间线建议

| 阶段 | 内容 | 建议周期 |
|------|------|----------|
| Phase 1 | 认证 + 衣柜 CRUD + AI 推荐 | 3-5 天 |
| Phase 2 | 用户资料 + 头像上传 | 2-3 天 |
| Phase 3 | 收藏 / 历史 | 1-2 天 |
| 联调 | 前后端联调 + 修 bug | 2-3 天 |

**总计约 8-13 个工作日。**

---

*文档由前端团队提供，如有字段调整请及时同步。*
