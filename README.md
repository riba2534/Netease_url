# 🎵 网易云音乐无损解析工具

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Docker-Ready-green.svg" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status">
</p>

一个强大的网易云音乐API服务，支持无损音质解析、歌曲搜索、歌单/专辑批量下载等功能。基于Flask构建，提供RESTful API接口，支持Docker一键部署。

## ✨ 核心功能

- 🎵 **单曲解析** - 支持通过ID或URL解析歌曲，获取多种音质下载链接
- 🔍 **音乐搜索** - 通过关键词搜索歌曲，支持分页和结果限制
- 📀 **歌单解析** - 批量获取歌单内所有歌曲信息
- 💿 **专辑解析** - 批量获取专辑内所有歌曲信息
- 📥 **音乐下载** - 自动下载并嵌入元数据（封面、歌词、艺术家等）
- 🎹 **音质选择** - 支持从标准到Hi-Res母带的7种音质级别
- 🌐 **Web界面** - 提供友好的网页操作界面

## 🎨 支持的音质级别

| 音质级别 | 说明 | 比特率 | 格式 | 会员要求 |
|---------|------|--------|------|----------|
| `standard` | 标准音质 | 128kbps | MP3 | 无 |
| `exhigh` | 极高音质 | 320kbps | MP3 | 无 |
| `lossless` | 无损音质 | 850kbps+ | FLAC | 黑胶VIP |
| `hires` | Hi-Res音质 | 1700kbps+ | FLAC | 黑胶VIP |
| `jyeffect` | 高清环绕声 | - | FLAC | 黑胶VIP |
| `sky` | 沉浸环绕声 | - | FLAC | 黑胶SVIP |
| `jymaster` | 超清母带 | 24bit/192kHz | FLAC | 黑胶SVIP |

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

#### 最简单运行
```bash
docker run -d -p 5000:5000 riba2534/netease_url:latest
```

#### 使用 docker-compose（推荐）

1. 创建 `docker-compose.yml` 文件：
```yaml
version: '3.8'

services:
  netease-music-api:
    image: riba2534/netease_url:latest
    container_name: netease-music-api
    ports:
      - "5000:5000"
    volumes:
      - ./downloads:/app/downloads
    environment:
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

2. 启动服务：
```bash
docker-compose up -d
```

#### 高级配置

使用自定义Cookie（黑胶VIP）：
```bash
docker run -d \
  -p 5000:5000 \
  -v ./downloads:/app/downloads \
  -e COOKIE_STRING="你的完整Cookie字符串" \
  riba2534/netease_url:latest
```

### 方式二：本地部署

#### 环境要求
- Python 3.10+
- uv (推荐) 或 pip

#### 安装步骤

1. 克隆项目：
```bash
git clone https://github.com/riba2534/Netease_url.git
cd Netease_url
```

2. 安装依赖（使用uv）：
```bash
# 安装uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync
```

3. 配置Cookie（可选，用于获取高音质）：
   - 将你的网易云音乐Cookie保存到 `cookie.txt` 文件

4. 运行服务：
```bash
uv run main.py
```

## 🔑 Cookie 获取方法

要获取无损音质，需要黑胶VIP账号的Cookie：

1. 登录[网易云音乐网页版](https://music.163.com)
2. 按 `F12` 打开开发者工具
3. 切换到 `Network` 标签页
4. 刷新页面，找到任意请求
5. 在请求头中找到 `Cookie` 字段，复制全部内容
6. 重点关注 `MUSIC_U` 字段（这是最重要的认证信息）

### Cookie 配置方式

#### Docker环境：
```bash
# 方式1：环境变量（推荐）
docker run -d -e COOKIE_STRING="完整Cookie内容" ...

# 方式2：挂载文件
docker run -d -v ./cookie.txt:/app/cookie.txt ...
```

#### 本地环境：
直接编辑项目根目录的 `cookie.txt` 文件

## 📡 API 接口文档

### 基础信息

- **基础URL**: `http://localhost:5000`
- **响应格式**: JSON
- **字符编码**: UTF-8

### 接口列表

#### 1. 健康检查
```http
GET /health
```

响应示例：
```json
{
  "status": 200,
  "success": true,
  "message": "API服务运行正常",
  "data": {
    "service": "running",
    "cookie_status": "valid",
    "version": "2.0.0"
  }
}
```

#### 2. 获取歌曲信息
```http
POST /song
```

请求参数：
```json
{
  "id": "167827",           // 歌曲ID
  "quality": "lossless"     // 音质级别（可选）
}
```

响应示例：
```json
{
  "status": 200,
  "success": true,
  "message": "获取歌曲URL成功",
  "data": {
    "id": 167827,
    "url": "http://...",
    "bitrate": 924151,
    "size": 27568111,
    "size_formatted": "26.29MB",
    "type": "flac",
    "level": "lossless",
    "quality_name": "无损音质"
  }
}
```

#### 3. 搜索音乐
```http
POST /search
GET /search?keyword=告白气球&limit=10
```

请求参数：
```json
{
  "keyword": "告白气球",
  "limit": 10,
  "offset": 0
}
```

#### 4. 获取歌单详情
```http
POST /playlist
```

请求参数：
```json
{
  "playlist_id": "2859214503"
}
```

#### 5. 获取专辑详情
```http
POST /album
```

请求参数：
```json
{
  "album_id": "34720827"
}
```

#### 6. 下载音乐
```http
POST /download
```

请求参数：
```json
{
  "music_id": "167827",
  "quality": "lossless"
}
```

返回：音频文件流（自动嵌入元数据）

#### 7. 批量下载
```http
POST /batch_download
```

支持SSE（Server-Sent Events）实时进度推送。

## 🐳 Docker 镜像管理

### 拉取最新镜像
```bash
docker pull riba2534/netease_url:latest
```

### 查看容器日志
```bash
docker logs -f netease-music-api
```

### 进入容器调试
```bash
docker exec -it netease-music-api /bin/bash
```

### 更新镜像
```bash
docker-compose pull
docker-compose up -d
```

## 🛠️ 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | 0.0.0.0 | 服务监听地址 |
| `PORT` | 5000 | 服务端口 |
| `DEBUG` | false | 调试模式 |
| `LOG_LEVEL` | INFO | 日志级别 |
| `DOWNLOADS_DIR` | downloads | 下载目录 |
| `COOKIE_FILE` | cookie.txt | Cookie文件路径 |
| `COOKIE_STRING` | - | Cookie字符串（优先级最高） |
| `CORS_ORIGINS` | * | CORS允许的源 |

## 📂 项目结构

```
Netease_url/
├── main.py              # Flask应用主入口
├── music_api.py         # 网易云API核心逻辑
├── music_downloader.py  # 下载和元数据处理
├── cookie_manager.py    # Cookie管理模块
├── qr_login.py         # 二维码登录（可选）
├── templates/          # Web界面模板
├── static/            # 静态资源
├── downloads/         # 下载文件存储
├── cookie.txt        # Cookie配置文件
├── Dockerfile        # Docker镜像定义
├── docker-compose.yml # Docker编排配置
└── pyproject.toml    # 项目依赖配置
```

## 🔧 开发指南

### 本地开发环境

```bash
# 克隆项目
git clone https://github.com/riba2534/Netease_url.git
cd Netease_url

# 安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
uv sync

# 运行开发服务器
DEBUG=true uv run main.py
```

### 构建Docker镜像

```bash
# 构建镜像
docker build -t netease_url:dev .

# 测试运行
docker run -p 5000:5000 netease_url:dev
```

### 代码风格

- 使用 `ruff` 进行代码检查
- 遵循 PEP 8 规范
- 类型注解使用 `typing` 模块

## 🐛 故障排查

### Cookie无效
- 确认Cookie包含完整的 `MUSIC_U` 字段
- 检查Cookie是否过期（通常有效期30天）
- 尝试重新登录获取新Cookie

### 无法获取无损音质
- 确认账号是黑胶VIP会员
- 检查Cookie配置是否正确
- 查看容器日志：`docker logs netease-music-api`

### 下载失败
- 检查下载目录权限
- 确认磁盘空间充足
- 查看详细错误日志

## 📜 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献步骤

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 🙏 致谢

- 网易云音乐API逆向工程社区
- Flask框架开发团队
- 所有贡献者和用户

## ⚠️ 免责声明

本项目仅供学习和研究使用。请勿用于商业用途或侵犯版权的行为。使用本项目产生的任何法律责任由使用者自行承担。

## 📮 联系方式

- GitHub: [@riba2534](https://github.com/riba2534)
- Issues: [项目问题反馈](https://github.com/riba2534/Netease_url/issues)

---

<p align="center">Made with ❤️ by riba2534</p>