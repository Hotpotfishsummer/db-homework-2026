# 项目概况：AI 私人衣橱

## 项目简介
AI 驱动的穿搭推荐移动 Web 应用，支持衣橱管理、AI 搭配生成、个人风格分析。

## 技术栈
- **框架**: Vue 3.5+ (Composition API, `<script setup>`)
- **构建工具**: Vite 6
- **状态管理**: Pinia 3
- **路由**: Vue Router 4 (HTML5 history mode)
- **PWA**: vite-plugin-pwa
- **UI**: 自定义组件 + scoped CSS + CSS 变量（无第三方 UI 库）
- **语言**: 中文（简体）

## 代码架构
```
src/
  main.js              — 入口：createApp, pinia, router
  App.vue              — 根组件，CSS 变量定义，主题初始化
  router/index.js      — 路由 + 鉴权守卫
  stores/              — Pinia 状态管理
    auth.js            — 登录/注册 mock（localStorage）
    user.js            — 用户资料、收藏、历史
    wardrobe.js        — 衣橱 CRUD、分类、筛选
    outfit.js          — AI 搭配状态机
    theme.js           — 深色/浅色主题切换
  services/            — API 服务层
    api.js             — API_BASE_URL + 超时配置
    outfit.js          — AI 搭配推荐（mock + real API）
    user.js            — 头像上传、图片验证/压缩
  composables/         — 组合式函数
    useHaptics.js      — 振动反馈
  components/          — 可复用组件
    BottomNav.vue      — 底部导航栏（毛玻璃效果）
    BottomSheet.vue    — 底部弹出 sheet
    ClothingDetail.vue — 衣物详情弹窗
    biz/               — 业务组件
      SceneSelector.vue        — 场景选择器
      OutfitRecommendSection.vue — 推荐区域
      MatchFilter.vue          — 场景+天气筛选
      AIThinking.vue           — AI 加载动画
      OutfitCard.vue           — 可滑动搭配卡片
    profile/           — 个人资料子组件
      CoverSection.vue         — 封面+头像+用户信息
      BodyCardSection.vue      — 身体数据卡片
      StylePersonalitySection.vue — 风格个性
      ProfileTabs.vue          — 标签切换
      LikedOutfitsPanel.vue    — 收藏列表
      HistoryPanel.vue         — 历史列表
      AvatarModal.vue          — 头像预览
      ConfirmDialog.vue        — 确认对话框
  views/               — 页面视图
    LoginView.vue      — 登录页
    RegisterView.vue   — 注册页
    HomeView.vue       — 首页（场景标签 + 推荐卡片）
    WardrobeView.vue   — 衣橱网格
    AddClothView.vue   — 添加衣物表单
    OutfitMatchView.vue — AI 搭配流程
    OutfitDetailView.vue — 搭配详情
    LikedView.vue      — 收藏列表
    HistoryView.vue    — 浏览历史
    ProfileView.vue    — 个人主页
    ProfileEditView.vue — 编辑资料
    ProfileSettingsView.vue — 设置页
  assets/
    base.css           — CSS reset
    main.css           — 导入 base.css
```

## 文档位置
- `DESIGN.md` — Apple 设计系统规范（颜色、字体、间距、圆角、组件）
- `RULE.md` — AI 编码强制规则（500 行限制、模块接口、Fail-Fast、TDD/DDD）
- `README.md` — 项目说明
- `.ai-temp/working-log/` — 工作日志
- `.ai-temp/memory-bank/` — 本文件（长期记忆）

## 设计系统（Apple Style）
- **主色调**: `#0066cc` (Action Blue)，唯一的交互色
- **字体**: SF Pro Display/Text，负字间距（display 级别 -0.374px）
- **圆角**: 18px（卡片），9999px（pill 按钮），8px（紧凑工具）
- **阴影**: 仅用于产品图片 `rgba(0,0,0,0.22) 3px 5px 30px`，UI 元素无阴影
- **间距**: 4/8/12/17/24/32/48/80px
- **字重阶梯**: 300/400/600/700（无 500）

## 必须注意的事项
1. **单文件 ≤ 500 行**（RULE.md 强制规则）
2. **模块引用走公共接口**，禁止直引内部实现
3. **禁止兜底**，必须 Fail-Fast
4. **工作日志必须写入** `.ai-temp/working-log/[yyyymmddHHMMSS]-[内容].md`
5. **尝试文件必须写入** `.ai-temp/attempts/` 目录
6. 主色调 `#0066cc` 是唯一交互色，不要引入第二个强调色
7. Apple 设计中装饰性渐变被禁止，渐变仅用于产品图片
