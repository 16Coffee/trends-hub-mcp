#!/usr/bin/env python3
"""
调试新闻获取问题
"""

import asyncio
import sys
import os
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import ConfigLoader
from src.feeds.manager import FeedManager

# 设置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def debug_news_fetch():
    """调试新闻获取"""
    print("🔍 开始调试新闻获取问题...")
    
    try:
        # 加载配置
        print("📋 加载配置...")
        config_loader = ConfigLoader()
        config = config_loader.load_config()
        
        print(f"✅ 配置加载成功:")
        print(f"  - 总分类数: {len(config.feeds.categories)}")
        total_feeds = sum(len(feeds) for feeds in config.feeds.categories.values())
        print(f"  - 总RSS源数: {total_feeds}")
        print(f"  - 默认限制: {config.feeds.default_limit}")
        
        # 创建RSS管理器
        print("\n🔧 创建RSS管理器...")
        feed_manager = FeedManager(config.feeds)
        
        # 测试单个RSS源
        print("\n🎯 测试单个RSS源 (wired)...")
        wired_feed = None
        for feeds in config.feeds.categories.values():
            for feed in feeds:
                if feed.name == 'wired':
                    wired_feed = feed
                    break
            if wired_feed:
                break
        
        if wired_feed:
            print(f"📡 获取 {wired_feed.name} ({wired_feed.url})...")
            articles = await feed_manager.fetch_feed(wired_feed, limit=3)
            print(f"📰 获取到 {len(articles)} 篇文章")
            
            if articles:
                for i, article in enumerate(articles, 1):
                    print(f"  {i}. {article.get('title', 'No title')[:50]}...")
                    print(f"     时间戳: {article.get('published_timestamp', 'No timestamp')}")
            else:
                print("❌ 没有获取到文章")
        else:
            print("❌ 未找到 wired RSS源")
        
        # 测试平衡获取
        print("\n🎯 测试平衡获取 (限制5条)...")
        balanced_articles = await feed_manager.fetch_all_feeds_balanced(limit=5)
        print(f"📰 平衡获取到 {len(balanced_articles)} 篇文章")
        
        if balanced_articles:
            source_count = {}
            for i, article in enumerate(balanced_articles, 1):
                source = article.get('source', 'Unknown')
                source_count[source] = source_count.get(source, 0) + 1
                print(f"  {i}. [{source}] {article.get('title', 'No title')[:50]}...")
                print(f"     时间戳: {article.get('published_timestamp', 'No timestamp')}")
            
            print(f"\n📊 各源分布:")
            for source, count in sorted(source_count.items()):
                print(f"  - {source}: {count} 篇")
        else:
            print("❌ 平衡获取没有获取到文章")
        
        # 测试传统获取
        print("\n🎯 测试传统获取 (限制5条)...")
        traditional_articles = await feed_manager.fetch_all_feeds(limit=5)
        print(f"📰 传统获取到 {len(traditional_articles)} 篇文章")
        
        if traditional_articles:
            for i, article in enumerate(traditional_articles, 1):
                source = article.get('source', 'Unknown')
                print(f"  {i}. [{source}] {article.get('title', 'No title')[:50]}...")
        else:
            print("❌ 传统获取没有获取到文章")
            
    except Exception as e:
        print(f"❌ 调试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_news_fetch())
