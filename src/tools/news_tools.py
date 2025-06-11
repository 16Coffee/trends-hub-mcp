"""
新闻工具模块
包含新闻获取、搜索等相关的MCP工具
"""

import logging
from typing import Dict, Any, Optional, List
from mcp.server.fastmcp import FastMCP

from ..config.settings import AppConfig
from ..feeds.manager import FeedManager

logger = logging.getLogger(__name__)


def register_news_tools(mcp: FastMCP, config: AppConfig, feed_manager: FeedManager):
    """注册新闻工具"""
    
    @mcp.tool()
    async def get_latest_news(category: Optional[str] = None, limit: int = None) -> Dict[str, Any]:
        """从 RSS 源获取最新新闻文章。
        
        参数:
            category: 可选的分类过滤器 (tech, general, business, science, travel, politics)。
                     如果为 None，则从所有源中获取样本。
            limit: 返回文章的最大数量 (默认: 5, 最大: 20)
        """
        try:
            # 验证和设置限制
            if limit is None:
                limit = config.limits.default_article_limit
            limit = min(limit, config.limits.max_articles_per_feed)
            
            # 验证分类
            available_categories = feed_manager.get_available_categories()
            if category and category not in available_categories:
                return {
                    "error": f"无效的分类: {category}",
                    "available_categories": available_categories,
                    "articles": []
                }
            
            # 获取文章
            if category:
                articles = await feed_manager.fetch_feeds_by_category(category, limit)
                source_info = f"分类: {category}"
            else:
                # 从所有分类中获取样本
                articles = await feed_manager.fetch_all_feeds(limit)
                source_info = "所有分类"
            
            return {
                "source": source_info,
                "total_articles": len(articles),
                "limit": limit,
                "articles": articles
            }
            
        except Exception as e:
            logger.error(f"获取最新新闻失败: {e}")
            return {
                "error": str(e),
                "source": category or "所有分类",
                "total_articles": 0,
                "articles": []
            }
    
    @mcp.tool()
    async def search_news(query: str, limit: int = None) -> Dict[str, Any]:
        """搜索匹配查询条件的新闻文章。
        
        参数:
            query: 在新闻文章中搜索的关键词
            limit: 返回文章的最大数量 (默认: 5, 最大: 20)
        """
        try:
            # 验证查询参数
            if not query or not query.strip():
                return {
                    "error": "搜索查询不能为空",
                    "query": query,
                    "total_articles": 0,
                    "articles": []
                }
            
            # 验证和设置限制
            if limit is None:
                limit = config.limits.default_article_limit
            limit = min(limit, config.limits.max_search_results)
            
            # 获取所有文章进行搜索
            all_articles = await feed_manager.fetch_all_feeds()
            
            # 执行搜索
            matched_articles = feed_manager.search_articles(all_articles, query.strip())
            
            # 限制结果数量
            limited_articles = matched_articles[:limit]
            
            return {
                "query": query.strip(),
                "total_found": len(matched_articles),
                "total_returned": len(limited_articles),
                "limit": limit,
                "articles": limited_articles
            }
            
        except Exception as e:
            logger.error(f"搜索新闻失败: {e}")
            return {
                "error": str(e),
                "query": query,
                "total_found": 0,
                "total_returned": 0,
                "articles": []
            }
    
    @mcp.tool()
    async def get_feed_content(feed_name: str, limit: int = None) -> Dict[str, Any]:
        """从指定的新闻源获取文章。
        
        参数:
            feed_name: 要获取的新闻源名称 (使用 list_available_feeds 查看可选项)
            limit: 返回文章的最大数量 (默认: 5, 最大: 20)
        """
        try:
            # 验证和设置限制
            if limit is None:
                limit = config.limits.default_article_limit
            limit = min(limit, config.limits.max_articles_per_feed)
            
            # 查找指定的RSS源
            feed_source = None
            for category_feeds in feed_manager.get_all_feeds().values():
                for feed in category_feeds:
                    if feed.name == feed_name:
                        feed_source = feed
                        break
                if feed_source:
                    break
            
            if not feed_source:
                # 获取所有可用的RSS源名称
                all_feed_names = []
                for category_feeds in feed_manager.get_all_feeds().values():
                    all_feed_names.extend([feed.name for feed in category_feeds])
                
                return {
                    "error": f"未找到RSS源: {feed_name}",
                    "available_feeds": all_feed_names,
                    "articles": []
                }
            
            # 获取RSS源内容
            articles = await feed_manager.fetch_feed(feed_source, limit)
            
            return {
                "feed_name": feed_name,
                "feed_description": feed_source.description,
                "feed_url": feed_source.url,
                "total_articles": len(articles),
                "limit": limit,
                "articles": articles
            }
            
        except Exception as e:
            logger.error(f"获取RSS源内容失败: {e}")
            return {
                "error": str(e),
                "feed_name": feed_name,
                "total_articles": 0,
                "articles": []
            }
    
    @mcp.tool()
    async def get_article_details(url: str) -> Dict[str, Any]:
        """通过 URL 获取特定文章的详细信息。
        
        参数:
            url: 要获取详细信息的文章 URL
        """
        try:
            if not url or not url.strip():
                return {
                    "error": "文章URL不能为空",
                    "url": url,
                    "article": None
                }
            
            # 从所有缓存的文章中查找
            all_articles = await feed_manager.fetch_all_feeds()
            
            # 查找匹配的文章
            matching_article = None
            for article in all_articles:
                if article.get('link') == url.strip():
                    matching_article = article
                    break
            
            if not matching_article:
                return {
                    "error": f"未找到URL对应的文章: {url}",
                    "url": url,
                    "article": None,
                    "suggestion": "请确保URL正确，或者该文章可能已从RSS源中移除"
                }
            
            return {
                "url": url,
                "found": True,
                "article": matching_article
            }
            
        except Exception as e:
            logger.error(f"获取文章详情失败: {e}")
            return {
                "error": str(e),
                "url": url,
                "article": None
            }
