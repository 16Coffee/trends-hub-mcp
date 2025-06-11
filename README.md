# MCP RSS Agent

该服务通过 MCP 协议提供热点新闻汇总，可通过 `stdin/stdout` 或 HTTP 模式运行。

## 默认来源
内置抓取以下媒体的 RSS：华尔街见闻、纽约时报、BBC News、Washington Post、新华网、人民日报。
如需自定义可通过 `FEED_URLS` 环境变量覆盖。

## 运行

```bash
# 安装依赖
pip install -r requirements.txt

# stdio 模式
python -m mcp_rss_agent.main --mode stdio
# 需要从标准输入写入符合 MCP 格式的 JSON，例如：
echo '{"id":"1","type":"request","action":"hot_news","payload":{},"ts":"2024-01-01T00:00:00Z"}' \
  | python -m mcp_rss_agent.main --mode stdio

# http 模式
python -m mcp_rss_agent.main --mode http --port 8080
# 通过 curl 发送 MCP 请求
curl -X POST http://localhost:8080/mcp \
  -H 'Content-Type: application/json' \
  -d '{"id":"1","type":"request","action":"hot_news","payload":{},"ts":"2024-01-01T00:00:00Z"}'
```

## Docker

```bash
docker build -t mcp_rss_agent .
docker run -p 8080:8080 mcp_rss_agent
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
