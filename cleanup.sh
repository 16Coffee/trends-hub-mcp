#!/bin/bash

# 项目清理脚本
# 用于清理开发过程中产生的临时文件和缓存

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
项目清理脚本

用法: $0 [选项]

选项:
    --all           清理所有文件 (包括虚拟环境)
    --cache         仅清理缓存文件
    --logs          仅清理日志文件
    --docker        清理 Docker 相关文件
    --venv          清理虚拟环境
    -h, --help      显示帮助信息

示例:
    $0              # 清理缓存和日志
    $0 --all        # 清理所有文件
    $0 --cache      # 仅清理缓存

EOF
}

# 清理 Python 缓存
clean_cache() {
    log_info "清理 Python 缓存文件..."
    
    # 清理 __pycache__ 目录
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # 清理 .pyc 文件
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # 清理 .pyo 文件
    find . -name "*.pyo" -delete 2>/dev/null || true
    
    log_success "Python 缓存清理完成"
}

# 清理日志文件
clean_logs() {
    log_info "清理日志文件..."
    
    # 清理根目录的日志文件
    rm -f *.log 2>/dev/null || true
    
    # 清理 logs 目录中的日志文件 (保留目录)
    if [ -d "logs" ]; then
        rm -f logs/*.log 2>/dev/null || true
    fi
    
    log_success "日志文件清理完成"
}

# 清理 Docker 相关文件
clean_docker() {
    log_info "清理 Docker 相关文件..."
    
    # 停止并删除容器
    docker-compose down 2>/dev/null || true
    
    # 清理未使用的镜像
    docker image prune -f 2>/dev/null || true
    
    # 清理未使用的卷
    docker volume prune -f 2>/dev/null || true
    
    log_success "Docker 清理完成"
}

# 清理虚拟环境
clean_venv() {
    log_warning "准备删除虚拟环境..."
    
    if [ -d "venv" ]; then
        read -p "确定要删除虚拟环境吗? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            log_success "虚拟环境已删除"
        else
            log_info "跳过虚拟环境删除"
        fi
    else
        log_info "虚拟环境不存在"
    fi
}

# 清理临时文件
clean_temp() {
    log_info "清理临时文件..."
    
    # 清理临时目录
    rm -rf tmp/ temp/ .tmp/ 2>/dev/null || true
    
    # 清理备份文件
    find . -name "*.bak" -delete 2>/dev/null || true
    find . -name "*.backup" -delete 2>/dev/null || true
    
    # 清理编辑器临时文件
    find . -name "*~" -delete 2>/dev/null || true
    find . -name "*.swp" -delete 2>/dev/null || true
    find . -name "*.swo" -delete 2>/dev/null || true
    
    log_success "临时文件清理完成"
}

# 清理系统文件
clean_system() {
    log_info "清理系统文件..."
    
    # 清理 macOS 文件
    find . -name ".DS_Store" -delete 2>/dev/null || true
    
    # 清理 Windows 文件
    find . -name "Thumbs.db" -delete 2>/dev/null || true
    find . -name "ehthumbs.db" -delete 2>/dev/null || true
    
    log_success "系统文件清理完成"
}

# 默认清理
default_clean() {
    log_info "执行默认清理..."
    clean_cache
    clean_logs
    clean_temp
    clean_system
}

# 全面清理
full_clean() {
    log_info "执行全面清理..."
    clean_cache
    clean_logs
    clean_temp
    clean_system
    clean_docker
    clean_venv
}

# 主函数
main() {
    case "${1:-default}" in
        --all)
            full_clean
            ;;
        --cache)
            clean_cache
            ;;
        --logs)
            clean_logs
            ;;
        --docker)
            clean_docker
            ;;
        --venv)
            clean_venv
            ;;
        --temp)
            clean_temp
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        default)
            default_clean
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
    
    log_success "清理完成！"
}

# 运行主函数
main "$@"
