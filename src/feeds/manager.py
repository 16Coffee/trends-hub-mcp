"""
RSS源管理模块
负责RSS源的获取、解析和管理
"""

import asyncio
import logging
import feedparser
import time
import random
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Dict, List, Any, Optional

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
        获取单个RSS源的内容，与旧版本逻辑保持一致

        Args:
            feed_source: RSS源配置
            limit: 文章数量限制

        Returns:
            文章列表
        """
        cache_key = f"feed:{feed_source.url}"

        # 检查缓存（简化版本，类似旧版本）
        cached_data = await self.cache.get(cache_key)
        if cached_data is not None:
            logger.debug(f"从缓存获取RSS源: {feed_source.name}")
            return cached_data[:limit] if limit else cached_data

        try:
            logger.info(f"获取RSS源: {feed_source.name} ({feed_source.url})")

            # 在线程池中执行RSS解析（避免阻塞）
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, feed_source.url)

            # 添加网络诊断信息
            if hasattr(feed, 'status'):
                logger.debug(f"RSS响应状态: {feed.status}")
            if hasattr(feed, 'headers') and feed.headers:
                try:
                    logger.debug(f"RSS响应头: {dict(feed.headers)}")
                except Exception:
                    logger.debug(f"RSS响应头: {feed.headers}")

            if feed.bozo:
                logger.warning(f"RSS源解析警告: {feed_source.name} - {feed.bozo_exception}")

            articles = []
            max_articles = limit or 20  # 类似旧版本的 MAX_ARTICLE_LIMIT

            for entry in feed.entries[:max_articles]:
                article = self._parse_entry(entry, feed_source.name)
                if article:
                    article["feed_url"] = feed_source.url
                    articles.append(article)

            # 缓存结果
            await self.cache.set(cache_key, articles, self.config.cache_duration)

            logger.info(f"成功获取 {len(articles)} 篇文章从 {feed_source.name}")
            return articles[:limit] if limit else articles

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

    async def fetch_all_feeds_balanced(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        平衡地从所有RSS源获取内容，每个源随机取1-2条文章

        Args:
            limit: 文章数量限制

        Returns:
            文章列表
        """
        all_articles = []

        # 收集所有RSS源
        all_feeds = []
        for category_feeds in self.config.categories.values():
            all_feeds.extend(category_feeds)

        # 随机打乱源的顺序，增加多样性
        random.shuffle(all_feeds)

        # 并发获取所有源的内容
        tasks = []
        for feed in all_feeds:
            # 每个源获取更多文章，后面再随机选择
            tasks.append(self.fetch_feed(feed, 10))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 从每个源随机选择1-2篇文章
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"获取RSS源失败: {all_feeds[i].name} - {result}")
                continue

            if result and isinstance(result, list) and len(result) > 0:  # 如果有文章
                # 随机选择1-2篇文章
                num_articles = min(random.randint(1, 2), len(result))
                selected_articles = random.sample(result, num_articles)
                all_articles.extend(selected_articles)

        # 按发布时间排序
        all_articles.sort(key=lambda x: x.get('published_timestamp', 0), reverse=True)

        # 限制最终数量
        return all_articles[:limit] if limit else all_articles

    async def fetch_feeds_by_category_balanced(self, category: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        平衡地根据分类获取RSS源内容，每个源随机取1-2条文章

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

        # 随机打乱源的顺序
        feeds_shuffled = feeds.copy()
        random.shuffle(feeds_shuffled)

        # 并发获取所有源的内容
        tasks = []
        for feed in feeds_shuffled:
            # 每个源获取更多文章，后面再随机选择
            tasks.append(self.fetch_feed(feed, 10))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 从每个源随机选择1-2篇文章
        all_articles = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"获取RSS源失败: {feeds_shuffled[i].name} - {result}")
                continue

            if result and isinstance(result, list) and len(result) > 0:  # 如果有文章
                # 随机选择1-2篇文章
                num_articles = min(random.randint(1, 2), len(result))
                selected_articles = random.sample(result, num_articles)
                all_articles.extend(selected_articles)

        # 按发布时间排序
        all_articles.sort(key=lambda x: x.get('published_timestamp', 0), reverse=True)

        # 限制最终数量
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
        解析RSS条目，与旧版本保持一致

        Args:
            entry: RSS条目
            feed_name: RSS源名称

        Returns:
            解析后的文章信息
        """
        try:
            # 解析发布时间
            published_str = getattr(entry, 'published', 'No date available')
            published_timestamp = 0

            if published_str != 'No date available':
                try:
                    # 尝试解析RSS时间格式
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_timestamp = time.mktime(entry.published_parsed)
                    else:
                        # 尝试使用email.utils解析
                        dt = parsedate_to_datetime(published_str)
                        published_timestamp = dt.timestamp()
                except Exception as e:
                    logger.debug(f"解析时间失败 {published_str}: {e}")
                    # 使用当前时间作为后备
                    published_timestamp = time.time()
            else:
                # 如果没有时间信息，使用当前时间
                published_timestamp = time.time()

            article = {
                "title": getattr(entry, 'title', '无标题'),
                "link": getattr(entry, 'link', ''),
                "summary": getattr(entry, 'summary', 'No summary available'),
                "published": published_str,
                "published_timestamp": published_timestamp,
                "source": feed_name,
                "feed_url": ""  # 这个会在调用时设置
            }

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

    async def get_article_details(self, url: str) -> Optional[Dict[str, Any]]:
        """
        通过URL获取文章详细信息

        Args:
            url: 文章URL

        Returns:
            文章详细信息，如果未找到则返回None
        """
        try:
            # 从所有缓存的文章中查找
            all_articles = await self.fetch_all_feeds()

            # 查找匹配的文章
            for article in all_articles:
                if article.get('link') == url:
                    return article

            logger.warning(f"未找到URL对应的文章: {url}")
            return None

        except Exception as e:
            logger.error(f"获取文章详情失败: {e}")
            return None
