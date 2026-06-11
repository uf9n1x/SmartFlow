# SmartFlow 智流云

> 大型活动实时客流统计与管控平台

[![GitHub](https://img.shields.io/badge/GitHub-smartflow-blue?logo=github)](https://github.com/your-org/smartflow)

基于 FastAPI + Vue3 + Redis + MySQL 的大型活动实时客流统计与管控平台，适用于展会、景区、庙会、市集等场景。

## 核心功能

- **游客扫码登记**：游客通过二维码扫码自主登记进场/出场，每人每次1\~10人
- **工作人员快速登记**：工作人员登录后使用快捷按钮（+1/+2/+3/+5/+10）快速登记
- **实时 Dashboard**：WebSocket 实时推送当前人数、进出场数据等
- **大屏展示**：全屏数据大屏，饼图、趋势图、操作记录实时滚动
- **后台管理**：活动配置、日志审计、报表导出（Excel/CSV）
- **防作弊机制**：IP 限频（10秒）、数量限制、原子计数

## 技术栈

| 层级     | 技术                              |
| ------ | ------------------------------- |
| 后端框架   | Python 3.12 + FastAPI           |
| ORM    | SQLAlchemy 2.0（异步）              |
| 缓存     | Redis 7（原子计数器）                  |
| 数据库    | MySQL 8.0                       |
| 认证     | JWT                             |
| 前端框架   | Vue 3 + TypeScript              |
| UI 组件库 | Element Plus                    |
| 构建工具   | Vite                            |
| 图表     | ECharts                         |
| 状态管理   | Pinia                           |
| 实时通信   | WebSocket                       |
| 部署     | Docker + Docker Compose + Nginx |

## 快速开始

### 方式一：Docker 部署（推荐）

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 修改数据库密码等配置

# 2. 一键启动
docker-compose up -d

# 3. 访问
# 前端：http://localhost
# 后端 API 文档：http://localhost:8000/docs
```

### 方式二：手动部署

#### 环境要求

部署前请确保已安装以下软件服务：

| 软件      | 最低版本  | 用途       | 下载/安装地址                             |
| ------- | ----- | -------- | ----------------------------------- |
| Python  | 3.12+ | 后端运行环境   | <https://www.python.org/downloads/> |
| Node.js | 18+   | 前端构建与运行  | <https://nodejs.org/（推荐> LTS 版本）    |
| MySQL   | 8.0+  | 数据持久化存储  | <https://dev.mysql.com/downloads/>  |
| Redis   | 7+    | 缓存与实时计数器 | <https://redis.io/download/>        |

> **Windows 用户注意**：MySQL 和 Redis 在 Windows 上可通过以下方式安装：
>
> - MySQL：下载 MySQL Installer for Windows
> - Redis：从 [MicrosoftArchive/redis](https://github.com/microsoftarchive/redis/releases) 下载 Windows 版，或使用 Docker 单独运行 Redis
>
> 安装 MySQL 时请记住 root 密码（后续配置需要用到）。

#### 第一步：获取代码

```bash
# 将项目代码解压或克隆到本地目录，例如：
cd 项目根目录
```

#### 第二步：创建 MySQL 数据库

连接到 MySQL 并创建数据库（字符集必须为 UTF-8）：

```sql
-- 使用 root 账号登录 MySQL 后执行：
CREATE DATABASE IF NOT EXISTS people_counting
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

命令行方式：

**Windows:**

```powershell
mysql -u root -p
# 输入 root 密码后，执行上面的 CREATE DATABASE 语句
```

**Linux:**

```bash
sudo mysql -u root -p
# 输入密码后执行 CREATE DATABASE 语句
```

#### 第三步：配置环境变量

将 `.env.example` 复制为 `.env`，并根据实际环境修改配置：

```bash
# Windows (PowerShell)
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

编辑 `.env` 文件，修改以下关键配置：

```ini
# ========== 数据库配置 ==========
DATABASE_URL=mysql+aiomysql://root:你的密码@localhost:3306/people_counting

# ========== Redis 配置 ==========
REDIS_URL=redis://localhost:6379/0
# 如果 Redis 有密码：
# REDIS_URL=redis://:你的Redis密码@localhost:6379/0

# ========== JWT 配置 ==========
# 生产环境必须改为随机安全字符串！
SECRET_KEY=change-me-to-a-secure-random-secret-key

# ========== 业务配置 ==========
MAX_PEOPLE=500                  # 默认最大人数上限
RATE_LIMIT_SECONDS=10           # IP 频率限制间隔（秒）
MAX_VISITOR_COUNT=10            # 游客单次最大人数
MAX_STAFF_COUNT=50              # 工作人员单次最大人数
```

#### 第四步：安装 Python 后端

**Windows (PowerShell)：**

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
```

**Linux/macOS：**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

#### 第五步：安装前端依赖

```bash
cd frontend
npm install
cd ..
```

#### 第六步：启动 Redis 和 MySQL 服务

**Windows：**

```powershell
# 检查 Redis 是否在运行
netstat -ano | findstr :6379
# 如果未运行：
redis-server.exe

# 检查 MySQL 是否在运行
netstat -ano | findstr :3306
# 如果未运行：
net start MySQL80
```

**Linux：**

```bash
sudo systemctl start redis
sudo systemctl start mysql
```

#### 第七步：启动后端 API 服务

**Windows：**

```powershell
.venv\Scripts\activate
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Linux：**

```bash
source .venv/bin/activate
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 第八步：启动前端开发服务器

**打开另一个终端窗口**，执行：

```powershell
# Windows
cd frontend
npm run dev
```

```bash
# Linux/macOS
cd frontend
npm run dev
```

#### 第九步：访问系统

| 地址                                   | 页面     | 说明                   |
| ------------------------------------ | ------ | -------------------- |
| <http://localhost:5173/entry>        | 游客进场登记 | 手机扫码访问               |
| <http://localhost:5173/exit>         | 游客出场登记 | 手机扫码访问               |
| <http://localhost:5173/login>        | 工作人员登录 | 账号: admin / admin123 |
| <http://localhost:5173/staff/entry>  | 入口工作人员 | 需登录                  |
| <http://localhost:5173/staff/exit>   | 出口工作人员 | 需登录                  |
| <http://localhost:5173/dashboard>    | 数据监控面板 | 需登录                  |
| <http://localhost:5173/screen>       | 大屏展示   | 1920x1080 全屏         |
| <http://localhost:5173/admin/config> | 活动配置管理 | 需管理员                 |

### 方式三：使用启动脚本（简化）

```bash
# Windows — 双击运行
start.bat

# Linux/macOS
chmod +x start.sh
./start.sh
```

***

## VPS 生产环境部署

以下步骤以 **Ubuntu 22.04/24.04 VPS** 为例，使用 Docker Compose 一键部署。

### 1. VPS 基础环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 安装 Docker Compose
sudo apt install -y docker-compose-plugin

# 将当前用户加入 docker 组（免 sudo）
sudo usermod -aG docker $USER
newgrp docker

# 验证安装
docker --version
docker compose version
```

### 2. 上传项目到 VPS

**方式A：使用 Git（推荐）**

```bash
# 在 VPS 上克隆项目
git clone <你的仓库地址> /opt/people-counting
cd /opt/people-counting
```

**方式B：使用 SCP 上传**

```bash
# 在本地执行，将项目打包上传
# Windows (PowerShell)
Compress-Archive -Path .\* -DestinationPath people-counting.zip
scp people-counting.zip root@你的VPS_IP:/opt/

# Linux/macOS
tar czf people-counting.tar.gz .
scp people-counting.tar.gz root@你的VPS_IP:/opt/

# 在 VPS 上解压
cd /opt
unzip people-counting.zip -d people-counting   # 或 tar xzf people-counting.tar.gz -C people-counting
cd people-counting
```

### 3. 配置环境变量

```bash
cp .env.example .env
nano .env
```

**生产环境必须修改以下配置：**

```ini
# ========== 数据库（Docker 部署 — 必须修改）==========
MYSQL_ROOT_PASSWORD=你的强密码     # Docker 自动创建 MySQL 时的 root 密码
MYSQL_DATABASE=people_counting    # 数据库名，一般不用改

# Docker 会自动用上面两个变量拼接下面的 DATABASE_URL，无需手动修改
# DATABASE_URL=mysql+aiomysql://root:你的强密码@mysql:3306/people_counting

# ========== JWT 密钥（必须修改）==========
# 可用命令生成：python3 -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=你生成的随机密钥

# ========== 业务配置（按需修改）==========
MAX_PEOPLE=500           # 最大人数上限（可在后台管理页面动态调整）
RATE_LIMIT_SECONDS=10    # 游客提交频率限制间隔
MAX_VISITOR_COUNT=10     # 游客单次最大人数
MAX_STAFF_COUNT=50       # 工作人员单次最大人数

# ========== 默认管理员账号（首次启动自动创建，已存在则忽略）==========
DEFAULT_ADMIN_USERNAME=admin      # 管理员用户名
DEFAULT_ADMIN_PASSWORD=admin123   # 管理员密码，生产环境务必修改！
```

### 4. 修改 Nginx 配置绑定域名

编辑 `frontend/nginx.conf`，将 `server_name localhost` 改为你的域名：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 改为你的域名或 VPS IP

    # ... 其余配置不变
}
```

### 5. 一键启动

```bash
cd /opt/people-counting
docker compose up -d --build
```

等待构建完成（首次约 3-5 分钟），检查服务状态：

```bash
# 查看所有容器状态
docker compose ps

# 查看后端日志
docker compose logs -f backend

# 查看前端日志
docker compose logs -f frontend
```

所有容器状态应为 `healthy` 或 `running`。

### 6. 配置 HTTPS（强烈推荐）

游客通过手机扫码访问，浏览器会对 HTTP 页面显示"不安全"警告，建议配置 HTTPS。

**方式A：使用 Certbot + Let's Encrypt（免费，有域名）**

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 先确保 Nginx 容器正在运行
docker compose up -d

# 申请证书（替换为你的域名和邮箱）
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 证书会自动续期，验证续期定时任务
sudo certbot renew --dry-run
```

**方式B：使用 Cloudflare（免费，有域名）**

1. 将域名 DNS 托管到 Cloudflare
2. 在 Cloudflare Dashboard 中开启 SSL/TLS → Full 模式
3. Cloudflare 自动提供 HTTPS，无需在 VPS 上额外配置

**方式C：使用自签名证书（无域名，仅测试用）**

```bash
# 生成自签名证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /opt/people-counting/ssl/key.pem \
  -out /opt/people-counting/ssl/cert.pem

# 修改 frontend/nginx.conf 添加 SSL 配置
# 然后修改 docker-compose.yml 挂载证书文件并开放 443 端口
```

### 7. 防火墙配置

```bash
# 开放必要端口
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 22/tcp      # SSH

# 如果需要外部直接访问后端 API（可选）
sudo ufw allow 8000/tcp

# 启用防火墙
sudo ufw enable
```

***

## 生成游客扫码二维码

系统部署完成后，需要在活动入口和出口分别放置二维码，供游客扫码登记。

### 二维码对应地址

| 二维码   | URL                  | 放置位置  |
| ----- | -------------------- | ----- |
| 进场二维码 | `https://你的域名/entry` | 活动入口处 |
| 出场二维码 | `https://你的域名/exit`  | 活动出口处 |

### 方式一：在线工具生成（最简单）

访问以下任一在线二维码生成网站，输入对应 URL 即可：

- <https://cli.im/> （草料二维码，国内访问快）
- <https://www.qrcode-monkey.com/>
- <https://qr.io/>

**建议设置：**

- 容错级别：M 或 H（防止打印模糊导致扫不出）
- 尺寸：至少 300x300 像素
- 可在二维码下方添加文字说明："扫码进场" / "扫码出场"

### 方式二：Python 脚本批量生成

在 VPS 或本地运行以下脚本，自动生成高清二维码图片：

```bash
# 安装依赖
pip install qrcode[pil]

# 生成进场二维码
python3 -c "
import qrcode
qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=15, border=4)
qr.add_data('https://你的域名/entry')
qr.make(fit=True)
img = qr.make_image(fill_color='black', back_color='white')
img.save('进场二维码.png')
print('进场二维码已保存为 进场二维码.png')
"

# 生成出场二维码
python3 -c "
import qrcode
qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=15, border=4)
qr.add_data('https://你的域名/exit')
qr.make(fit=True)
img = qr.make_image(fill_color='black', back_color='white')
img.save('出场二维码.png')
print('出场二维码已保存为 出场二维码.png')
"
```

### 方式三：前端页面内嵌二维码（可选）

如需在 Dashboard 或管理页面内展示二维码，可使用 `qrcode.vue` 组件：

```bash
cd frontend
npm install qrcode.vue
```

在页面中使用：

```vue
<template>
  <QrcodeVue :value="entryUrl" :size="200" level="H" />
</template>

<script setup>
import QrcodeVue from 'qrcode.vue'
const entryUrl = `${window.location.origin}/entry`
</script>
```

### 二维码打印建议

1. **尺寸**：建议打印为 A4 纸 1/4 大小（约 10cm x 10cm），确保手机能轻松扫描
2. **材质**：使用亚克力板或过塑纸张，防止磨损
3. **标识**：在二维码上方标注"进场登记"或"出场登记"，避免游客扫错
4. **放置**：入口/出口显眼位置，高度约 1.2-1.5 米（方便手机扫描）
5. **备用**：准备 2-3 份备用二维码，防止损坏

***

## 默认账号

| 角色  | 用户名   | 密码       |
| --- | ----- | -------- |
| 管理员 | admin | admin123 |

> **安全提示**：生产环境部署后，请立即登录系统修改默认密码！

***

## 常用运维命令

```bash
# 查看服务状态
docker compose ps

# 查看实时日志
docker compose logs -f

# 重启某个服务
docker compose restart backend
docker compose restart frontend

# 重新构建并启动（代码更新后）
docker compose up -d --build

# 停止所有服务
docker compose down

# 停止并清除数据卷（重置数据库，慎用！）
docker compose down -v

# 进入后端容器调试
docker compose exec backend bash

# 进入 MySQL 容器
docker compose exec mysql mysql -u root -p
```

***

## 页面路由

| 路由            | 页面     | 权限  | 用途           |
| ------------- | ------ | --- | ------------ |
| /entry        | 游客进场登记 | 公开  | 入口二维码指向此页    |
| /exit         | 游客出场登记 | 公开  | 出口二维码指向此页    |
| /login        | 工作人员登录 | 公开  | 工作人员登录入口     |
| /staff/entry  | 入口工作人员 | JWT | 工作人员快速登记进场   |
| /staff/exit   | 出口工作人员 | JWT | 工作人员快速登记出场   |
| /dashboard    | 数据监控面板 | JWT | 实时数据监控       |
| /screen       | 大屏展示   | 公开  | 投屏到大屏幕       |
| /admin/config | 活动配置管理 | 管理员 | 修改人数上限等      |
| /admin/logs   | 操作日志审计 | 管理员 | 查看操作记录       |
| /admin/report | 数据报表导出 | 管理员 | 导出 Excel/CSV |

***

## 项目结构

```
├── backend/                # FastAPI 后端
│   ├── main.py             # 应用入口
│   ├── api/v1/             # API 路由
│   ├── core/               # 核心配置（数据库、Redis、JWT）
│   ├── models/             # 数据模型
│   ├── schemas/            # Pydantic Schema
│   ├── services/           # 业务逻辑层
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
├── frontend/               # Vue3 前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   │   ├── visitor/    # 游客页面（进场/出场）
│   │   │   ├── auth/       # 登录页面
│   │   │   ├── staff/      # 工作人员页面
│   │   │   ├── dashboard/  # 仪表盘
│   │   │   ├── screen/     # 大屏展示
│   │   │   └── admin/      # 后台管理
│   │   ├── stores/         # Pinia Store
│   │   ├── router/         # 路由配置
│   │   └── styles/         # 样式（公安蓝主题）
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml      # Docker 编排
├── .env.example            # 环境变量模板
├── start.bat               # Windows 启动脚本
├── start.sh                # Linux 启动脚本
└── docs/                   # 文档
```

## 文档

- [API 文档](docs/API.md)
- [部署文档](docs/DEPLOY.md)
- [数据库设计文档](docs/DB_DESIGN.md)

