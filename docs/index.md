# AI Style 文档中心

> "不仅是衣橱，更是你的 AI 穿搭策略中心"

## 技术栈

| 模块 | 技术 | 说明 |
|------|------|------|
| [Frontend](./modules/frontend.md) | Vue 3 + Pinia + Vue Router | 移动端优先，Mock/真实一键切换 |
| [Backend](./modules/backend.md) | FastAPI + Python 异步 | AI 穿搭推荐、天气 API |
| [Database](./modules/db.md) | PostgreSQL + SQLAlchemy 2.0 async | 4 张表、21 个 Repository 方法 |

## 快速导航

- [环境搭建](./guides/setup.md) — 10 分钟启动开发环境
- [部署指南](./guides/deployment.md) — 生产环境部署
- [贡献规范](./guides/contributing.md) — Git 工作流与代码规范
- [架构概述](./architecture/overview.md) — 系统组件与模块职责
- [数据流](./architecture/data-flow.md) — 核心业务流程

## 项目概览

前后端分离的 AI 穿搭推荐应用，根据天气 + 用户衣橱生成场景化穿搭方案。

- AI 搭配：三阶段交互（输入 → 生成动画 → 卡片结果）
- 天气感知：和风天气 API + DeepSeek LLM
- 数据持久化：Neon PostgreSQL + Alembic 迁移

> 详细项目说明见 [根目录 README](../README.md)