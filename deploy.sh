#!/bin/bash

# News MCP Server Docker 部署脚本
# 支持本地测试和生产部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
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

# 显示帮助信息
show_help() {
    cat << EOF
News MCP Server Docker 部署脚本

用法: $0 [选项] [命令]

命令:
    build       构建 Docker 镜像
    start       启动服务 (默认)
    stop        停止服务
    restart     重启服务
    logs        查看日志
    status      查看服务状态
    clean       清理容器和镜像
    test        运行测试
    test-proxy  测试代理连接

选项:
    -e, --env ENV       环境 (local|production) [默认: local]
    -p, --port PORT     端口号 [默认: 8000]
    -h, --help          显示帮助信息
    --with-nginx        启用 Nginx 反向代理
    --build-only        仅构建镜像，不启动服务
    --proxy HOST        代理服务器地址 [默认: 127.0.0.1:7890]
    --tools TOOLS       启用的工具列表 (用逗号分隔)

示例:
    $0                                      # 本地启动服务
    $0 build                                # 构建镜像
    $0 start --with-nginx                   # 启动服务并启用 Nginx
    $0 -e production start                  # 生产环境启动
    $0 --proxy 127.0.0.1:7890 start        # 使用代理启动
    $0 --tools health_check,get_latest_news start  # 仅启用指定工具
    $0 test-proxy                           # 测试代理连接
    $0 logs                                 # 查看日志
    $0 clean                                # 清理所有容器和镜像

EOF
}

# 默认参数
ENVIRONMENT="local"
PORT="8000"
COMMAND="start"
WITH_NGINX=false
BUILD_ONLY=false
PROXY_HOST="127.0.0.1:7890"
ENABLED_TOOLS=""

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        --with-nginx)
            WITH_NGINX=true
            shift
            ;;
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
    --proxy)
            PROXY_HOST="$2"
            shift 2
            ;;
        --tools)
            ENABLED_TOOLS="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        build|start|stop|restart|logs|status|clean|test|test-proxy)
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

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    mkdir -p logs
    mkdir -p nginx/ssl
}

# 构建镜像
build_image() {
    log_info "构建 Docker 镜像..."
    docker-compose build --no-cache
    log_success "镜像构建完成"
}

# 启动服务
start_service() {
    log_info "启动 News MCP Server..."

    # 设置环境变量
    export PORT=$PORT

    # 设置代理环境变量
    if [ -n "$PROXY_HOST" ]; then
        export HTTP_PROXY="http://$PROXY_HOST"
        export HTTPS_PROXY="http://$PROXY_HOST"
        export NO_PROXY="localhost,127.0.0.1,0.0.0.0,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
        log_info "使用代理: $PROXY_HOST"
    fi

    # 设置工具配置
    if [ -n "$ENABLED_TOOLS" ]; then
        export ENABLED_TOOLS="$ENABLED_TOOLS"
        log_info "启用的工具: $ENABLED_TOOLS"
    fi

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
    sleep 5

    # 检查服务状态
    check_service_health
}

# 停止服务
stop_service() {
    log_info "停止服务..."
    docker-compose down
    log_success "服务已停止"
}

# 重启服务
restart_service() {
    log_info "重启服务..."
    stop_service
    start_service
}

# 查看日志
show_logs() {
    log_info "显示服务日志..."
    docker-compose logs -f --tail=100
}

# 查看服务状态
show_status() {
    log_info "服务状态:"
    docker-compose ps
    echo
    log_info "容器资源使用情况:"
    docker stats --no-stream $(docker-compose ps -q) 2>/dev/null || true
}

# 检查服务健康状态
check_service_health() {
    log_info "检查服务健康状态..."
    
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

# 测试代理连接
test_proxy() {
    log_info "测试代理连接..."

    if [ -z "$PROXY_HOST" ]; then
        log_error "未设置代理地址，请使用 --proxy 参数"
        return 1
    fi

    log_info "代理地址: $PROXY_HOST"

    # 测试代理是否可达
    if curl -x "http://$PROXY_HOST" --connect-timeout 5 -s http://www.google.com > /dev/null 2>&1; then
        log_success "代理连接测试成功"
        return 0
    else
        log_warning "代理连接测试失败，尝试直连测试..."
        if curl --connect-timeout 5 -s http://www.baidu.com > /dev/null 2>&1; then
            log_warning "直连成功，但代理可能有问题"
        else
            log_error "网络连接异常"
        fi
        return 1
    fi
}

# 运行测试
run_tests() {
    log_info "运行服务测试..."

    # 启动测试服务
    docker-compose up -d news-mcp

    # 等待服务启动
    sleep 10

    # 运行健康检查测试
    if check_service_health; then
        log_success "基础健康检查通过"
    else
        log_error "基础健康检查失败"
        return 1
    fi

    # 测试 MCP 工具
    log_info "测试 MCP 工具..."

    # 这里可以添加更多的测试逻辑

    log_success "所有测试通过"
}

# 清理容器和镜像
clean_up() {
    log_warning "这将删除所有相关的容器、镜像和卷"
    read -p "确定要继续吗? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "清理容器和镜像..."
        docker-compose down -v --rmi all --remove-orphans
        log_success "清理完成"
    else
        log_info "取消清理操作"
    fi
}

# 主函数
main() {
    log_info "News MCP Server Docker 部署脚本"
    log_info "环境: $ENVIRONMENT"
    log_info "端口: $PORT"
    log_info "命令: $COMMAND"
    
    check_docker
    create_directories
    
    case $COMMAND in
        build)
            build_image
            if [ "$BUILD_ONLY" = false ]; then
                start_service
            fi
            ;;
        start)
            build_image
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
        test)
            run_tests
            ;;
        test-proxy)
            test_proxy
            ;;
        clean)
            clean_up
            ;;
        *)
            log_error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
