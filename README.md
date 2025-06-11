# News MCP Server

一个基于 Model Context Protocol (MCP) 的新闻聚合服务器，支持从多个 RSS 源获取和搜索新闻文章。

## 🌟 功能特性

- 📰 **多源新闻聚合**: 支持 13+ 主流新闻源（科技、综合、商业、科学等）
- 🔍 **智能搜索**: 支持关键词搜索新闻文章
- 📂 **分类管理**: 按类别组织新闻源
- ⚡ **缓存机制**: 可配置缓存时间避免频繁请求
- 🌐 **多传输协议**: 支持 stdio、SSE、Streamable HTTP
- 🔧 **自定义源**: 支持通过配置文件和环境变量添加自定义 RSS 源
- 🖥️ **Web 界面**: HTTP 模式下提供状态信息页面
- ⚙️ **配置管理**: 使用 YAML 配置文件进行灵活配置
- 🏗️ **模块化架构**: 清晰的代码结构，易于维护和扩展

## 📰 支持的新闻源

| 分类 | 新闻源 |
|------|--------|
| 🔬 **科技** | Wired, The Verge, CNET |
| 📰 **综合** | 纽约时报, BBC, 卫报 |
| 💼 **商业** | CNBC, 华尔街日报 |
| 🧪 **科学** | NASA, Science Magazine |
| 🌍 **其他** | 旅游、政治等专门类别 |

## 🚀 快速开始

### 安装

1. **克隆项目**：
```bash
git clone <repository-url>
cd trends-hub-mcp
```

2. **创建虚拟环境**：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

3. **安装依赖**：
```bash
pip install -r requirements.txt
```

### 启动服务器

#### 🖥️ 本地开发 (stdio)
```bash
# 使用 Python 模块方式 (推荐)
python -m src.main

# 或直接运行主文件
python src/main.py

# 或使用启动脚本
./start_news_mcp.sh
```

#### 🌐 Web 部署 (HTTP)
```bash
# Streamable HTTP (推荐)
python -m src.main --transport streamable-http --port 8000

# SSE 协议
python -m src.main --transport sse --port 8000

# 自定义主机和端口
python -m src.main --transport streamable-http --host 0.0.0.0 --port 3000

# 使用启动脚本
./start_news_mcp.sh --transport streamable-http --port 8000
```

#### 📋 命令行参数
```
选项:
  -t, --transport PROTOCOL    传输协议 (stdio|sse|streamable-http)
  -p, --port PORT            HTTP服务器端口 (默认: 从配置文件读取)
  --host HOST                HTTP服务器主机 (默认: 从配置文件读取)
  --log-level LEVEL          日志级别 (DEBUG|INFO|WARNING|ERROR)
  --config-dir DIR           配置文件目录 (默认: config)
  -h, --help                 显示帮助信息
```

#### ⚙️ 配置文件
项目使用 YAML 配置文件进行管理：
- `config/server.yaml`: 服务器配置（端口、日志、缓存等）
- `config/feeds.yaml`: RSS 源配置

可以通过命令行参数覆盖配置文件中的设置。

## 📁 项目结构

```
trends-hub-mcp/
├── src/                    # 主要源代码目录
│   ├── __init__.py
│   ├── main.py            # 主入口文件
│   ├── server.py          # MCP 服务器实现
│   ├── config/            # 配置管理模块
│   │   ├── __init__.py
│   │   └── settings.py    # 配置加载器
│   ├── feeds/             # RSS 源管理模块
│   │   ├── __init__.py
│   │   ├── manager.py     # RSS 源管理器
│   │   └── cache.py       # 缓存实现
│   └── tools/             # MCP 工具实现
│       ├── __init__.py
│       ├── news_tools.py  # 新闻相关工具
│       └── system_tools.py # 系统工具
├── config/                # 配置文件目录
│   ├── server.yaml        # 服务器配置
│   └── feeds.yaml         # RSS 源配置
├── requirements.txt       # Python 依赖
├── start_news_mcp.sh     # 启动脚本
└── README.md             # 项目说明
```

### 验证服务器
启动后访问 `http://localhost:8000` 查看服务器状态页面（仅 HTTP 模式）。

## 🔧 MCP 工具

| 工具名称 | 功能描述 | 主要参数 |
|----------|----------|----------|
| `health_check` | 检查服务器健康状态 | 无 |
| `list_available_feeds` | 列出所有可用的新闻源和分类 | 无 |
| `get_latest_news` | 获取最新新闻文章 | `category`, `limit` |
| `search_news` | 搜索匹配查询的新闻文章 | `query`, `limit` |
| `get_feed_content` | 获取特定新闻源的文章 | `feed_name`, `limit` |
| `get_article_details` | 通过 URL 获取文章详细信息 | `url` |

**参数说明**：
- `category`: 分类过滤 (tech, general, business, science, travel, politics)
- `limit`: 返回文章数量 (默认: 5, 最大: 20)
- `query`: 搜索关键词
- `feed_name`: 新闻源名称
- `url`: 文章 URL

## 🌐 HTTP API 使用

### 端点信息
| 协议 | 端点 | 说明 |
|------|------|------|
| **Streamable HTTP** | `http://localhost:8000/mcp` | MCP 协议端点 |
| **SSE** | `http://localhost:8000/sse` | SSE 连接端点 |
| **SSE** | `http://localhost:8000/messages` | 消息发送端点 |
| **信息页面** | `http://localhost:8000/` | 服务器状态页面 |

### 快速测试
```bash
# 初始化连接
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}'

# 健康检查
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: YOUR_SESSION_ID" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "health_check", "arguments": {}}}'
```

> **注意**: Streamable HTTP 协议需要维护会话 ID，详细用法请参考服务器状态页面。

## ⚙️ 高级配置

### 自定义 RSS 源
有两种方式添加自定义新闻源：

#### 方式1: 修改配置文件
编辑 `config/feeds.yaml` 文件添加新的 RSS 源。

#### 方式2: 环境变量
```bash
export NEWS_MCP_CUSTOM_FEEDS="techcrunch:https://techcrunch.com/feed/;hacker_news:https://hnrss.org/frontpage"
python -m src.main --transport streamable-http
```
格式：`name1:url1;name2:url2`

### 开发和调试
```bash
# 调试模式
python -m src.main --log-level DEBUG

# 指定配置目录
python -m src.main --config-dir ./custom-config

# 运行测试
pip install pytest pytest-asyncio
pytest
```

### 故障排除
| 问题 | 解决方案 |
|------|----------|
| HTTP 404 错误 | 确保使用正确的端点 URL |
| 连接被拒绝 | 检查服务器是否启动，端口是否正确 |
| 会话问题 | 确保包含正确的 `Mcp-Session-Id` 头 |

使用 `curl -v` 查看详细的 HTTP 交互信息。

## 🛠️ 技术栈

| 组件 | 用途 |
|------|------|
| **Python 3.8+** | 主要编程语言 |
| **MCP SDK** | Model Context Protocol 官方 Python SDK |
| **FastMCP** | 高级 MCP 服务器框架 |
| **feedparser** | RSS 解析 |
| **PyYAML** | YAML 配置文件解析 |
| **uvicorn** | ASGI 服务器 (HTTP 传输) |
| **asyncio** | 异步编程 |

## 🔄 从旧版本迁移

如果你之前使用的是 `news_mcp.py` 启动方式，请按以下步骤迁移：

1. **更新启动命令**：
   ```bash
   # 旧方式
   python news_mcp.py --transport streamable-http --port 8000

   # 新方式
   python -m src.main --transport streamable-http --port 8000
   ```

2. **配置文件**：新版本使用 `config/` 目录下的 YAML 配置文件，你可以删除旧的 `news_mcp.py` 文件。

3. **功能保持不变**：所有 MCP 工具和 API 接口保持完全兼容。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**快速链接**: [安装](#-快速开始) | [启动服务器](#启动服务器) | [MCP 工具](#-mcp-工具) | [HTTP API](#-http-api-使用)
