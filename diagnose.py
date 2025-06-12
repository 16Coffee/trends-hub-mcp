#!/usr/bin/env python3
"""
诊断RSS源访问问题
"""

import asyncio
import sys
import os
import feedparser
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import load_config


async def diagnose_feeds():
    """诊断RSS源访问问题"""
    print("🔍 开始诊断RSS源访问...")
    
    try:
        # 加载配置
        config = load_config()
        print(f"✅ 配置加载成功，共 {len(config.feeds.categories)} 个分类")
        
        # 测试每个RSS源
        total_feeds = 0
        working_feeds = 0
        
        for category, feeds in config.feeds.categories.items():
            print(f"\n📂 测试分类: {category}")
            
            for feed in feeds:
                total_feeds += 1
                print(f"  🔗 测试 {feed.name}: {feed.url}")
                
                try:
                    # 测试RSS源访问
                    start_time = time.time()
                    parsed_feed = feedparser.parse(feed.url)
                    end_time = time.time()
                    
                    if parsed_feed.bozo:
                        print(f"    ⚠️  解析警告: {parsed_feed.bozo_exception}")
                    
                    if hasattr(parsed_feed, 'entries') and len(parsed_feed.entries) > 0:
                        print(f"    ✅ 成功获取 {len(parsed_feed.entries)} 篇文章 ({end_time - start_time:.2f}s)")
                        working_feeds += 1
                        
                        # 显示第一篇文章标题
                        if parsed_feed.entries:
                            first_title = parsed_feed.entries[0].get('title', '无标题')
                            print(f"    📰 第一篇: {first_title[:50]}...")
                    else:
                        print(f"    ❌ 无法获取文章 ({end_time - start_time:.2f}s)")
                        
                except Exception as e:
                    print(f"    ❌ 访问失败: {e}")
        
        print(f"\n📊 诊断结果:")
        print(f"  总RSS源数: {total_feeds}")
        print(f"  正常工作: {working_feeds}")
        print(f"  失败数量: {total_feeds - working_feeds}")
        print(f"  成功率: {working_feeds/total_feeds*100:.1f}%")
        
        if working_feeds == 0:
            print("\n❌ 所有RSS源都无法访问，可能的原因:")
            print("  1. 网络连接问题")
            print("  2. 防火墙阻止外网访问")
            print("  3. 需要配置代理")
            print("  4. DNS解析问题")
        elif working_feeds < total_feeds:
            print(f"\n⚠️  部分RSS源无法访问，建议:")
            print("  1. 检查网络连接")
            print("  2. 考虑添加国内RSS源")
            print("  3. 配置代理服务器")
        else:
            print("\n✅ 所有RSS源都正常工作!")
            
    except Exception as e:
        print(f"❌ 诊断过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(diagnose_feeds())
