"""
工具管理器模块
负责根据配置动态注册MCP工具
"""

import logging
import time
from typing import Set, List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

from ..config.settings import AppConfig
from ..feeds.manager import FeedManager

logger = logging.getLogger(__name__)


class ToolManager:
    """工具管理器"""
    
    # 定义所有可用的工具
    ALL_TOOLS = {
        # 系统工具
        'health_check': 'system',
        'list_available_feeds': 'system',
        
        # 新闻工具
        'get_latest_news': 'news',
        'search_news': 'news',
        'get_feed_content': 'news',
        'get_article_details': 'news',
    }
    
    def __init__(self, config: AppConfig, feed_manager: FeedManager):
        self.config = config
        self.feed_manager = feed_manager
        self.tools_config = config.tools
        self.enabled_tools = self._get_enabled_tools()
        
    def _get_enabled_tools(self) -> Set[str]:
        """获取启用的工具列表"""
        if not self.tools_config.enabled:
            # 如果配置为空，启用所有工具
            logger.info("工具配置为空，启用所有工具")
            return set(self.ALL_TOOLS.keys())
        
        enabled = set(self.tools_config.enabled)
        
        # 验证工具名称
        invalid_tools = enabled - set(self.ALL_TOOLS.keys())
        if invalid_tools:
            logger.warning(f"配置中包含无效的工具: {invalid_tools}")
            enabled -= invalid_tools
        
        logger.info(f"启用的工具: {sorted(enabled)}")
        return enabled
    
    def register_tools(self, mcp: FastMCP) -> None:
        """注册启用的工具"""
        logger.info("开始注册MCP工具...")
        
        # 获取需要注册的工具分组
        system_tools = self._get_tools_by_group('system')
        news_tools = self._get_tools_by_group('news')
        
        # 注册系统工具
        if system_tools:
            logger.info(f"注册系统工具: {sorted(system_tools)}")
            self._register_system_tools_selective(mcp, system_tools)
        
        # 注册新闻工具
        if news_tools:
            logger.info(f"注册新闻工具: {sorted(news_tools)}")
            self._register_news_tools_selective(mcp, news_tools)
        
        logger.info(f"工具注册完成，共注册 {len(self.enabled_tools)} 个工具")
    
    def _get_tools_by_group(self, group: str) -> Set[str]:
        """获取指定分组中启用的工具"""
        group_tools = set()
        for tool_name, tool_group in self.ALL_TOOLS.items():
            if tool_group == group and tool_name in self.enabled_tools:
                group_tools.add(tool_name)
        return group_tools
    
    def _register_system_tools_selective(self, mcp: FastMCP, enabled_tools: Set[str]) -> None:
        """选择性注册系统工具"""
        
        if 'health_check' in enabled_tools:
            @mcp.tool()
            async def health_check() -> Dict[str, Any]:
                """
                检查新闻 MCP 服务器的健康状态和运行情况。

                返回服务器状态信息，包括版本、可用源数量、缓存统计等。
                """
                try:
                    # 获取缓存统计
                    cache_stats = self.feed_manager.cache.get_stats()
                    
                    # 获取可用分类数量
                    categories = self.feed_manager.get_available_categories()
                    
                    # 计算总的RSS源数量
                    total_feeds = sum(
                        len(feeds) for feeds in self.feed_manager.get_all_feeds().values()
                    )
                    
                    return {
                        "status": "healthy",
                        "version": self.config.server.version,
                        "server_name": self.config.server.name,
                        "feeds_available": total_feeds,
                        "categories_available": len(categories),
                        "cache_stats": {
                            "hits": cache_stats.get("hits", 0),
                            "misses": cache_stats.get("misses", 0),
                            "size": cache_stats.get("size", 0),
                            "max_size": cache_stats.get("max_size", 0)
                        },
                        "config": {
                            "cache_enabled": self.config.cache.enabled,
                            "cache_duration": self.config.cache.duration,
                            "max_articles_per_feed": self.config.limits.max_articles_per_feed,
                            "default_limit": self.config.limits.default_article_limit
                        },
                        "enabled_tools": sorted(self.enabled_tools)
                    }
                except Exception as e:
                    logger.error(f"健康检查失败: {e}")
                    return {
                        "status": "error",
                        "error": str(e),
                        "version": self.config.server.version,
                        "server_name": self.config.server.name
                    }
        
        if 'list_available_feeds' in enabled_tools:
            @mcp.tool()
            async def list_available_feeds() -> Dict[str, Any]:
                """
                列出所有可用的新闻源及其分类。

                返回所有配置的RSS新闻源信息，按分类组织。
                """
                try:
                    all_feeds = self.feed_manager.get_all_feeds()
                    categories = self.feed_manager.get_available_categories()
                    
                    feeds_info = {}
                    total_feeds = 0
                    
                    for category in categories:
                        feeds = self.feed_manager.get_feeds_by_category(category)
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
                            "cache_duration": self.config.feeds.cache_duration,
                            "max_articles_per_feed": self.config.feeds.max_articles,
                            "default_limit": self.config.feeds.default_limit
                        }
                    }
                except Exception as e:
                    logger.error(f"获取RSS源列表失败: {e}")
                    return {
                        "error": f"获取RSS源列表失败: {str(e)}",
                        "total_feeds": 0,
                        "total_categories": 0,
                        "categories": [],
                        "feeds_by_category": {}
                    }
    
    def _register_news_tools_selective(self, mcp: FastMCP, enabled_tools: Set[str]) -> None:
        """选择性注册新闻工具"""
        
        if 'get_latest_news' in enabled_tools:
            @mcp.tool()
            async def get_latest_news(category: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
                """
                从 RSS 源获取最新新闻文章。

                参数:
                    category (str, 可选): 新闻分类过滤，可选值: tech, general, business, science, travel, politics
                    limit (int, 可选): 返回文章数量限制，默认5条，最大20条

                返回:
                    包含文章列表、总数、分类和时间戳的字典
                """
                try:
                    logger.info(f"get_latest_news 开始执行，category={category}, limit={limit}")

                    # 使用配置的默认限制
                    if limit is None:
                        limit = self.config.limits.default_article_limit

                    # 限制最大文章数量
                    limit = min(limit, self.config.limits.max_articles_per_feed)

                    logger.info(f"处理后的参数：category={category}, limit={limit}")

                    # 获取文章 - 使用平衡获取方法，每个源随机取1-2条
                    if category:
                        logger.info(f"按分类获取文章：{category}（平衡模式：每个源随机1-2条）")
                        articles = await self.feed_manager.fetch_feeds_by_category_balanced(
                            category=category,
                            limit=limit
                        )
                    else:
                        logger.info("获取所有文章（平衡模式：每个源随机1-2条）")
                        articles = await self.feed_manager.fetch_all_feeds_balanced(
                            limit=limit
                        )

                    logger.info(f"成功获取 {len(articles)} 篇文章")
                    
                    return {
                        "articles": articles,
                        "total_count": len(articles),
                        "category": category or "all",
                        "limit": limit,
                        "timestamp": time.time()
                    }
                    
                except Exception as e:
                    logger.error(f"获取最新新闻失败: {e}")
                    return {
                        "error": f"获取最新新闻失败: {str(e)}",
                        "articles": [],
                        "total_count": 0,
                        "category": category or "all",
                        "limit": limit or self.config.limits.default_article_limit
                    }
        
        if 'search_news' in enabled_tools:
            @mcp.tool()
            async def search_news(query: str, limit: Optional[int] = None) -> Dict[str, Any]:
                """
                在新闻文章中搜索匹配查询的内容。

                参数:
                    query (str, 必需): 搜索关键词，不能为空
                    limit (int, 可选): 返回结果数量限制，默认5条，最大50条

                返回:
                    包含匹配文章列表、总数、查询词和时间戳的字典
                """
                try:
                    if not query or not query.strip():
                        return {
                            "error": "搜索查询不能为空",
                            "articles": [],
                            "total_count": 0,
                            "query": query,
                            "limit": limit or self.config.limits.default_article_limit
                        }
                    
                    # 使用配置的默认限制
                    if limit is None:
                        limit = self.config.limits.default_article_limit
                    
                    # 限制最大搜索结果数量
                    limit = min(limit, self.config.limits.max_search_results)
                    
                    # 先获取所有文章，然后搜索
                    all_articles = await self.feed_manager.fetch_all_feeds()
                    articles = self.feed_manager.search_articles(
                        articles=all_articles,
                        query=query.strip()
                    )

                    # 限制结果数量
                    if limit:
                        articles = articles[:limit]
                    
                    return {
                        "articles": articles,
                        "total_count": len(articles),
                        "query": query.strip(),
                        "limit": limit,
                        "timestamp": time.time()
                    }
                    
                except Exception as e:
                    logger.error(f"搜索新闻失败: {e}")
                    return {
                        "error": f"搜索新闻失败: {str(e)}",
                        "articles": [],
                        "total_count": 0,
                        "query": query,
                        "limit": limit or self.config.limits.default_article_limit
                    }
        
        if 'get_feed_content' in enabled_tools:
            @mcp.tool()
            async def get_feed_content(feed_name: str, limit: Optional[int] = None) -> Dict[str, Any]:
                """
                获取特定新闻源的文章内容。

                参数:
                    feed_name (str, 必需): 新闻源名称，不能为空
                    limit (int, 可选): 返回文章数量限制，默认5条，最大20条

                返回:
                    包含指定源的文章列表、总数、源名称和时间戳的字典
                """
                try:
                    if not feed_name or not feed_name.strip():
                        return {
                            "error": "新闻源名称不能为空",
                            "articles": [],
                            "total_count": 0,
                            "feed_name": feed_name,
                            "limit": limit or self.config.limits.default_article_limit
                        }
                    
                    # 使用配置的默认限制
                    if limit is None:
                        limit = self.config.limits.default_article_limit
                    
                    # 限制最大文章数量
                    limit = min(limit, self.config.limits.max_articles_per_feed)
                    
                    # 查找指定的RSS源
                    feed_source = None
                    for category_feeds in self.feed_manager.get_all_feeds().values():
                        for feed in category_feeds:
                            if feed.name == feed_name.strip():
                                feed_source = feed
                                break
                        if feed_source:
                            break

                    if not feed_source:
                        return {
                            "success": False,
                            "error": f"未找到名为 '{feed_name.strip()}' 的RSS源",
                            "available_feeds": [
                                feed.name for feeds in self.feed_manager.get_all_feeds().values()
                                for feed in feeds
                            ]
                        }

                    # 获取特定源的文章
                    articles = await self.feed_manager.fetch_feed(
                        feed_source=feed_source,
                        limit=limit
                    )
                    
                    return {
                        "articles": articles,
                        "total_count": len(articles),
                        "feed_name": feed_name.strip(),
                        "limit": limit,
                        "timestamp": time.time()
                    }
                    
                except Exception as e:
                    logger.error(f"获取新闻源内容失败: {e}")
                    return {
                        "error": f"获取新闻源内容失败: {str(e)}",
                        "articles": [],
                        "total_count": 0,
                        "feed_name": feed_name,
                        "limit": limit or self.config.limits.default_article_limit
                    }
        
        if 'get_article_details' in enabled_tools:
            @mcp.tool()
            async def get_article_details(url: str) -> Dict[str, Any]:
                """
                通过URL获取文章的详细信息。

                参数:
                    url (str, 必需): 文章的完整URL地址，不能为空

                返回:
                    包含文章详细信息、URL和查找状态的字典
                """
                try:
                    if not url or not url.strip():
                        return {
                            "error": "文章URL不能为空",
                            "url": url
                        }
                    
                    # 获取文章详情
                    article = await self.feed_manager.get_article_details(url.strip())

                    if article:
                        return {
                            "article": article,
                            "url": url.strip(),
                            "found": True,
                            "timestamp": time.time()
                        }
                    else:
                        return {
                            "error": "未找到指定URL的文章",
                            "url": url.strip(),
                            "found": False
                        }
                    
                except Exception as e:
                    logger.error(f"获取文章详情失败: {e}")
                    return {
                        "error": f"获取文章详情失败: {str(e)}",
                        "url": url,
                        "found": False
                    }
    
    def get_enabled_tools_info(self) -> Dict[str, Any]:
        """获取启用工具的信息"""
        return {
            "enabled_tools": sorted(self.enabled_tools),
            "total_enabled": len(self.enabled_tools),
            "total_available": len(self.ALL_TOOLS),
            "tools_by_group": {
                group: sorted(self._get_tools_by_group(group))
                for group in set(self.ALL_TOOLS.values())
            }
        }
