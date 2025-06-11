"""
RSS源管理模块
负责RSS源的获取、解析和管理
"""

import asyncio
import logging
import feedparser
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..config.settings import FeedSource, FeedsConfig
from .cache import get_cache


logger = logging.getLogger(__name__)


class FeedManager:
    """RSS源管理器"""
    
    def __init__(self, config: FeedsConfig):
        """
        初始化RSS源管理器
        
        Args:
            config: RSS源配置
        """
        self.config = config
        self.cache = get_cache()
        
    async def fetch_feed(self, feed_source: FeedSource, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取单个RSS源的内容
        
        Args:
            feed_source: RSS源配置
            limit: 文章数量限制
            
        Returns:
            文章列表
        """
        cache_key = f"feed:{feed_source.name}"
        
        # 尝试从缓存获取
        cached_data = await self.cache.get(cache_key)
        if cached_data is not None:
            logger.debug(f"从缓存获取RSS源: {feed_source.name}")
            return cached_data[:limit] if limit else cached_data
        
        try:
            logger.info(f"获取RSS源: {feed_source.name} ({feed_source.url})")
            
            # 在线程池中执行RSS解析（避免阻塞）
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, feed_source.url)
            
            if feed.bozo:
                logger.warning(f"RSS源解析警告: {feed_source.name} - {feed.bozo_exception}")
            
            articles = []
            max_articles = limit or self.config.max_articles
            
            for entry in feed.entries[:max_articles]:
                article = self._parse_entry(entry, feed_source.name)
                if article:
                    articles.append(article)
            
            # 缓存结果
            await self.cache.set(cache_key, articles, self.config.cache_duration)
            
            logger.info(f"成功获取 {len(articles)} 篇文章从 {feed_source.name}")
            return articles
            
        except Exception as e:
            logger.error(f"获取RSS源失败: {feed_source.name} - {e}")
            return []
    
    async def fetch_feeds_by_category(self, category: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        根据分类获取RSS源内容
        
        Args:
            category: 分类名称
            limit: 文章数量限制
            
        Returns:
            文章列表
        """
        feeds = self.config.categories.get(category, [])
        if not feeds:
            logger.warning(f"未找到分类: {category}")
            return []
        
        # 限制并发请求数量
        max_feeds = min(len(feeds), self.config.max_feeds_per_request)
        selected_feeds = feeds[:max_feeds]
        
        # 并发获取多个RSS源
        tasks = [
            self.fetch_feed(feed, limit)
            for feed in selected_feeds
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果
        all_articles = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"获取RSS源失败: {selected_feeds[i].name} - {result}")
            else:
                all_articles.extend(result)
        
        # 按发布时间排序
        all_articles.sort(key=lambda x: x.get('published_timestamp', 0), reverse=True)
        
        return all_articles[:limit] if limit else all_articles
    
    async def fetch_all_feeds(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取所有RSS源的内容
        
        Args:
            limit: 文章数量限制
            
        Returns:
            文章列表
        """
        all_articles = []
        
        for category in self.config.categories.keys():
            articles = await self.fetch_feeds_by_category(category, limit)
            all_articles.extend(articles)
        
        # 按发布时间排序并限制数量
        all_articles.sort(key=lambda x: x.get('published_timestamp', 0), reverse=True)
        
        return all_articles[:limit] if limit else all_articles
    
    def search_articles(self, articles: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        在文章中搜索关键词
        
        Args:
            articles: 文章列表
            query: 搜索关键词
            
        Returns:
            匹配的文章列表
        """
        query_lower = query.lower()
        matched_articles = []
        
        for article in articles:
            # 在标题、摘要和内容中搜索
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            content = article.get('content', '').lower()
            
            if (query_lower in title or 
                query_lower in summary or 
                query_lower in content):
                matched_articles.append(article)
        
        return matched_articles
    
    def _parse_entry(self, entry: Any, feed_name: str) -> Optional[Dict[str, Any]]:
        """
        解析RSS条目
        
        Args:
            entry: RSS条目
            feed_name: RSS源名称
            
        Returns:
            解析后的文章信息
        """
        try:
            # 解析发布时间
            published_timestamp = 0
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                import time
                published_timestamp = time.mktime(entry.published_parsed)
            
            article = {
                'title': getattr(entry, 'title', '无标题'),
                'link': getattr(entry, 'link', ''),
                'summary': getattr(entry, 'summary', ''),
                'published': getattr(entry, 'published', ''),
                'published_timestamp': published_timestamp,
                'feed_name': feed_name,
                'author': getattr(entry, 'author', ''),
                'tags': [tag.term for tag in getattr(entry, 'tags', [])],
                'content': ''
            }
            
            # 提取内容
            if hasattr(entry, 'content') and entry.content:
                article['content'] = entry.content[0].value if entry.content else ''
            elif hasattr(entry, 'description'):
                article['content'] = entry.description
            
            return article
            
        except Exception as e:
            logger.error(f"解析RSS条目失败: {e}")
            return None
    
    def get_available_categories(self) -> List[str]:
        """获取可用的分类列表"""
        return list(self.config.categories.keys())
    
    def get_feeds_by_category(self, category: str) -> List[FeedSource]:
        """根据分类获取RSS源列表"""
        return self.config.categories.get(category, [])
    
    def get_all_feeds(self) -> Dict[str, List[FeedSource]]:
        """获取所有RSS源"""
        return self.config.categories
