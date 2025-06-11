from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone

from mcp_rss_agent.mcp.schema import MCPMessage, HotNewsPayload
from mcp_rss_agent.mcp.transport import handle_stdio, create_http_app
from mcp_rss_agent.feeds.fetcher import fetch_feeds


async def handle_message(msg: MCPMessage) -> MCPMessage:
    if msg.action != "hot_news":
        return MCPMessage(id=msg.id, type="error", action=msg.action, payload={"error": "unsupported action"}, ts=datetime.now(timezone.utc))

    items = await fetch_feeds()
    payload = HotNewsPayload(items=items)
    return MCPMessage(id=msg.id, type="response", action="hot_news", payload=payload.model_dump(mode="json"), ts=datetime.now(timezone.utc))


def run_stdio():
    asyncio.run(handle_stdio(handle_message))


def run_http(port: int):
    import uvicorn

    app = create_http_app(handle_message)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["stdio", "http"], required=True)
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    if args.mode == "stdio":
        run_stdio()
    else:
        run_http(args.port)
