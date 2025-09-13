# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用命令

### 运行项目
```bash
# 使用 uv 运行项目
uv run main.py
```

### 依赖管理
```bash
# 使用 uv 管理依赖
uv sync  # 安装/更新所有依赖
uv add <package>  # 添加新依赖
uv remove <package>  # 移除依赖

# 查看依赖树
uv tree

# 更新依赖
uv lock --upgrade
```

### 清理进程和文件
```bash
# 清理运行中的进程
ps aux | grep "uv run main.py" | grep -v grep | awk '{print $2}' | xargs -r kill -9

# 清理临时文件
rm -rf __pycache__/
rm -rf .pytest_cache/
```

### Cookie配置
必须在 `cookie.txt` 文件中配置有效的网易云音乐黑胶会员Cookie，格式如下：
```
MUSIC_U=你的MUSIC_U值;os=pc;appver=8.9.70;
```

## 架构概览

### 核心模块关系

1. **main.py** - Flask应用主入口
   - 初始化 `MusicAPIService` 服务类
   - 定义所有HTTP路由端点
   - 处理请求验证和响应格式化
   - 依赖：`music_api.py`, `cookie_manager.py`, `music_downloader.py`

2. **music_api.py** - 网易云音乐API封装
   - `NeteaseAPI` 类：核心API交互逻辑，包含请求加密、签名等
   - 提供独立函数：`url_v1`, `name_v1`, `lyric_v1`, `search_music`, `playlist_detail`, `album_detail`
   - 音质级别枚举：`QualityLevel` (standard, exhigh, lossless, hires等)
   - 处理网易云音乐的加密通信协议

3. **music_downloader.py** - 音乐下载处理
   - `MusicDownloader` 类：负责下载音频文件和元数据处理
   - 支持多种音频格式（MP3, FLAC等）
   - 自动嵌入歌曲元信息（标题、艺术家、专辑、封面等）
   - 使用 `mutagen` 库处理音频元数据

4. **cookie_manager.py** - Cookie管理
   - `CookieManager` 类：管理和验证Cookie
   - 从 `cookie.txt` 文件读取Cookie
   - Cookie格式解析和验证

5. **qr_login.py** - 二维码登录
   - `QRLoginManager` 类：处理网易云音乐二维码登录流程
   - 生成登录二维码
   - 轮询登录状态

### API路由结构

- `/` - Web界面首页
- `/health` - 健康检查
- `/song` - 单曲解析（支持GET/POST）
- `/search` - 歌曲搜索
- `/playlist` - 歌单解析
- `/album` - 专辑解析
- `/download` - 音乐下载
- `/batch_download` - 批量下载（歌单/专辑）

### 请求流程

1. **用户请求** → Flask路由处理器（main.py）
2. **参数验证** → 提取ID或URL，验证Cookie
3. **API调用** → 调用 `music_api.py` 中的相应函数
4. **数据处理** → 获取音乐信息、下载链接等
5. **下载处理**（如需要）→ `music_downloader.py` 下载文件并嵌入元数据
6. **响应返回** → JSON格式或文件流

### 重要配置

- **端口**：默认5000（可通过环境变量PORT修改）
- **下载目录**：`downloads/`
- **日志级别**：默认INFO
- **请求超时**：30秒
- **最大文件大小**：500MB

### Cookie获取方法

1. 登录网易云音乐网页版
2. F12打开开发者工具
3. Network标签页找到任意请求
4. 复制Cookie中的MUSIC_U值

### 音质级别说明

- `standard`: 标准音质 (128kbps)
- `exhigh`: 极高音质 (320kbps)
- `lossless`: 无损音质 (FLAC)
- `hires`: Hi-Res音质 (24bit/96kHz)
- `jyeffect`: 高清环绕声（黑胶VIP）
- `sky`: 沉浸环绕声（黑胶SVIP）
- `jymaster`: 超清母带（黑胶SVIP）

### 错误处理

项目使用自定义异常类：
- `APIException` - API调用异常
- `CookieException` - Cookie相关异常
- `DownloadException` - 下载相关异常

所有API响应遵循统一格式：
```json
{
  "status": 状态码,
  "success": true/false,
  "message": "消息",
  "data": 数据对象
}
```