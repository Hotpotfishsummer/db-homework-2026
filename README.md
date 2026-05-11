# db-homework-2026

MySQL 课程设计作业基础仓库，采用前后端分离结构：

- 前端：Vue 3 + Vite
- 后端：Python (FastAPI)
- Python 环境管理：Conda + `environment.yml`

## 目录结构

```text
.
├── backend/
│   ├── app/
│   │   ├── api/v1/        # API 路由
│   │   ├── core/          # 配置与安全
│   │   ├── models/        # Pydantic 模型
│   │   ├── services/      # 业务逻辑
│   │   └── static/        # 图片存储
│   ├── tests/
│   ├── main.py            # FastAPI 入口
│   ├── requirements.txt
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

## 后端启动

```bash
cd backend
conda env create -f environment.yml
conda activate l-wardrobe
python main.py --port 8080
```

后端 API 文档：`http://localhost:8080/docs`
