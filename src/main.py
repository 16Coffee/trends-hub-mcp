"""
News MCP Server 主入口点
"""

import argparse
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import load_config
from src.server import create_server, setup_logging

logger = logging.getLogger(__name__)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="News MCP Server - RSS新闻聚合服务器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
传输协议说明:
  stdio           - 标准输入输出协议 (默认，适用于本地工具)
  sse             - Server-Sent Events协议 (适用于Web集成)
  streamable-http - 流式HTTP协议 (推荐用于Web部署)

示例:
  python -m src.main                                    # 使用stdio协议
  python -m src.main --transport sse                    # 使用SSE协议，默认端口8000
  python -m src.main --transport streamable-http --port 3000  # 使用HTTP协议，端口3000
        """
    )
    
    parser.add_argument(
        '--transport', '-t',
        choices=['stdio', 'sse', 'streamable-http'],
        default=None,
        help='传输协议 (默认: 从配置文件读取)'
    )
    
    parser.add_argument(
        '--host',
        default=None,
        help='HTTP服务器主机地址 (默认: 从配置文件读取)'
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=None,
        help='HTTP服务器端口 (默认: 从配置文件读取)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default=None,
        help='日志级别 (默认: 从配置文件读取)'
    )
    
    parser.add_argument(
        '--config-dir',
        default='config',
        help='配置文件目录 (默认: config)'
    )
    
    return parser.parse_args()


def run_server(transport: str, host: str, port: int, config):
    """运行服务器"""
    logger.info(f"启动 News MCP Server，传输协议: {transport}")

    # 创建服务器
    mcp = create_server(config)

    if transport == 'stdio':
        logger.info("使用 stdio 传输协议")
        mcp.run(transport='stdio')
    elif transport == 'sse':
        logger.info(f"SSE 服务器将在 http://{host}:{port}/sse 启动")
        mcp.settings.host = host
        mcp.settings.port = port
        mcp.run(transport='sse')
    elif transport == 'streamable-http':
        logger.info(f"Streamable HTTP 服务器将在 http://{host}:{port}/mcp 启动")
        logger.info(f"状态页面: http://{host}:{port}/")
        mcp.settings.host = host
        mcp.settings.port = port
        mcp.run(transport='streamable-http')
    elif transport == 'multi':
        logger.info(f"多协议服务器将在 http://{host}:{port} 启动")
        logger.info(f"SSE 端点: http://{host}:{port}/sse")
        logger.info(f"Streamable HTTP 端点: http://{host}:{port}/mcp")
        logger.info(f"状态页面: http://{host}:{port}/")
        run_multi_protocol_server(mcp, host, port)
    else:
        raise ValueError(f"不支持的传输协议: {transport}")


def main():
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_args()
        
        # 加载配置
        from src.config.settings import ConfigLoader
        config_loader = ConfigLoader(args.config_dir)
        config = config_loader.load_config()
        
        # 命令行参数覆盖配置文件
        transport = args.transport or config.transport.default
        host = args.host or config.transport.http_host
        port = args.port or config.transport.http_port
        
        # 设置日志级别
        if args.log_level:
            config.logging.level = args.log_level
        
        # 初始化日志
        setup_logging(config)
        
        logger.info("=" * 50)
        logger.info("News MCP Server 启动中...")
        logger.info(f"配置目录: {args.config_dir}")
        logger.info(f"传输协议: {transport}")
        if transport != 'stdio':
            logger.info(f"服务器地址: {host}:{port}")
        logger.info("=" * 50)
        
        # 启动服务器
        run_server(transport, host, port, config)
        
    except KeyboardInterrupt:
        logger.info("服务器被用户停止")
    except FileNotFoundError as e:
        logger.error(f"配置文件错误: {e}")
        logger.error("请确保配置文件存在于指定目录中")
        sys.exit(1)
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        logger.exception("详细错误信息:")
        sys.exit(1)


if __name__ == "__main__":
    main()
