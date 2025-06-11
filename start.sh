#!/bin/sh
MODE=${MODE:-http}
PORT=${PORT:-8080}

exec python -m mcp_rss_agent.main --mode "$MODE" --port "$PORT"
