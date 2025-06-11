from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
import sys
from typing import Callable, Awaitable

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .schema import MCPMessage


async def handle_stdio(handler: Callable[[MCPMessage], Awaitable[MCPMessage]]):
    loop = asyncio.get_running_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    writer_transport, writer_protocol = await loop.connect_write_pipe(asyncio.streams.FlowControlMixin, sys.stdout)
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, loop)

    while True:
        line = await reader.readline()
        if not line:
            break
        data: dict | None = None
        try:
            data = json.loads(line)
            msg = MCPMessage.model_validate(data)
            response = await handler(msg)
            writer.write((response.model_dump_json() + "\n").encode())
            await writer.drain()
        except Exception as exc:  # noqa: BLE001
            msg_id = data.get("id", "") if isinstance(data, dict) else ""
            err = MCPMessage(
                id=msg_id,
                type="error",
                action="hot_news",
                payload={"error": str(exc)},
                ts=datetime.now(timezone.utc),
            )
            writer.write((err.model_dump_json() + "\n").encode())
            await writer.drain()


def create_http_app(handler: Callable[[MCPMessage], Awaitable[MCPMessage]]) -> FastAPI:
    app = FastAPI()

    @app.post("/mcp")
    async def mcp_endpoint(msg: MCPMessage) -> JSONResponse:
        resp = await handler(msg)
        return JSONResponse(resp.model_dump(mode="json"))

    return app
