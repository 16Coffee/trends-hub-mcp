import os
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from mcp_rss_agent.mcp.transport import create_http_app
from mcp_rss_agent.main import handle_message

BASE_DIR = Path(__file__).parent


@pytest.mark.asyncio
async def test_http():
    env = os.environ.copy()
    env["FEED_URLS"] = f"file://{(BASE_DIR / 'tests_data' / 'feed.xml').resolve()}"
    os.environ.update(env)
    app = create_http_app(handle_message)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        req = {
            "id": "1",
            "type": "request",
            "action": "hot_news",
            "payload": {},
            "ts": "2024-01-01T00:00:00Z",
        }
        resp = await ac.post("/mcp", json=req)
        data = resp.json()
        assert data["type"] == "response"
        assert len(data["payload"]["items"]) == 2
