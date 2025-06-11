from __future__ import annotations

import os
from typing import List

import openai

from mcp_rss_agent.mcp.schema import NewsItem


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

def is_enabled() -> bool:
    return bool(OPENAI_API_KEY)


async def refine_items(items: List[NewsItem]) -> List[NewsItem]:
    if not is_enabled() or not items:
        return items

    openai.api_key = OPENAI_API_KEY
    for item in items:
        prompt = f"请用中文简要概括以下新闻: {item.summary or item.title}"
        try:
            response = await openai.ChatCompletion.acreate(model=MODEL, messages=[{"role": "user", "content": prompt}])
            item.summary = response.choices[0].message.content.strip()
        except Exception:  # noqa: BLE001
            continue
    return items
