#!/bin/bash

# News MCP Server 启动脚本
# 确保使用正确的 Python 环境和路径

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 显示帮助信息
show_help() {
    echo "News MCP Server 启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -t, --transport PROTOCOL    传输协议 (stdio|sse|streamable-http, 默认: stdio)"
    echo "  -p, --port PORT            HTTP服务器端口 (默认: 8000)"
    echo "  --host HOST                HTTP服务器主机 (默认: 127.0.0.1)"
    echo "  --log-level LEVEL          日志级别 (DEBUG|INFO|WARNING|ERROR, 默认: INFO)"
    echo "  -h, --help                 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                                    # 使用stdio协议"
    echo "  $0 -t sse                            # 使用SSE协议"
    echo "  $0 -t streamable-http -p 3000        # 使用HTTP协议，端口3000"
    echo ""
}

# 检查帮助参数
for arg in "$@"; do
    if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
        show_help
        exit 0
    fi
done

# 激活虚拟环境并启动服务器
cd "$SCRIPT_DIR"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "错误: 虚拟环境不存在。请先运行以下命令创建虚拟环境:"
    echo "python -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

# 检查依赖是否安装
if ! python -c "import mcp, feedparser, uvicorn, yaml" 2>/dev/null; then
    echo "警告: 某些依赖可能未安装。正在尝试安装..."
    pip install -r requirements.txt
fi

# 启动服务器，传递所有参数
echo "启动 News MCP Server (重构版本)..."
python -m src.main "$@"
