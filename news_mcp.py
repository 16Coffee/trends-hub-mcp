"""
News MCP Server - Provides news information from various feeds

This MCP server exposes tools to fetch and search news from RSS feeds.
It follows the Model Context Protocol (MCP) standard for AI assistant integration.

Author: Your Name
License: MIT
Version: 1.0.0
"""

import os
import logging
import argparse
from typing import Any, List, Dict, Optional
import feedparser
from mcp.server.fastmcp import FastMCP
import asyncio
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("news_mcp.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("news_mcp")

# Initialize FastMCP server
mcp = FastMCP("news", description="Access news articles from various RSS feeds")

# Define your RSS feed URLs
RSS_FEEDS = {
    "wired": "https://www.wired.com/feed/rss",
    "nytimes": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
    "cnbc": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "guardian": "https://www.theguardian.com/world/rss",
    "wsj": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "theverge": "https://www.theverge.com/rss/index.xml",
    "tech": "https://www.cnet.com/rss/news/",
    "nasa": "https://www.nasa.gov/news-release/feed/",
    "travel": "https://www.theguardian.com/uk/travel/rss",
    "business": "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml",
    "politics": "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
    "science": "https://www.sciencemag.org/rss/news_current.xml"
}

# Load custom feeds from environment variable if available
def load_custom_feeds():
    """Load custom RSS feeds from environment variables."""
    try:
        custom_feeds_env = os.environ.get("NEWS_MCP_CUSTOM_FEEDS", "")
        if custom_feeds_env:
            custom_feeds = {}
            feed_entries = custom_feeds_env.split(";")
            for entry in feed_entries:
                if ":" in entry:
                    name, url = entry.split(":", 1)
                    custom_feeds[name.strip()] = url.strip()
            
            if custom_feeds:
                logger.info(f"Loaded {len(custom_feeds)} custom feeds from environment")
                return custom_feeds
    except Exception as e:
        logger.error(f"Error loading custom feeds: {e}")
    
    return {}

# Add custom feeds if available
RSS_FEEDS.update(load_custom_feeds())

# Category mappings
CATEGORIES = {
    "tech": ["wired", "theverge", "tech"],
    "general": ["nytimes", "bbc", "guardian"],
    "business": ["cnbc", "wsj", "business"],
    "science": ["nasa", "science"],
    "travel": ["travel"],
    "politics": ["politics"]
}

# Constants
MAX_FEEDS_PER_REQUEST = 3
DEFAULT_ARTICLE_LIMIT = 5
MAX_ARTICLE_LIMIT = 20
CACHE_DURATION = 300  # seconds

# Cache for RSS feeds to avoid frequent requests
feed_cache = {}

# Helper functions
async def fetch_rss_feed(feed_url: str, limit: int = DEFAULT_ARTICLE_LIMIT) -> List[Dict[str, Any]]:
    """Fetch articles from an RSS feed with caching."""
    try:
        # Check cache first
        current_time = time.time()
        if feed_url in feed_cache:
            cache_time, cache_data = feed_cache[feed_url]
            if current_time - cache_time < CACHE_DURATION:
                logger.debug(f"Using cached data for {feed_url}")
                return cache_data[:limit]
        
        logger.info(f"Fetching RSS feed: {feed_url}")
        feed = feedparser.parse(feed_url)
        articles = []
        
        for entry in feed.entries[:MAX_ARTICLE_LIMIT]:  # Cache more than needed
            article = {
                "title": entry.title,
                "link": entry.link,
                "summary": entry.get("summary", "No summary available"),
                "published": entry.get("published", "No date available"),
                "feed_url": feed_url
            }
            articles.append(article)
        
        # Update cache
        feed_cache[feed_url] = (current_time, articles)
        
        return articles[:limit]
    except Exception as e:
        error_msg = f"Error fetching RSS feed {feed_url}: {e}"
        logger.error(error_msg)
        return []

def format_article(article: Dict[str, Any]) -> str:
    """Format an article dictionary into a readable string."""
    return f"""
Title: {article.get('title', 'Unknown title')}
Published: {article.get('published', 'Unknown date')}
Source: {article.get('source', 'Unknown source')}
Link: {article.get('link', 'No link available')}
Summary: {article.get('summary', 'No summary available')}
"""

# Health check
@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """检查新闻 MCP 服务器的健康状态和运行情况。"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "feeds_available": len(RSS_FEEDS),
        "categories_available": len(CATEGORIES)
    }

# MCP Tools
@mcp.tool()
async def list_available_feeds() -> Dict[str, Any]:
    """列出所有可用的新闻源及其分类。"""
    logger.info("Listing available feeds")
    
    # Create a structured response
    result = {
        "all_feeds": sorted(RSS_FEEDS.keys()),
        "categories": {}
    }
    
    # Add feeds by category
    for category, feeds in sorted(CATEGORIES.items()):
        # Filter to only include feeds that exist in RSS_FEEDS
        valid_feeds = [feed for feed in feeds if feed in RSS_FEEDS]
        result["categories"][category] = valid_feeds
    
    return result

@mcp.tool()
async def get_latest_news(category: Optional[str] = None, limit: int = DEFAULT_ARTICLE_LIMIT) -> Dict[str, Any]:
    """从 RSS 源获取最新新闻文章。

    参数:
        category: 可选的分类过滤器 (tech, general, business, science, travel, politics)。
                 如果为 None，则从所有源中获取样本。
        limit: 返回文章的最大数量 (默认: 5, 最大: 20)
    """
    # Validate limit
    if limit > MAX_ARTICLE_LIMIT:
        limit = MAX_ARTICLE_LIMIT
    
    logger.info(f"Getting latest news for category: {category}, limit: {limit}")
    
    # Determine which feeds to fetch from
    feeds_to_fetch = []
    if category is None:
        # Use a sample of feeds if no category specified (1 from each category)
        for cat_feeds in CATEGORIES.values():
            if cat_feeds:
                feeds_to_fetch.append(cat_feeds[0])
    elif category.lower() in CATEGORIES:
        # Use feeds from the specified category
        feeds_to_fetch = [feed for feed in CATEGORIES[category.lower()] if feed in RSS_FEEDS]
    else:
        return {
            "error": f"Invalid category: {category}",
            "available_categories": list(CATEGORIES.keys()),
            "articles": []
        }
    
    # Limit to max feeds per request to avoid too many requests
    feeds_to_fetch = feeds_to_fetch[:MAX_FEEDS_PER_REQUEST]
    
    # Fetch articles in parallel
    fetch_tasks = []
    for feed_name in feeds_to_fetch:
        if feed_name in RSS_FEEDS:
            fetch_tasks.append(fetch_rss_feed(RSS_FEEDS[feed_name], limit))
    
    if not fetch_tasks:
        return {"articles": [], "message": "No feeds available to fetch"}
    
    # Wait for all fetches to complete
    results = await asyncio.gather(*fetch_tasks)
    
    # Combine and process results
    all_articles = []
    for i, articles in enumerate(results):
        feed_name = feeds_to_fetch[i] if i < len(feeds_to_fetch) else "unknown"
        for article in articles:
            article["source"] = feed_name
            all_articles.append(article)
    
    # Sort by published date (if available)
    all_articles = sorted(
        all_articles, 
        key=lambda x: x.get("published", ""), 
        reverse=True
    )[:limit]
    
    if not all_articles:
        return {"articles": [], "message": "No news articles found"}
    
    # Return structured data
    return {
        "articles": all_articles,
        "count": len(all_articles),
        "sources": list(set(article["source"] for article in all_articles)),
        "category": category
    }

@mcp.tool()
async def search_news(query: str, limit: int = DEFAULT_ARTICLE_LIMIT) -> Dict[str, Any]:
    """搜索匹配查询条件的新闻文章。

    参数:
        query: 在新闻文章中搜索的关键词
        limit: 返回文章的最大数量 (默认: 5, 最大: 20)
    """
    # Validate limit
    if limit > MAX_ARTICLE_LIMIT:
        limit = MAX_ARTICLE_LIMIT
    
    if not query:
        return {
            "error": "Search query cannot be empty",
            "articles": []
        }
    
    logger.info(f"Searching news for query: {query}, limit: {limit}")
    
    # Fetch articles in parallel (more to search through)
    fetch_tasks = []
    for feed_name, feed_url in RSS_FEEDS.items():
        fetch_tasks.append(fetch_rss_feed(feed_url, MAX_ARTICLE_LIMIT))
    
    if not fetch_tasks:
        return {"articles": [], "message": "No feeds available to search"}
    
    # Wait for all fetches to complete
    results = await asyncio.gather(*fetch_tasks)
    
    # Combine and process results
    all_articles = []
    feed_names = list(RSS_FEEDS.keys())
    
    for i, articles in enumerate(results):
        feed_name = feed_names[i] if i < len(feed_names) else "unknown"
        for article in articles:
            article["source"] = feed_name
            # Check if query is in title or summary
            if (query.lower() in article.get("title", "").lower() or 
                query.lower() in article.get("summary", "").lower()):
                all_articles.append(article)
    
    # Sort and limit results
    all_articles = sorted(
        all_articles, 
        key=lambda x: x.get("published", ""), 
        reverse=True
    )[:limit]
    
    if not all_articles:
        return {
            "articles": [], 
            "message": f"No news articles found matching '{query}'",
            "query": query
        }
    
    # Return structured data
    return {
        "articles": all_articles,
        "count": len(all_articles),
        "query": query,
        "sources": list(set(article["source"] for article in all_articles))
    }

@mcp.tool()
async def get_feed_content(feed_name: str, limit: int = DEFAULT_ARTICLE_LIMIT) -> Dict[str, Any]:
    """从指定的新闻源获取文章。

    参数:
        feed_name: 要获取的新闻源名称 (使用 list_available_feeds 查看可选项)
        limit: 返回文章的最大数量 (默认: 5, 最大: 20)
    """
    # Validate limit
    if limit > MAX_ARTICLE_LIMIT:
        limit = MAX_ARTICLE_LIMIT
    
    logger.info(f"Getting feed content for: {feed_name}, limit: {limit}")
    
    if feed_name not in RSS_FEEDS:
        return {
            "error": f"Feed '{feed_name}' not found",
            "available_feeds": sorted(RSS_FEEDS.keys()),
            "articles": []
        }
    
    feed_url = RSS_FEEDS[feed_name]
    articles = await fetch_rss_feed(feed_url, limit)
    
    if not articles:
        return {
            "articles": [],
            "message": f"No articles found in the '{feed_name}' feed",
            "feed": feed_name
        }
    
    # Add source to each article
    for article in articles:
        article["source"] = feed_name
    
    # Return structured data
    return {
        "articles": articles,
        "count": len(articles),
        "feed": feed_name,
        "feed_url": feed_url
    }

@mcp.tool()
async def get_article_details(url: str) -> Dict[str, Any]:
    """通过 URL 获取特定文章的详细信息。

    参数:
        url: 要获取详细信息的文章 URL
    """
    logger.info(f"Getting article details for URL: {url}")
    
    # Find the feed that might contain this article
    found_article = None
    
    # Fetch from multiple feeds in parallel
    fetch_tasks = []
    for feed_name, feed_url in RSS_FEEDS.items():
        fetch_tasks.append((feed_name, fetch_rss_feed(feed_url, 20)))  # Check more articles
    
    for feed_name, task in fetch_tasks:
        articles = await task
        for article in articles:
            if article.get("link") == url:
                article["source"] = feed_name
                found_article = article
                break
        if found_article:
            break
    
    if not found_article:
        return {
            "error": f"Article with URL '{url}' not found in any of the feeds",
            "url": url
        }
    
    # Return the article details
    return {
        "article": found_article,
        "source": found_article.get("source", "Unknown source"),
        "url": url
    }

# Main entry point
def run_server(transport: str = 'stdio', host: str = '127.0.0.1', port: int = 8000):
    """Run the News MCP server.

    Args:
        transport: Transport protocol ('stdio', 'sse', 'streamable-http')
        host: Host address for HTTP transports
        port: Port number for HTTP transports
    """
    logger.info(f"Starting News MCP Server with {transport} transport...")

    if transport == 'stdio':
        mcp.run(transport='stdio')
    elif transport == 'sse':
        logger.info(f"SSE server will be available at http://{host}:{port}/sse")
        # 设置服务器配置
        mcp.settings.host = host
        mcp.settings.port = port
        mcp.run(transport='sse')
    elif transport == 'streamable-http':
        logger.info(f"Streamable HTTP server will be available at http://{host}:{port}/mcp")
        logger.info(f"Root endpoint redirect available at http://{host}:{port}/")
        # 设置服务器配置
        mcp.settings.host = host
        mcp.settings.port = port

        # 添加根路径处理
        @mcp.custom_route("/", methods=["GET", "POST"])
        async def root_handler(request):
            from starlette.responses import HTMLResponse, RedirectResponse

            if request.method == "GET":
                # GET 请求返回信息页面
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>News MCP Server</title>
                    <meta charset="utf-8">
                </head>
                <body>
                    <h1>News MCP Server</h1>
                    <p>服务器正在运行中...</p>
                    <h2>MCP 端点信息</h2>
                    <ul>
                        <li><strong>Streamable HTTP 端点:</strong> <a href="/mcp">/mcp</a></li>
                        <li><strong>服务器地址:</strong> http://{host}:{port}</li>
                        <li><strong>协议版本:</strong> 2024-11-05</li>
                    </ul>
                    <h2>使用说明</h2>
                    <p>请在您的 MCP 客户端中配置以下 URL:</p>
                    <code>http://{host}:{port}/mcp</code>
                    <p>或者使用根路径，服务器会自动处理:</p>
                    <code>http://{host}:{port}/</code>
                </body>
                </html>
                """
                return HTMLResponse(content=html_content)
            else:  # POST 和其他方法
                # POST 请求重定向到 /mcp
                return RedirectResponse(url="/mcp", status_code=307)

        # 添加 favicon 处理
        @mcp.custom_route("/favicon.ico", methods=["GET"])
        async def favicon_handler(request):
            from starlette.responses import Response
            return Response(status_code=204)

        mcp.run(transport='streamable-http')
    else:
        raise ValueError(f"Unsupported transport: {transport}")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="News MCP Server - RSS新闻聚合服务器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
传输协议说明:
  stdio           - 标准输入输出协议 (默认，适用于本地工具)
  sse             - Server-Sent Events协议 (适用于Web集成)
  streamable-http - 流式HTTP协议 (推荐用于Web部署)

示例:
  python news_mcp.py                                    # 使用stdio协议
  python news_mcp.py --transport sse                    # 使用SSE协议，默认端口8000
  python news_mcp.py --transport streamable-http --port 3000  # 使用HTTP协议，端口3000
        """
    )

    parser.add_argument(
        '--transport', '-t',
        choices=['stdio', 'sse', 'streamable-http'],
        default='stdio',
        help='传输协议 (默认: stdio)'
    )

    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='HTTP服务器主机地址 (默认: 127.0.0.1)'
    )

    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8000,
        help='HTTP服务器端口 (默认: 8000)'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别 (默认: INFO)'
    )

    return parser.parse_args()

if __name__ == "__main__":
    # 解析命令行参数
    args = parse_args()

    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    logger.setLevel(getattr(logging, args.log_level))

    # 启动服务器
    try:
        run_server(
            transport=args.transport,
            host=args.host,
            port=args.port
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise