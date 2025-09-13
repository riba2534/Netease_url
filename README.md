# 网易云音乐 API 服务

一个基于 Flask 的网易云音乐解析与下载服务，支持歌曲信息获取、搜索、歌单与专辑解析、单曲下载与批量下载。提供完整的 Docker 支持，便于快速部署。

## 功能特性

- 🎵 **单曲解析**：支持网易云音乐链接/ID解析，获取下载链接、歌词等信息
- 🔍 **音乐搜索**：关键词搜索歌曲，支持分页
- 📋 **歌单/专辑解析**：获取完整的歌单或专辑详情信息
- ⬇️ **音乐下载**：单曲下载，支持多种音质（标准到超清母带）
- 📦 **批量下载**：歌单/专辑批量下载，生成ZIP文件，附下载报告
- 🌐 **Web界面**：内置简洁前端页面，支持一键操作
- 🏥 **健康检查**：提供 `/health` 接口监控服务状态
- 📊 **实时进度**：批量下载支持 SSE 实时进度反馈

## 快速开始

### 方式一：Docker Compose（推荐）

1. 创建项目目录并切换到该目录：
```bash
mkdir netease-music-api && cd netease-music-api
```

2. 下载配置文件：
```bash
# 下载 docker-compose.yml
wget https://raw.githubusercontent.com/riba2534/Netease_url/main/docker-compose.yml

# 或者手动创建 docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  netease-music-api:
    image: riba2534/netease_url:latest
    container_name: netease-music-api
    ports:
      - "${HOST_PORT:-5000}:5000"
    environment:
      HOST: 0.0.0.0
      PORT: 5000
      DEBUG: "false"
      DOWNLOADS_DIR: downloads
      LOG_LEVEL: INFO
      CORS_ORIGINS: "*"
      # 方式1: 直接设置Cookie（推荐，取消注释并填入您的Cookie）
      # COOKIE_STRING: "_iuqxldmzr_=32; _ntes_nnid=xxx; MUSIC_U=你的完整MUSIC_U值; __csrf=xxx;"
    volumes:
      - ./downloads:/app/downloads
      # 方式2: 挂载Cookie文件（可选，如使用方式1请注释掉下一行）
      - ./cookie.txt:/app/cookie.txt:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s

networks:
  default:
    name: netease-music-network
EOF
```

3. 配置 Cookie（二选一）：

**方法A：使用环境变量（推荐）**
```bash
# 编辑 docker-compose.yml，取消 COOKIE_STRING 注释并填入完整Cookie
# COOKIE_STRING: "你的完整Cookie字符串"
```

**方法B：使用Cookie文件**
```bash
# 创建 cookie.txt 文件
echo "你的完整Cookie字符串" > cookie.txt
```

4. 启动服务：
```bash
# 前台启动（查看日志）
docker compose up

# 后台启动
docker compose up -d

# 查看日志
docker compose logs -f
```

5. 访问服务：
```bash
# 浏览器访问 Web 界面
open http://localhost:5000

# 命令行测试健康检查
curl http://localhost:5000/health
```

### 方式二：Docker 命令行

```bash
# 1. 拉取最新镜像
docker pull riba2534/netease_url:latest

# 2. 创建必要目录
mkdir -p downloads

# 3. 运行容器（环境变量方式）
docker run -d \
  --name netease-music-api \
  -p 5000:5000 \
  -v $(pwd)/downloads:/app/downloads \
  -e COOKIE_STRING="你的完整Cookie字符串" \
  -e LOG_LEVEL=INFO \
  --restart unless-stopped \
  riba2534/netease_url:latest

# 或者使用Cookie文件方式
echo "你的完整Cookie字符串" > cookie.txt
docker run -d \
  --name netease-music-api \
  -p 5000:5000 \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/cookie.txt:/app/cookie.txt:ro \
  --restart unless-stopped \
  riba2534/netease_url:latest
```

### 方式三：本地开发

```bash
# 克隆项目
git clone https://github.com/riba2534/Netease_url.git
cd Netease_url

# 使用 uv 管理依赖（推荐）
uv sync
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 配置 Cookie
echo "MUSIC_U=你的MUSIC_U值;os=pc;appver=8.9.70;" > cookie.txt

# 运行服务
python main.py
```

## Cookie 配置

### 📋 获取完整 Cookie 的方法

1. **登录网易云音乐**：
   - 访问 [网易云音乐网页版](https://music.163.com)
   - 使用您的黑胶VIP账号登录

2. **获取完整Cookie**：
   - 按 `F12` 打开开发者工具
   - 切换到 `Network` 标签页
   - 刷新页面或播放一首歌曲
   - 找到任意一个请求（推荐选择 `/api/` 开头的请求）
   - 点击请求，在 `Headers` 中找到 `Cookie` 字段
   - **复制完整的Cookie字符串**（不只是MUSIC_U）

3. **Cookie 格式示例**：
```
_iuqxldmzr_=32; _ntes_nnid=xxx; NMTID=xxx; MUSIC_U=你的MUSIC_U值; __csrf=xxx; JSESSIONID-WYYY=xxx; 其他Cookie值
```

### 🔧 配置方式

**方式一：环境变量（推荐）**
```bash
# Docker Compose 中设置
COOKIE_STRING: "你的完整Cookie字符串"

# Docker 命令行中设置
-e COOKIE_STRING="你的完整Cookie字符串"
```

**方式二：Cookie文件**
```bash
# 创建 cookie.txt 文件
echo "你的完整Cookie字符串" > cookie.txt

# Docker 中挂载文件
-v $(pwd)/cookie.txt:/app/cookie.txt:ro
```

### ⚠️ 重要说明

- **推荐使用黑胶VIP账号**：获得所有音质和功能支持
- **Cookie会过期**：通常1-7天，需要定期更新
- **保护隐私**：Cookie包含敏感信息，不要泄露给他人
- **完整Cookie更稳定**：比只使用MUSIC_U更不容易被限制

## API 接口

### 基础接口
- `GET  /` - Web 前端页面
- `GET  /health` - 健康检查
- `GET  /api/info` - API 信息

### 音乐相关接口
- `GET/POST /song` - 获取单曲信息
  - 参数：`id` 或 `url`（音乐ID或网易云链接），`level`（音质等级），`type`（返回类型）
- `GET/POST /search` - 搜索音乐
  - 参数：`keyword`（搜索关键词），`limit`（限制数量），`offset`（偏移量）
- `GET/POST /playlist` - 获取歌单详情
  - 参数：`id`（歌单ID）
- `GET/POST /album` - 获取专辑详情
  - 参数：`id`（专辑ID）

### 下载接口
- `GET/POST /download` - 单曲下载
  - 参数：`id`（音乐ID），`quality`（音质），`format`（返回格式：file/json）
- `POST /batch_download` - 批量下载（传统方式）
- `POST /batch_download_v2` - 批量下载任务（SSE进度）
- `GET  /download_progress/<task_id>` - SSE 进度监控
- `GET  /download_result/<task_id>` - 获取下载结果ZIP

## 音质支持

| 音质等级 | 说明 | 会员要求 |
|---------|------|----------|
| `standard` | 标准音质 (128kbps) | 普通用户 |
| `exhigh` | 极高音质 (320kbps) | VIP |
| `lossless` | 无损音质 (FLAC) | VIP |
| `hires` | Hi-Res音质 (24bit) | 黑胶VIP |
| `jyeffect` | 高清环绕声 | 黑胶VIP |
| `sky` | 沉浸环绕声 | 黑胶SVIP |
| `jymaster` | 超清母带 | 黑胶SVIP |

## 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | `0.0.0.0` | 服务绑定地址 |
| `PORT` | `5000` | 服务端口 |
| `DEBUG` | `false` | 是否开启调试模式 |
| `DOWNLOADS_DIR` | `downloads` | 下载目录 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `CORS_ORIGINS` | `*` | CORS 允许的源 |
| `COOKIE_FILE` | `cookie.txt` | Cookie 文件路径 |
| `COOKIE_STRING` | - | 直接设置 Cookie 内容 |

## 部署示例

### 使用 Docker Compose

```yaml
version: '3.8'

services:
  netease-music-api:
    image: riba2534/netease_url:latest
    container_name: netease-music-api
    ports:
      - "5000:5000"
    environment:
      HOST: 0.0.0.0
      PORT: 5000
      LOG_LEVEL: INFO
      COOKIE_STRING: "MUSIC_U=你的MUSIC_U值;os=pc;appver=8.9.70;"
    volumes:
      - ./downloads:/app/downloads
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s
```

### 反向代理配置（Nginx）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE 支持
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
```

## 🐳 Docker 管理命令

### 容器管理
```bash
# 查看容器状态
docker ps -a | grep netease

# 查看容器日志
docker logs -f netease-music-api

# 进入容器
docker exec -it netease-music-api bash

# 重启容器
docker restart netease-music-api

# 停止容器
docker stop netease-music-api

# 删除容器
docker rm netease-music-api

# 删除镜像
docker rmi riba2534/netease_url:latest
```

### Docker Compose 管理
```bash
# 启动服务
docker compose up -d

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 停止并删除数据卷
docker compose down -v

# 更新镜像
docker compose pull
docker compose up -d
```

### 故障排查
```bash
# 检查容器健康状态
docker inspect netease-music-api | grep -A 10 Health

# 检查端口占用
netstat -tlnp | grep 5000
lsof -i :5000

# 检查磁盘空间
df -h
docker system df

# 清理Docker缓存
docker system prune -a
```

## 🔧 本地构建和推送

### 本地构建
```bash
# 构建镜像（使用uv管理依赖）
docker build -t riba2534/netease_url:latest .

# 构建时指定平台
docker buildx build --platform linux/amd64,linux/arm64 -t riba2534/netease_url:latest .

# 推送到 Docker Hub
docker push riba2534/netease_url:latest
```

### 使用脚本
```bash
# 使用内置脚本构建并推送
chmod +x scripts/docker_build_push.sh
./scripts/docker_build_push.sh [标签名]
```

### 构建要求
- 项目使用 `uv` 进行依赖管理
- 需要 `pyproject.toml` 和 `uv.lock` 文件
- 不再需要 `requirements.txt` 文件

## 目录结构

```
.
├── main.py                 # Flask 应用主入口
├── music_api.py            # 网易云音乐 API 封装
├── music_downloader.py     # 音乐下载器
├── cookie_manager.py       # Cookie 管理器
├── download_progress.py    # 下载进度管理
├── enhanced_download.py    # 增强下载功能
├── qr_login.py            # 二维码登录
├── templates/             # Web 前端模板
│   └── index.html
├── Dockerfile             # Docker 构建文件
├── docker-compose.yml     # Docker Compose 配置
├── requirements.txt       # Python 依赖
└── scripts/               # 辅助脚本
    └── docker_build_push.sh
```

## 注意事项

1. **Cookie 要求**：需要有效的网易云音乐 Cookie，建议使用黑胶会员账号以获得完整功能
2. **版权限制**：某些歌曲可能因版权限制无法下载
3. **存储空间**：批量下载会占用大量存储空间，请确保有足够空间
4. **网络要求**：需要稳定的网络连接访问网易云音乐服务器
5. **使用限制**：请遵守相关法律法规，仅用于个人学习研究

## 更新日志

### v2.2.0 (2025-09-13)
- 🚀 **重大更新**：Docker构建完全迁移到 uv 依赖管理
- 🔧 **优化构建**：移除 requirements.txt，使用 pyproject.toml + uv.lock
- 📦 **镜像优化**：更快的依赖安装速度（10-100倍提升）
- 🍪 **Cookie增强**：更新默认Cookie配置，支持完整Cookie字符串
- 📚 **文档完善**：重写Docker使用方法，提供完整的管理命令
- ✅ **配置优化**：完善 docker-compose.yml 和 .dockerignore

### v2.1.0 (2025-09-13)
- ✅ 修复 Dockerfile 配置问题
- ✅ 新增 docker-compose.yml 配置文件
- ✅ 更新依赖包到最新安全版本
- ✅ 优化 Docker 镜像大小和安全性
- ✅ 完善健康检查机制
- ✅ 更新文档和部署说明

## 许可证

本项目基于现有开源项目修改，遵循原项目许可证。

## 致谢

Modified by riba2534 based on work by Suxiaoqingx

---

**访问地址**：服务启动后访问 http://localhost:5000