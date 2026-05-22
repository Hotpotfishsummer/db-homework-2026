# Frontend 模块

## 概述

Vue 3 移动端应用，Composition API + Pinia + Vue Router，三阶段 AI 搭配交互，Mock/真实 API 一键切换。

## 目录结构

```
frontend/src/
├── views/                   # 页面级组件（11 个）
├── components/
│   ├── biz/                # 业务组件
│   │   ├── MatchFilter.vue  # 场景/天气选择器
│   │   ├── AIThinking.vue   # 生成动画
│   │   └── OutfitCard.vue    # 搭配结果卡片
│   ├── BottomNav.vue        # 底部导航
│   ├── BottomSheet.vue      # 底部弹出
│   └── ClothingDetail.vue   # 衣服详情
├── stores/                  # Pinia 状态管理
│   ├── auth.js             # 用户认证
│   ├── outfit.js           # AI 搭配状态机
│   ├── wardrobe.js         # 衣橱数据
│   ├── user.js             # 用户档案
│   └── theme.js            # 主题管理
├── services/               # API 客户端
│   ├── api.js              # API 基地址配置
│   ├── outfit.js           # AI 搭配（USE_MOCK 切换）
│   └── user.js             # 用户服务
├── composables/
│   └── useHaptics.js       # 触觉反馈
└── router/
    └── index.js            # 路由 + 守卫
```

## 状态管理

| Store | 职责 |
|-------|------|
| `auth` | 登录/注册，localStorage Mock |
| `wardrobe` | 衣橱数据管理 |
| `outfit` | AI 搭配 INPUT → GENERATING → RESULTS 三阶段 |
| `user` | 用户档案、收藏、历史 |
| `theme` | 亮/暗主题切换 |

## USE_MOCK 切换

`frontend/src/services/outfit.js` 中：

```javascript
const USE_MOCK = true   // true = 本地 Mock, false = 真实后端
```

## AI 搭配三阶段

```
MatchFilter.vue (INPUT) → AIThinking.vue (GENERATING) → OutfitCard.vue (RESULTS)
```

## 详细文档

完整功能展示、设计原则、开发规范见 [frontend/README.md](../../frontend/README.md)。