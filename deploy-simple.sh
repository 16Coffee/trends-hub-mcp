#!/bin/bash

# 简化版阿里云部署脚本 - 不使用构建时代理

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 默认参数
PORT="8001"
ENABLED_TOOLS="get_latest_news"
PROXY_HOST="host.docker.internal:7890"  # Docker内部访问宿主机代理

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        --tools)
            ENABLED_TOOLS="$2"
            shift 2
            ;;
        --proxy)
            PROXY_HOST="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

log_info "简化版阿里云 ECS 部署"
log_info "端口: $PORT"
log_info "工具: $ENABLED_TOOLS"

# 设置环境变量
export PORT=$PORT
export ENABLED_TOOLS="$ENABLED_TOOLS"
export HTTP_PROXY="http://$PROXY_HOST"
export HTTPS_PROXY="http://$PROXY_HOST"
export NO_PROXY="localhost,127.0.0.1,0.0.0.0,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"

log_info "Docker容器代理配置:"
log_info "  HTTP_PROXY=$HTTP_PROXY"
log_info "  HTTPS_PROXY=$HTTPS_PROXY"

log_info "使用代理: $PROXY_HOST"
log_info "启用的工具: $ENABLED_TOOLS"

# 创建目录
mkdir -p logs

# 清理旧版本并重新构建 (确保使用最新代码)
log_info "清理旧版本..."
docker-compose down news-mcp 2>/dev/null || true
docker rmi trends-hub-mcp:latest 2>/dev/null || true

log_info "清理Python缓存..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

log_info "重新构建并启动服务 (不使用缓存)..."
docker-compose build --no-cache news-mcp
docker-compose up -d news-mcp

log_success "服务启动成功"
log_info "服务地址: http://localhost:$PORT"

# 等待并检查服务
log_info "等待服务启动..."
sleep 15

for i in {1..20}; do
    if curl -f http://localhost:$PORT/ >/dev/null 2>&1; then
        log_success "服务健康检查通过"
        log_info "可以开始测试了！"
        exit 0
    fi
    log_info "等待服务启动... ($i/20)"
    sleep 3
done

log_info "服务可能还在启动中，请稍后手动检查"
log_info "检查命令: curl http://localhost:$PORT/"
