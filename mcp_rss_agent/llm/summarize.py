from __future__ import annotations

import os
import asyncio
from typing import List

from openai import AsyncOpenAI

from mcp_rss_agent.mcp.schema import NewsItem


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

def is_enabled() -> bool:
    return bool(OPENAI_API_KEY)


async def refine_items(items: List[NewsItem]) -> List[NewsItem]:
    if not is_enabled() or not items:
        return items

    async with AsyncOpenAI(api_key=OPENAI_API_KEY) as client:
        async def refine(item: NewsItem) -> None:
            prompt = f"请用中文简要概括以下新闻: {item.summary or item.title}"
            try:
                resp = await client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": prompt}],
                )
                item.summary = resp.choices[0].message.content.strip()
            except Exception:  # noqa: BLE001
                pass

        await asyncio.gather(*(refine(item) for item in items))
    return items
