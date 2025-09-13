# 网易云音乐 API 服务（Docker 版）

一个基于 Flask 的网易云音乐解析与下载服务，支持歌曲信息获取、搜索、歌单与专辑解析、单曲下载与批量下载（后台任务 + SSE 进度）。已提供 Docker 镜像封装，便于快速部署。

## 功能特性
- 单曲信息：链接/ID 解析、下载链接查询、歌词获取
- 搜索能力：关键词搜索（歌曲为主）
- 详情页：歌单、专辑详情解析
- 下载能力：单曲下载、批量下载（ZIP，附下载报告）
- 前端页面：内置简洁首页，支持一键复制链接、回车触发
- 健康检查：`/health` 接口

## 快速开始（Docker）

### 方式一：本地构建镜像
```bash
# 构建镜像（位于项目根目录）
docker build -t netease-music-api:latest .

# 运行容器（映射端口、下载目录、cookie.txt）
docker run -d \
  --name netease-music-api \
  -p 5000:5000 \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/cookie.txt:/app/cookie.txt:ro \
  -e LOG_LEVEL=INFO \
  netease-music-api:latest

# 访问服务
# 前端页面
open http://localhost:5000
# 健康检查
curl http://localhost:5000/health
```

### 方式二：Docker Compose
```yaml
services:
  netease:
    image: ${DOCKER_IMAGE:-riba2534/netease_url:latest}
    container_name: netease-music-api
    ports:
      - "5000:5000"
    environment:
      HOST: 0.0.0.0
      PORT: 5000
      DEBUG: "false"
      DOWNLOADS_DIR: downloads
      LOG_LEVEL: INFO
      CORS_ORIGINS: "*"
    volumes:
      - ./downloads:/app/downloads
    restart: unless-stopped
```
启动：
```bash
docker compose up -d
```

### 方式三：从 Docker Hub 拉取（镜像：riba2534/netease_url）
```bash
# 登录（首次需要）
docker login

# 拉取镜像
docker pull riba2534/netease_url:latest

# 运行
docker run -d \
  --name netease-music-api \
  -p 5000:5000 \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/cookie.txt:/app/cookie.txt:ro \
  riba2534/netease_url:latest
```

## 环境变量
- `HOST`：绑定地址（默认 `0.0.0.0`）
- `PORT`：服务端口（默认 `5000`）
- `DEBUG`：是否开启调试（`true/false`，默认 `false`）
- `DOWNLOADS_DIR`：下载目录（默认 `downloads`）
- `LOG_LEVEL`：日志等级（默认 `INFO`）
- `CORS_ORIGINS`：CORS 白名单（默认 `*`）
- `COOKIE_FILE`：容器内 Cookie 文件路径（默认 `cookie.txt`，即 `/app/cookie.txt`）
- `COOKIE_STRING`：直接通过环境变量注入 Cookie 内容（若设置，将写入 `COOKIE_FILE`）

## 常用目录挂载
- `/app/downloads`：下载输出目录（建议映射到宿主机，避免容器删除后文件丢失）
- `/app/cookie.txt` 或 `/app/config/cookie.txt`：Cookie 文件（建议以只读方式挂载 `:ro`）

示例一（默认路径 `/app/cookie.txt`）：
```bash
-v $(pwd)/cookie.txt:/app/cookie.txt:ro
```

示例二（自定义路径 `/app/config/cookie.txt`）：
```bash
-v $(pwd)/cookie.txt:/app/config/cookie.txt:ro -e COOKIE_FILE=/app/config/cookie.txt
```

示例三（不挂载文件，使用环境变量直接提供 Cookie）
```bash
-e COOKIE_STRING='MUSIC_U=xxx; __csrf=yyy; ...'
```

## 主要接口
- `GET  /`：内置前端页面
- `GET  /health`：健康检查
- `GET/POST /song`：歌曲信息（支持 `id|url`，`level`）
- `GET/POST /search`：搜索
- `GET/POST /playlist`：歌单详情
- `GET/POST /album`：专辑详情
- `GET/POST /download`：下载单曲（支持 `format=json|file`）
- `POST /batch_download_v2`：批量下载任务（后台任务 + SSE）
- `GET  /download_progress/<task_id>`：SSE 进度
- `GET  /download_result/<task_id>`：下载结果（ZIP）

## 本地开发
```bash
# 推荐使用 uv（已提供 uv.lock）
uv venv && uv sync
source .venv/bin/activate  # Windows: .\\.venv\\Scripts\\activate

# 运行
python main.py
```

## 构建并推送到 Docker Hub（手动）
```bash
# 登录
docker login

# 构建（latest 标签）
docker build -t riba2534/netease_url:latest .

# 推送
docker push riba2534/netease_url:latest

# 若需要自定义标签（例如 tagname）
docker tag riba2534/netease_url:latest riba2534/netease_url:tagname
docker push riba2534/netease_url:tagname
```

## GitHub Action 自动推送（可选）
已提供 `.github/workflows/docker-publish.yml`，在你仓库配置 Secrets 后，将在 push 到默认分支时自动构建并推送镜像：
- `DOCKERHUB_USERNAME`：你的 Docker Hub 用户名
- `DOCKERHUB_TOKEN`：Docker Hub 的 Access Token

默认推送 `latest` 与基于 Git 信息生成的标签。

## 许可
遵循仓库内 `LICENSE` 文件。

---
页脚说明：本项目前端页脚按要求保留英文专业风格、年自动更新、仓库链接，以及“Modified by riba2534 based on work by Suxiaoqingx”致谢。
