from __future__ import annotations

import os
import asyncio
from typing import List

import aiohttp
import feedparser
from tenacity import retry, stop_after_attempt, wait_fixed

from mcp_rss_agent.mcp.schema import NewsItem


def get_feed_urls() -> List[str]:
    urls = os.getenv("FEED_URLS", "").split(",")
    return [u.strip() for u in urls if u.strip()]


def get_timeout() -> int:
    return int(os.getenv("FETCH_TIMEOUT", "10"))


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def fetch(session: aiohttp.ClientSession, url: str) -> feedparser.FeedParserDict:
    if url.startswith("file://"):
        path = url[len("file://") :]
        with open(path, "rb") as f:
            data = f.read()
        return feedparser.parse(data)
    async with session.get(url) as resp:
        resp.raise_for_status()
        data = await resp.read()
        return feedparser.parse(data)


async def fetch_feeds() -> List[NewsItem]:
    urls = get_feed_urls()
    if not urls:
        return []

    timeout = aiohttp.ClientTimeout(total=get_timeout())
    async with aiohttp.ClientSession(timeout=timeout) as session:
        results = await asyncio.gather(*(fetch(session, url) for url in urls), return_exceptions=True)

    items: List[NewsItem] = []
    seen = set()
    for result in results:
        if isinstance(result, Exception):
            continue
        for entry in result.entries[:5]:
            link = entry.get("link")
            if not link or link in seen:
                continue
            seen.add(link)
            published = entry.get("published") or entry.get("updated")
            items.append(
                NewsItem(
                    title=entry.get("title", ""),
                    link=link,
                    published=published,
                    summary=entry.get("summary"),
                )
            )
    return items
