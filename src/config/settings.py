"""
配置管理模块
负责加载和管理服务器配置
"""

import os
import yaml
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """服务器配置"""
    name: str
    version: str
    description: str


@dataclass
class TransportConfig:
    """传输协议配置"""
    default: str
    http_host: str
    http_port: int
    sse_host: str
    sse_port: int


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str
    format: str
    file: str


@dataclass
class CacheConfig:
    """缓存配置"""
    enabled: bool
    duration: int
    max_size: int


@dataclass
class LimitsConfig:
    """限制配置"""
    max_articles_per_feed: int
    default_article_limit: int
    max_search_results: int
    request_timeout: int


@dataclass
class ToolsConfig:
    """工具配置"""
    enabled: List[str]
    groups: Dict[str, List[str]]


@dataclass
class FeedSource:
    """RSS源配置"""
    name: str
    url: str
    description: str


@dataclass
class FeedsConfig:
    """RSS源配置"""
    categories: Dict[str, List[FeedSource]]
    cache_duration: int
    max_articles: int
    default_limit: int
    max_feeds_per_request: int


@dataclass
class AppConfig:
    """应用程序完整配置"""
    server: ServerConfig
    transport: TransportConfig
    logging: LoggingConfig
    cache: CacheConfig
    limits: LimitsConfig
    tools: ToolsConfig
    feeds: FeedsConfig


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        
    def load_config(self) -> AppConfig:
        """加载完整配置"""
        server_config = self._load_server_config()
        feeds_config = self._load_feeds_config()
        
        # 处理环境变量覆盖
        tools_config = self._override_tools_config(server_config.tools)

        return AppConfig(
            server=server_config.server,
            transport=server_config.transport,
            logging=server_config.logging,
            cache=server_config.cache,
            limits=server_config.limits,
            tools=tools_config,
            feeds=feeds_config
        )
    
    def _load_server_config(self) -> Any:
        """加载服务器配置"""
        config_file = self.config_dir / "server.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"服务器配置文件不存在: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return type('ServerConfigData', (), {
            'server': ServerConfig(**data['server']),
            'transport': TransportConfig(
                default=data['transport']['default'],
                http_host=data['transport']['http']['host'],
                http_port=data['transport']['http']['port'],
                sse_host=data['transport']['sse']['host'],
                sse_port=data['transport']['sse']['port']
            ),
            'logging': LoggingConfig(**data['logging']),
            'cache': CacheConfig(**data['cache']),
            'limits': LimitsConfig(**data['limits']),
            'tools': ToolsConfig(**data['tools'])
        })()
    
    def _load_feeds_config(self) -> FeedsConfig:
        """加载RSS源配置"""
        config_file = self.config_dir / "feeds.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"RSS源配置文件不存在: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # 解析分类和RSS源
        categories = {}
        for category, feeds in data['categories'].items():
            categories[category] = [
                FeedSource(**feed) for feed in feeds
            ]
        
        # 加载自定义RSS源（从环境变量）
        custom_feeds = self._load_custom_feeds()
        if custom_feeds:
            categories['custom'] = custom_feeds
        
        return FeedsConfig(
            categories=categories,
            cache_duration=data['defaults']['cache_duration'],
            max_articles=data['defaults']['max_articles'],
            default_limit=data['defaults']['default_limit'],
            max_feeds_per_request=data['defaults']['max_feeds_per_request']
        )
    
    def _load_custom_feeds(self) -> Optional[List[FeedSource]]:
        """从环境变量加载自定义RSS源"""
        custom_feeds_env = os.getenv('NEWS_MCP_CUSTOM_FEEDS')
        if not custom_feeds_env:
            return None
        
        feeds = []
        for feed_pair in custom_feeds_env.split(';'):
            if ':' in feed_pair:
                name, url = feed_pair.split(':', 1)
                feeds.append(FeedSource(
                    name=name.strip(),
                    url=url.strip(),
                    description=f"自定义RSS源: {name.strip()}"
                ))
        
        return feeds if feeds else None

    def _override_tools_config(self, tools_config: ToolsConfig) -> ToolsConfig:
        """使用环境变量覆盖工具配置"""
        enabled_tools_env = os.getenv('ENABLED_TOOLS', '').strip()

        if enabled_tools_env:
            # 从环境变量解析启用的工具
            enabled_tools = [tool.strip() for tool in enabled_tools_env.split(',') if tool.strip()]
            logger.info(f"从环境变量覆盖启用的工具: {enabled_tools}")

            return ToolsConfig(
                enabled=enabled_tools,
                groups=tools_config.groups
            )

        return tools_config


# 全局配置加载器实例
_config_loader = ConfigLoader()


def load_config() -> AppConfig:
    """加载应用程序配置"""
    return _config_loader.load_config()


def get_all_feeds() -> Dict[str, List[FeedSource]]:
    """获取所有RSS源"""
    config = load_config()
    return config.feeds.categories


def get_feeds_by_category(category: str) -> List[FeedSource]:
    """根据分类获取RSS源"""
    all_feeds = get_all_feeds()
    return all_feeds.get(category, [])
