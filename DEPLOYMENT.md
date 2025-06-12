# Docker 部署指南

## 🚀 本地测试部署

### 快速开始

1. **构建并启动服务**：
```bash
./deploy.sh
```

2. **如果需要代理访问外网**：
```bash
./deploy.sh --proxy 127.0.0.1:7890 start
```

3. **启用 Nginx 反向代理**：
```bash
./deploy.sh start --with-nginx
# 或使用代理版本
./deploy.sh --proxy 127.0.0.1:7890 start --with-nginx
```

3. **查看服务状态**：
```bash
./deploy.sh status
```

4. **查看日志**：
```bash
./deploy.sh logs
```

### 详细命令

```bash
# 仅构建镜像
./deploy.sh build --build-only

# 指定端口启动
./deploy.sh -p 3000 start

# 运行测试
./deploy.sh test

# 停止服务
./deploy.sh stop

# 清理所有容器和镜像
./deploy.sh clean
```

## 🌐 代理配置 (重要)

### 适用场景
如果你的服务器需要通过代理访问外网（如阿里云 ECS、企业内网等），请使用代理部署方式。

### 代理部署方式

#### 1. 使用专用代理脚本 (推荐)
```bash
# 测试代理连接
./deploy-with-proxy.sh test

# 使用默认代理 (127.0.0.1:7890) 启动
./deploy-with-proxy.sh start

# 指定自定义代理启动
./deploy-with-proxy.sh -p 192.168.1.100:8080 start

# 启用 Nginx 反向代理
./deploy-with-proxy.sh --with-nginx start
```

#### 2. 手动配置环境变量
```bash
# 设置代理环境变量
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
export NO_PROXY=localhost,127.0.0.1,0.0.0.0,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16

# 启动服务
./deploy.sh start
```

#### 3. 使用配置文件
```bash
# 开发环境
cp .env.example .env.dev
vim .env.dev
docker-compose --env-file .env.dev up -d

# 生产环境
cp .env.example .env.prod
vim .env.prod
docker-compose --env-file .env.prod --profile with-nginx up -d
```

### 代理配置说明

| 环境变量 | 说明 | 示例值 |
|----------|------|--------|
| `HTTP_PROXY` | HTTP 代理地址 | `http://127.0.0.1:7890` |
| `HTTPS_PROXY` | HTTPS 代理地址 | `http://127.0.0.1:7890` |
| `NO_PROXY` | 不使用代理的地址 | `localhost,127.0.0.1` |

### 常见代理软件端口

| 软件 | 默认端口 | 配置示例 |
|------|----------|----------|
| **Clash** | 7890 | `127.0.0.1:7890` |
| **V2Ray** | 1080 | `127.0.0.1:1080` |
| **Shadowsocks** | 1080 | `127.0.0.1:1080` |
| **企业代理** | 8080 | `proxy.company.com:8080` |

## ☁️ 阿里云 ECS 部署

### 1. 准备 ECS 实例

**推荐配置**：
- CPU: 2核心
- 内存: 4GB
- 存储: 40GB SSD
- 操作系统: Ubuntu 20.04 LTS 或 CentOS 8

### 2. 安装 Docker

**Ubuntu/Debian**：
```bash
# 更新包索引
sudo apt update

# 安装必要的包
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# 添加 Docker 官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 将用户添加到 docker 组
sudo usermod -aG docker $USER
```

**CentOS/RHEL**：
```bash
# 安装必要的包
sudo yum install -y yum-utils

# 添加 Docker 仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 将用户添加到 docker 组
sudo usermod -aG docker $USER
```

### 3. 安装 Docker Compose

```bash
# 下载 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 设置执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 4. 部署应用

```bash
# 克隆项目
git clone <your-repository-url>
cd trends-hub-mcp

# 设置脚本权限
chmod +x deploy.sh

# 如果服务器需要代理访问外网 (推荐)
./deploy.sh --proxy 127.0.0.1:7890 -e production start --with-nginx

# 或者使用标准部署 (如果不需要代理)
./deploy.sh -e production start --with-nginx

# 或者手动使用配置文件
docker-compose --env-file .env.prod --profile with-nginx up -d
```

### 5. 配置防火墙

**Ubuntu (UFW)**：
```bash
# 启用防火墙
sudo ufw enable

# 允许 SSH
sudo ufw allow ssh

# 允许 HTTP 和 HTTPS
sudo ufw allow 80
sudo ufw allow 443

# 允许自定义端口 (如果需要)
sudo ufw allow 8000
```

**CentOS (firewalld)**：
```bash
# 启动防火墙
sudo systemctl start firewalld
sudo systemctl enable firewalld

# 允许 HTTP 和 HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# 允许自定义端口
sudo firewall-cmd --permanent --add-port=8000/tcp

# 重新加载配置
sudo firewall-cmd --reload
```

### 6. 配置域名和 SSL (可选)

1. **配置域名解析**：
   - 在域名服务商处添加 A 记录，指向 ECS 公网 IP

2. **获取 SSL 证书**：
```bash
# 安装 Certbot
sudo apt install -y certbot

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 复制证书到项目目录
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
sudo chown $USER:$USER nginx/ssl/*.pem
```

3. **更新 Nginx 配置**：
   - 编辑 `nginx/nginx.conf`，启用 HTTPS 配置部分
   - 将 `your-domain.com` 替换为实际域名

### 7. 设置自动启动

创建 systemd 服务文件：

```bash
sudo tee /etc/systemd/system/news-mcp.service > /dev/null <<EOF
[Unit]
Description=News MCP Server
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/trends-hub-mcp
ExecStart=/path/to/trends-hub-mcp/deploy.sh -e production start --with-nginx
ExecStop=/path/to/trends-hub-mcp/deploy.sh stop
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
sudo systemctl enable news-mcp.service
sudo systemctl start news-mcp.service
```

## 🔧 生产环境优化

### 1. 资源限制

在 `docker-compose.prod.yml` 中已配置了资源限制：
- CPU: 最大 1 核心，预留 0.5 核心
- 内存: 最大 512MB，预留 256MB

### 2. 日志管理

```bash
# 配置 Docker 日志轮转
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# 重启 Docker
sudo systemctl restart docker
```

### 3. 监控和告警

可以集成以下监控工具：
- Prometheus + Grafana
- 阿里云云监控
- Docker 健康检查

### 4. 备份策略

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/news-mcp"

mkdir -p $BACKUP_DIR

# 备份配置文件
tar -czf $BACKUP_DIR/config_$DATE.tar.gz config/

# 备份日志
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# 清理旧备份 (保留 7 天)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# 添加到 crontab
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

## 🔍 故障排除

### 常见问题

1. **端口被占用**：
```bash
# 查看端口占用
sudo netstat -tlnp | grep :8000
# 或
sudo ss -tlnp | grep :8000
```

2. **容器启动失败**：
```bash
# 查看容器日志
docker-compose logs news-mcp

# 查看容器状态
docker-compose ps
```

3. **内存不足**：
```bash
# 查看系统资源
free -h
df -h

# 查看容器资源使用
docker stats
```

4. **网络问题**：
```bash
# 测试容器网络
docker-compose exec news-mcp ping google.com

# 检查防火墙
sudo ufw status
```

### 日志查看

```bash
# 实时查看应用日志
./deploy.sh logs

# 查看 Nginx 日志
docker-compose logs nginx

# 查看系统日志
sudo journalctl -u docker.service
```

## 📞 技术支持

如果遇到部署问题，请检查：
1. Docker 和 Docker Compose 版本
2. 系统资源是否充足
3. 网络连接是否正常
4. 防火墙配置是否正确
