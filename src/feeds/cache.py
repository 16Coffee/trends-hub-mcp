"""
缓存管理模块
负责RSS源内容的缓存管理
"""

import time
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """缓存条目"""
    data: List[Dict[str, Any]]
    timestamp: float
    ttl: int  # 生存时间（秒）
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return time.time() - self.timestamp > self.ttl


class FeedCache:
    """RSS源缓存管理器"""
    
    def __init__(self, default_ttl: int = 300, max_size: int = 100):
        """
        初始化缓存管理器
        
        Args:
            default_ttl: 默认缓存时间（秒）
            max_size: 最大缓存条目数
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取缓存内容
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的数据，如果不存在或过期则返回None
        """
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            
            if entry.is_expired():
                del self._cache[key]
                return None
            
            return entry.data
    
    async def set(self, key: str, data: List[Dict[str, Any]], ttl: Optional[int] = None) -> None:
        """
        设置缓存内容
        
        Args:
            key: 缓存键
            data: 要缓存的数据
            ttl: 缓存时间，如果为None则使用默认值
        """
        async with self._lock:
            # 如果缓存已满，删除最旧的条目
            if len(self._cache) >= self.max_size:
                oldest_key = min(self._cache.keys(), 
                               key=lambda k: self._cache[k].timestamp)
                del self._cache[oldest_key]
            
            self._cache[key] = CacheEntry(
                data=data,
                timestamp=time.time(),
                ttl=ttl or self.default_ttl
            )
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存条目
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功删除
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def clear(self) -> None:
        """清空所有缓存"""
        async with self._lock:
            self._cache.clear()
    
    async def cleanup_expired(self) -> int:
        """
        清理过期缓存
        
        Returns:
            清理的条目数量
        """
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        return {
            "total_entries": len(self._cache),
            "max_size": self.max_size,
            "default_ttl": self.default_ttl,
            "cache_keys": list(self._cache.keys())
        }


# 全局缓存实例
_global_cache: Optional[FeedCache] = None


def get_cache() -> FeedCache:
    """获取全局缓存实例"""
    global _global_cache
    if _global_cache is None:
        _global_cache = FeedCache()
    return _global_cache


def init_cache(default_ttl: int = 300, max_size: int = 100) -> FeedCache:
    """
    初始化全局缓存
    
    Args:
        default_ttl: 默认缓存时间
        max_size: 最大缓存大小
        
    Returns:
        缓存实例
    """
    global _global_cache
    _global_cache = FeedCache(default_ttl, max_size)
    return _global_cache
