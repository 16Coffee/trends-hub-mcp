# MCP RSS Agent

该服务通过 MCP 协议提供热点新闻汇总，可通过 `stdin/stdout` 或 HTTP 模式运行。

## 环境变量
- `FEED_URLS`：逗号分隔的 RSS 地址列表。
- `OPENAI_API_KEY`：可选，用于摘要精炼。

## 运行

```bash
# stdio 模式
python -m mcp_rss_agent.main --mode stdio
# 需要从标准输入写入符合 MCP 格式的 JSON，例如：
echo '{"id":"1","type":"request","action":"hot_news","payload":{},"ts":"2024-01-01T00:00:00Z"}' \
  | python -m mcp_rss_agent.main --mode stdio

# http 模式
python -m mcp_rss_agent.main --mode http --port 8080
```

## Docker

```bash
docker build -t mcp_rss_agent .
docker run -e FEED_URLS="https://example.com/rss" -p 8080:8080 mcp_rss_agent
```

## MCP 配置文件

仓库根目录提供了示例 `mcp.json`，内容如下：

```json
{
  "mcpServers": {
    "interactive-feedback": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/yajun/Downloads/ai_project/interactive-feedback-mcp",
        "run",
        "server.py"
      ],
      "timeout": 600,
      "autoApprove": [
        "interactive_feedback"
      ]
    }
  }
}
```
