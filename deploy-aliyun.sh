#!/bin/bash

# 阿里云 ECS 部署脚本
# 针对中国大陆网络环境优化

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 默认参数
PROXY_HOST="127.0.0.1:7890"
PORT="8000"
ENABLED_TOOLS=""
WITH_NGINX=false

# 显示帮助
show_help() {
    cat << EOF
阿里云 ECS 部署脚本

用法: $0 [选项] [命令]

命令:
    start       启动服务 (默认)
    stop        停止服务
    restart     重启服务
    logs        查看日志
    status      查看状态

选项:
    -p, --port PORT         端口号 [默认: 8000]
    --proxy HOST           代理地址 [默认: 127.0.0.1:7890]
    --tools TOOLS          启用的工具 (逗号分隔)
    --with-nginx           启用 Nginx
    -h, --help             显示帮助

示例:
    $0 start                                    # 启动所有工具
    $0 -p 8001 --tools health_check,get_latest_news start  # 指定端口和工具
    $0 --proxy 127.0.0.1:7890 start           # 使用代理启动

EOF
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        --proxy)
            PROXY_HOST="$2"
            shift 2
            ;;
        --tools)
            ENABLED_TOOLS="$2"
            shift 2
            ;;
        --with-nginx)
            WITH_NGINX=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        start|stop|restart|logs|status)
            COMMAND="$1"
            shift
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

COMMAND=${COMMAND:-start}

# 配置 Docker 镜像加速
setup_docker_mirror() {
    log_info "配置 Docker 镜像加速..."
    
    sudo mkdir -p /etc/docker
    sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://registry.docker-cn.com",
    "https://docker.mirrors.ustc.edu.cn"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    log_success "Docker 镜像加速配置完成"
}

# 启动服务
start_service() {
    log_info "启动 News MCP Server (阿里云 ECS)..."
    
    # 设置环境变量
    export PORT=$PORT
    
    if [ -n "$PROXY_HOST" ]; then
        export HTTP_PROXY="http://$PROXY_HOST"
        export HTTPS_PROXY="http://$PROXY_HOST"
        export NO_PROXY="localhost,127.0.0.1,0.0.0.0,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
        log_info "使用代理: $PROXY_HOST"
    fi
    
    if [ -n "$ENABLED_TOOLS" ]; then
        export ENABLED_TOOLS="$ENABLED_TOOLS"
        log_info "启用的工具: $ENABLED_TOOLS"
    fi
    
    # 创建必要目录
    mkdir -p logs
    
    # 启动服务
    if [ "$WITH_NGINX" = true ]; then
        log_info "启用 Nginx 反向代理..."
        docker-compose --profile with-nginx up -d
    else
        docker-compose up -d news-mcp
    fi
    
    log_success "服务启动成功"
    log_info "服务地址: http://localhost:$PORT"
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 健康检查
    for i in {1..30}; do
        if curl -f http://localhost:$PORT/ >/dev/null 2>&1; then
            log_success "服务健康检查通过"
            return 0
        fi
        log_info "等待服务启动... ($i/30)"
        sleep 2
    done
    
    log_error "服务健康检查失败"
    return 1
}

# 停止服务
stop_service() {
    log_info "停止服务..."
    docker-compose down
    log_success "服务已停止"
}

# 重启服务
restart_service() {
    stop_service
    sleep 2
    start_service
}

# 查看日志
show_logs() {
    docker-compose logs -f --tail=100
}

# 查看状态
show_status() {
    log_info "服务状态:"
    docker-compose ps
    echo
    log_info "容器资源使用:"
    docker stats --no-stream $(docker-compose ps -q) 2>/dev/null || true
}

# 主函数
main() {
    log_info "阿里云 ECS 部署脚本"
    log_info "端口: $PORT"
    log_info "命令: $COMMAND"
    
    case $COMMAND in
        start)
            # 首次运行时配置 Docker 镜像加速
            if [ ! -f "/etc/docker/daemon.json" ]; then
                setup_docker_mirror
            fi
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        *)
            log_error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
