# Docker 服务启动指南

## 适用场景

本文说明如何在本地启动项目依赖的 Docker 服务，适合开发、联调和排查问题时参考。

它不依赖具体的 VS Code 调试配置，也不假设服务会部署到云端。

## 服务说明

仓库根目录的 `docker-compose.yml` 负责启动项目相关容器。常见服务包括：

- 数据库服务：为后端提供 PostgreSQL 连接。
- 后端服务：提供 FastAPI 接口。
- 前端服务：提供 Vue 开发或静态服务。

具体服务名称以当前仓库的 Compose 文件为准，若有调整，可先查看 `docker compose config` 或 `docker compose ps`。

## 启动步骤

1. 确认本地环境变量已配置，尤其是后端的数据库连接地址。
2. 在仓库根目录执行启动命令。

```bash
docker compose up --build
```

如果只想启动某个服务，可以显式指定服务名：

```bash
docker compose up --build backend
docker compose up --build frontend
```

## 常用命令

查看运行状态：

```bash
docker compose ps
```

查看日志：

```bash
docker compose logs -f
```

停止服务：

```bash
docker compose down --remove-orphans
```

重新构建后启动：

```bash
docker compose up --build --force-recreate
```

## 访问方式

启动完成后，按项目实际端口访问对应服务：

- 前端页面：浏览器访问前端暴露的地址。
- 后端接口：浏览器访问后端的 Swagger 或健康检查地址。
- 数据库：通过本地客户端或后端连接字符串访问。

## 常见问题

- 服务起不来时，优先检查端口是否被占用。
- 数据库连接失败时，确认 `DATABASE_URL` 是否与 Compose 中的数据库服务一致。
- 如果某个服务已经存在旧容器，先执行停止命令再重新启动。

## 备注

这是一份抽象的启动说明，便于在不暴露额外调试配置的前提下统一指导本地 Docker 启动流程。