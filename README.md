# MCP RSS Agent

该服务通过 MCP 协议提供热点新闻汇总，可通过 `stdin/stdout` 或 HTTP 模式运行。

## 环境变量
- `FEED_URLS`：逗号分隔的 RSS 地址列表。
- `OPENAI_API_KEY`：可选，用于摘要精炼。

## 运行

```bash
# stdio 模式
python -m mcp_rss_agent.main --mode stdio

# http 模式
python -m mcp_rss_agent.main --mode http --port 8080
```

## Docker

```bash
docker build -t mcp_rss_agent .
docker run -e FEED_URLS="https://example.com/rss" -p 8080:8080 mcp_rss_agent
```
