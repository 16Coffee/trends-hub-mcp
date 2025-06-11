from __future__ import annotations

import os
import asyncio
from typing import List, Callable, Awaitable

import aiohttp
import feedparser
from tenacity import retry, stop_after_attempt, wait_fixed

from mcp_rss_agent.mcp.schema import NewsItem

# 默认的 RSS 源，覆盖环境变量 FEED_URLS 可自定义
DEFAULT_FEED_URLS = {
    "wallstreetcn": "https://rsshub.app/wallstreetcn/news/global",
    "nytimes": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "bbc": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "washpost": "https://feeds.washingtonpost.com/rss/world",
    "xinhua": "https://rsshub.app/xinhua/world",
    "people": "https://rsshub.app/people/opinion",
}




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


# 针对每个站点构建独立的抓取工具
async def fetch_wallstreetcn(session: aiohttp.ClientSession) -> feedparser.FeedParserDict:
    return await fetch(session, DEFAULT_FEED_URLS["wallstreetcn"])


async def fetch_nytimes(session: aiohttp.ClientSession) -> feedparser.FeedParserDict:
    return await fetch(session, DEFAULT_FEED_URLS["nytimes"])


async def fetch_bbc(session: aiohttp.ClientSession) -> feedparser.FeedParserDict:
    return await fetch(session, DEFAULT_FEED_URLS["bbc"])


async def fetch_washpost(session: aiohttp.ClientSession) -> feedparser.FeedParserDict:
    return await fetch(session, DEFAULT_FEED_URLS["washpost"])


async def fetch_xinhua(session: aiohttp.ClientSession) -> feedparser.FeedParserDict:
    return await fetch(session, DEFAULT_FEED_URLS["xinhua"])


async def fetch_people(session: aiohttp.ClientSession) -> feedparser.FeedParserDict:
    return await fetch(session, DEFAULT_FEED_URLS["people"])


TOOLS: List[Callable[[aiohttp.ClientSession], Awaitable[feedparser.FeedParserDict]]] = [
    fetch_wallstreetcn,
    fetch_nytimes,
    fetch_bbc,
    fetch_washpost,
    fetch_xinhua,
    fetch_people,
]


async def fetch_feeds() -> List[NewsItem]:
    env = os.getenv("FEED_URLS")
    timeout = aiohttp.ClientTimeout(total=get_timeout())
    async with aiohttp.ClientSession(timeout=timeout) as session:
        if env:
            urls = [u.strip() for u in env.split(",") if u.strip()]
            tasks = [fetch(session, url) for url in urls]
        else:
            tasks = [tool(session) for tool in TOOLS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

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
