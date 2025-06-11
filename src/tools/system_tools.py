"""
系统工具模块
包含健康检查等系统相关的MCP工具
"""

import logging
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP

from ..config.settings import AppConfig
from ..feeds.manager import FeedManager

logger = logging.getLogger(__name__)


def register_system_tools(mcp: FastMCP, config: AppConfig, feed_manager: FeedManager):
    """注册系统工具"""
    
    @mcp.tool()
    async def health_check() -> Dict[str, Any]:
        """检查新闻 MCP 服务器的健康状态和运行情况。"""
        try:
            # 获取缓存统计
            cache_stats = feed_manager.cache.get_stats()
            
            # 获取可用分类数量
            categories = feed_manager.get_available_categories()
            
            # 计算总的RSS源数量
            total_feeds = sum(
                len(feeds) for feeds in feed_manager.get_all_feeds().values()
            )
            
            return {
                "status": "healthy",
                "server_info": {
                    "name": config.server.name,
                    "version": config.server.version,
                    "description": config.server.description
                },
                "feeds_info": {
                    "total_feeds": total_feeds,
                    "categories_available": len(categories),
                    "categories": categories
                },
                "cache_info": {
                    "enabled": config.cache.enabled,
                    "entries": cache_stats["total_entries"],
                    "max_size": cache_stats["max_size"],
                    "default_ttl": cache_stats["default_ttl"]
                },
                "limits": {
                    "max_articles_per_feed": config.limits.max_articles_per_feed,
                    "default_article_limit": config.limits.default_article_limit,
                    "max_search_results": config.limits.max_search_results
                }
            }
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "server_info": {
                    "name": config.server.name,
                    "version": config.server.version
                }
            }
    
    @mcp.tool()
    async def list_available_feeds() -> Dict[str, Any]:
        """列出所有可用的新闻源及其分类。"""
        try:
            all_feeds = feed_manager.get_all_feeds()
            categories = feed_manager.get_available_categories()
            
            feeds_info = {}
            total_feeds = 0
            
            for category in categories:
                feeds = feed_manager.get_feeds_by_category(category)
                feeds_info[category] = [
                    {
                        "name": feed.name,
                        "description": feed.description,
                        "url": feed.url
                    }
                    for feed in feeds
                ]
                total_feeds += len(feeds)
            
            return {
                "total_feeds": total_feeds,
                "total_categories": len(categories),
                "categories": list(categories),
                "feeds_by_category": feeds_info,
                "config": {
                    "cache_duration": config.feeds.cache_duration,
                    "max_articles_per_feed": config.feeds.max_articles,
                    "default_limit": config.feeds.default_limit
                }
            }
        except Exception as e:
            logger.error(f"列出RSS源失败: {e}")
            return {
                "error": str(e),
                "total_feeds": 0,
                "total_categories": 0,
                "categories": [],
                "feeds_by_category": {}
            }
