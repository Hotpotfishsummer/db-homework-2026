# 环境搭建

## 前置要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Node.js | >= 16.0.0 | 前端开发 |
| Python | 3.12+ | 后端开发 |
| Conda | 任意版本 | Python 环境管理 |
| PostgreSQL | 15+ | 数据库（本地/云） |

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd db-homework-2026
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

### 3. 安装后端依赖

```bash
cd backend
conda env create -f environment.yml   # 或 conda activate l-wardrobe
pip install -r requirements.txt
```

### 4. 配置环境变量

**后端** (`backend/.env`)：

```bash
HEFENG_API_KEY=your_hefeng_api_key
HEFENG_API_HOST=your_host.re.qweatherapi.com
DEEPSEEK_API_KEY=sk-your_key
DEBUG=true
```

**数据库** (`backend/.env`)：

```bash
# 本地 PostgreSQL（推荐）
DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/l_wardrobe

# Neon / 云数据库（兼容保留）
# DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require&channel_binding=require
```

详细配置见 [数据库模块文档](../modules/db.md)。

### 4.1 Docker Compose 本地开发

如果你想直接起三容器联调环境，先准备好 [backend/.env](../../backend/.env) 的本地配置，然后在仓库根目录执行：

```bash
docker compose up --build backend
docker compose up --build frontend
```

相关辅助命令：

```bash
docker compose logs -f
docker compose down --remove-orphans
```

VS Code 里也可以直接使用 `Frontend: Dev`、`Backend: Compose Up`、`Frontend: Compose Up`、`Compose: Logs`、`Compose: Down` 这几个任务。

`Backend: Compose Up` 和 `Frontend: Compose Up` 会在集成终端里分别启动对应容器并持续输出日志，适合配合调试器使用。

### 5. 初始化数据库

```bash
# 在项目根目录执行，应用所有迁移
alembic -c db/alembic.ini upgrade head
```

### 6. 启动服务

**后端：**
```bash
cd backend
python main.py --port 8000
# API 文档: http://localhost:8000/docs
```

**前端：**
```bash
cd frontend
npm run dev
# 默认: http://localhost:5173
```

## 验证

- 前端：`http://localhost:5173` 能打开登录页
- 后端：`http://localhost:8000/docs` 能打开 Swagger UI
- 数据库：执行 `alembic -c db/alembic.ini current` 确认已应用迁移