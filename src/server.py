"""
MCP服务器模块
负责创建和配置MCP服务器
"""

import logging
from mcp.server.fastmcp import FastMCP

from .config.settings import AppConfig
from .feeds.manager import FeedManager
from .feeds.cache import init_cache
from .tools.manager import ToolManager

logger = logging.getLogger(__name__)


def create_server(config: AppConfig) -> FastMCP:
    """
    创建和配置MCP服务器
    
    Args:
        config: 应用程序配置
        
    Returns:
        配置好的FastMCP服务器实例
    """
    # 创建MCP服务器
    mcp = FastMCP(config.server.name)
    
    # 初始化缓存
    init_cache(
        default_ttl=config.cache.duration,
        max_size=config.cache.max_size
    )
    
    # 创建RSS源管理器
    feed_manager = FeedManager(config.feeds)

    # 创建工具管理器并注册工具
    tool_manager = ToolManager(config, feed_manager)
    tool_manager.register_tools(mcp)
    
    # 配置HTTP路由（如果需要）
    _setup_http_routes(mcp, config)
    
    logger.info(f"MCP服务器 '{config.server.name}' 创建完成")
    return mcp


def _setup_http_routes(mcp: FastMCP, config: AppConfig):
    """设置HTTP路由"""
    
    @mcp.custom_route("/", methods=["GET", "POST"])
    async def root_handler(request):
        from starlette.responses import HTMLResponse, RedirectResponse
        
        if request.method == "GET":
            # GET 请求返回信息页面
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{config.server.name}</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ color: #2c3e50; }}
                    .info {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
                    .endpoint {{ background: #e9ecef; padding: 10px; margin: 10px 0; border-radius: 3px; }}
                    code {{ background: #f1f3f4; padding: 2px 4px; border-radius: 3px; }}
                </style>
            </head>
            <body>
                <h1 class="header">{config.server.name}</h1>
                <p>{config.server.description}</p>
                
                <div class="info">
                    <h2>服务器信息</h2>
                    <ul>
                        <li><strong>版本:</strong> {config.server.version}</li>
                        <li><strong>协议版本:</strong> 2024-11-05</li>
                        <li><strong>缓存:</strong> {'启用' if config.cache.enabled else '禁用'}</li>
                    </ul>
                </div>
                
                <div class="info">
                    <h2>MCP 端点</h2>
                    <div class="endpoint">
                        <strong>Streamable HTTP:</strong> <code>/mcp</code>
                    </div>
                    <div class="endpoint">
                        <strong>SSE:</strong> <code>/sse</code> (连接) + <code>/messages</code> (消息)
                    </div>
                </div>
                
                <div class="info">
                    <h2>可用工具</h2>
                    <ul>
                        <li><code>health_check</code> - 检查服务器健康状态</li>
                        <li><code>list_available_feeds</code> - 列出所有RSS源</li>
                        <li><code>get_latest_news</code> - 获取最新新闻</li>
                        <li><code>search_news</code> - 搜索新闻文章</li>
                        <li><code>get_feed_content</code> - 获取特定源内容</li>
                        <li><code>get_article_details</code> - 获取文章详情</li>
                    </ul>
                </div>
                
                <div class="info">
                    <h2>配置说明</h2>
                    <p>在您的 MCP 客户端中配置以下 URL:</p>
                    <ul>
                        <li><code>http://{config.transport.http_host}:{config.transport.http_port}/mcp</code> (推荐)</li>
                        <li><code>http://{config.transport.http_host}:{config.transport.http_port}/</code> (自动重定向)</li>
                    </ul>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        else:  # POST 和其他方法
            # POST 请求重定向到 /mcp
            return RedirectResponse(url="/mcp", status_code=307)
    
    @mcp.custom_route("/favicon.ico", methods=["GET"])
    async def favicon_handler(request):
        from starlette.responses import Response
        return Response(status_code=204)


def setup_logging(config: AppConfig):
    """设置日志配置"""
    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        format=config.logging.format,
        handlers=[
            logging.FileHandler(config.logging.file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 设置特定模块的日志级别
    logging.getLogger("feedparser").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
