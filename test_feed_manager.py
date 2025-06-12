#!/usr/bin/env python3
"""
测试FeedManager修复后的功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import load_config
from src.feeds.manager import FeedManager


async def test_feed_manager():
    """测试FeedManager的各个方法"""
    print("🚀 开始测试FeedManager...")
    
    # 加载配置
    config = load_config("config")
    feed_manager = FeedManager(config.feeds)
    
    # 1. 测试获取所有文章
    print("\n📰 测试获取所有文章...")
    try:
        articles = await feed_manager.fetch_all_feeds(limit=3)
        print(f"✅ 成功获取 {len(articles)} 篇文章")
        if articles:
            print(f"第一篇文章标题: {articles[0].get('title', '无标题')}")
    except Exception as e:
        print(f"❌ 获取文章失败: {e}")
    
    # 2. 测试搜索功能
    print("\n🔍 测试搜索功能...")
    try:
        # 先获取一些文章
        all_articles = await feed_manager.fetch_all_feeds(limit=10)
        if all_articles:
            # 测试搜索（不传递limit参数）
            search_results = feed_manager.search_articles(all_articles, "技术")
            print(f"✅ 搜索'技术'找到 {len(search_results)} 篇文章")
        else:
            print("⚠️ 没有文章可供搜索")
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
    
    # 3. 测试获取文章详情
    print("\n📄 测试获取文章详情...")
    try:
        # 先获取一些文章
        all_articles = await feed_manager.fetch_all_feeds(limit=5)
        if all_articles:
            test_url = all_articles[0].get('link')
            if test_url:
                article_details = await feed_manager.get_article_details(test_url)
                if article_details:
                    print(f"✅ 成功获取文章详情: {article_details.get('title', '无标题')}")
                else:
                    print("⚠️ 未找到文章详情")
            else:
                print("⚠️ 文章没有链接")
        else:
            print("⚠️ 没有文章可供测试")
    except Exception as e:
        print(f"❌ 获取文章详情失败: {e}")
    
    # 4. 测试按分类获取文章
    print("\n📂 测试按分类获取文章...")
    try:
        categories = feed_manager.get_available_categories()
        print(f"可用分类: {categories}")
        
        if categories:
            category = categories[0]
            articles = await feed_manager.fetch_feeds_by_category(category, limit=2)
            print(f"✅ 从分类'{category}'获取 {len(articles)} 篇文章")
    except Exception as e:
        print(f"❌ 按分类获取文章失败: {e}")
    
    print("\n✅ FeedManager测试完成!")


if __name__ == "__main__":
    asyncio.run(test_feed_manager())
