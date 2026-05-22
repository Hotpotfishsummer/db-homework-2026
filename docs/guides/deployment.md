# 部署指南

## 环境变量

生产环境必须配置以下变量，**不要**提交到 Git：

```bash
# 后端
HEFENG_API_KEY=
DEEPSEEK_API_KEY=
DEBUG=false

# 数据库
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
```

## 后端部署

### uvicorn 直接运行

```bash
cd backend
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2 > app.log 2>&1 &
```

### nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 前端部署

```bash
cd frontend
npm run build
# 输出到 dist/ 目录，可直接用 nginx 托管
```

## CORS 配置

后端默认允许 `http://localhost:5173` 开发 origins。生产环境修改 `backend/app/core/config.py` 中的 CORS 白名单。

## 数据库连接池

Neon 免费版配置（`db/session.py`）：

- `pool_size=10`
- `max_overflow=5`

如使用其他 PostgreSQL 服务，适当调整连接池参数。