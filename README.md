# db-homework-2026

MySQL 课程设计作业基础仓库，采用前后端分离结构：

- 前端：Vue 3 + Vite
- 后端：Python
- Python 环境管理：Conda + `environment.yml`

## 目录结构

```text
.
├── backend/
│   ├── app/
│   ├── tests/
│   └── environment.yml
└── frontend/
    ├── src/
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 后端环境准备

```bash
cd backend
conda env create -f environment.yml
conda activate db-homework-2026-backend
```

当前仓库仅提供基础项目框架，不包含示例业务代码。
