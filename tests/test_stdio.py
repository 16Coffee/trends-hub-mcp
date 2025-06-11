import json
import os
import subprocess
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).parent


@pytest.mark.asyncio
async def test_stdio():
    env = os.environ.copy()
    env["FEED_URLS"] = f"file://{(BASE_DIR / 'tests_data' / 'feed.xml').resolve()}"
    proc = subprocess.Popen([
        "python",
        "-m",
        "mcp_rss_agent.main",
        "--mode",
        "stdio",
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env, text=True)

    req = {
        "id": "1",
        "type": "request",
        "action": "hot_news",
        "payload": {},
        "ts": "2024-01-01T00:00:00Z",
    }
    proc.stdin.write(json.dumps(req) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    proc.terminate()
    resp = json.loads(line)
    assert resp["type"] == "response"
    assert resp["action"] == "hot_news"
    assert len(resp["payload"]["items"]) == 2
