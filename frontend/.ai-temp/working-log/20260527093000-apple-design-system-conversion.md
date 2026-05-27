# 工作日志：Apple Design System UI 转换

## 上次工作结果
- 无（本次为首次工作）

## 本次工作目标
根据 DESIGN.md 将整个前端 UI 从 teal/green 设计方案转换为 Apple 风格设计系统：
- 主色调从 `#5B9A8B` (teal) 改为 `#0066cc` (Apple Blue)
- 移除所有装饰性渐变和阴影（Apple 设计原则）
- 统一圆角体系（18px 卡片，9999px pill 按钮）
- 更新字体栈为 SF Pro Display/Text
- 将超过 500 行的文件拆分为子组件（RULE.md 合规）

## 预期结果
- 所有 18+ 个 Vue 文件的 UI 风格统一为 Apple 设计系统
- 所有文件 ≤ 500 行
- 构建成功，无编译错误
- 零残留旧颜色（teal/purple/pink）

## 实际结果
- ✅ 所有文件 UI 已转换为 Apple 设计系统
- ✅ 所有文件 ≤ 500 行（最大 480 行 OutfitDetailView）
- ✅ 构建成功（102 modules, 1.16s）
- ✅ 零残留旧颜色（grep 验证通过）
- ✅ 零残留 `var(--primary-gradient)` 引用

## 详细改动

### Phase 0: CSS 变量基础
- `src/App.vue` — 替换全部 CSS 变量为 Apple tokens，添加新变量（hairline, surface-pearl, surface-black, product-shadow 等），更新深色主题，更新字体栈

### Phase 1: 低风险视图（6 文件）
- `src/views/LikedView.vue` — 移除阴影，18px 圆角，pill CTA
- `src/views/HistoryView.vue` — 移除阴影，hairline 边框，pill CTA
- `src/views/WardrobeView.vue` — 移除阴影，18px 卡片圆角，pill 标签
- `src/views/OutfitDetailView.vue` — 黑色导航栏，移除卡片阴影，pill 按钮
- `src/views/OutfitMatchView.vue` — 移除阴影，pill 重新生成按钮
- `src/views/AddClothView.vue` — pill 保存按钮，移除卡片阴影

### Phase 2: 中风险视图（4 文件）
- `src/views/LoginView.vue` — 移除渐变背景，flat blue CTA pill
- `src/views/RegisterView.vue` — 替换粉红渐变为 flat blue
- `src/views/ProfileSettingsView.vue` — 替换 teal 色调，移除阴影
- `src/components/BottomSheet.vue` — 18px 圆角，移除阴影

### Phase 3: 高风险视图（3 文件，含拆分）
- `src/views/HomeView.vue` — 644→226 行，提取 SceneSelector + OutfitRecommendSection
- `src/views/ProfileEditView.vue` — 716→202 行，提取 BodyCardSection + StylePersonalitySection
- `src/views/ProfileView.vue` — 1832→367 行，提取 7 个子组件（CoverSection, BodyCardSection, ProfileTabs, LikedOutfitsPanel, HistoryPanel, AvatarModal, ConfirmDialog）

### Phase 4: 组件（5 文件）
- `src/components/BottomNav.vue` — 毛玻璃导航栏，flat blue 操作按钮
- `src/components/ClothingDetail.vue` — 18px 圆角，flat blue AI 建议
- `src/components/biz/MatchFilter.vue` — pill 场景标签，flat blue 生成按钮
- `src/components/biz/AIThinking.vue` — 替换紫色渐变为蓝色
- `src/components/biz/OutfitCard.vue` — 18px 圆角，移除阴影

### 新增文件
- `src/components/biz/SceneSelector.vue` — 场景选择器组件
- `src/components/biz/OutfitRecommendSection.vue` — 推荐区域组件
- `src/components/profile/CoverSection.vue` — 封面区域组件
- `src/components/profile/BodyCardSection.vue` — 身体数据卡片组件
- `src/components/profile/StylePersonalitySection.vue` — 风格个性组件
- `src/components/profile/LikedOutfitsPanel.vue` — 收藏列表组件
- `src/components/profile/HistoryPanel.vue` — 历史列表组件
- `src/components/profile/ProfileTabs.vue` — 标签切换组件
- `src/components/profile/AvatarModal.vue` — 头像预览弹窗
- `src/components/profile/ConfirmDialog.vue` — 确认对话框

## 注意事项
- 设计规范详见 `DESIGN.md`
- 编码规范详见 `RULE.md`（单文件 ≤ 500 行，模块走公共接口，Fail-Fast）
- 主色调 `#0066cc` 是唯一的交互色，不要引入第二个强调色
- Apple 设计系统中阴影仅用于产品图片，不在卡片/按钮上使用
