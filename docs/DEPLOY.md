# 部署文档

## 目录

- [环境要求](#环境要求)
- [方式一：Docker 部署（推荐）](#方式一docker-部署推荐)
- [方式二：手动部署](#方式二手动部署)
  - [Windows 完整步骤](#windows-完整步骤)
  - [Linux 完整步骤](#linux-完整步骤)
- [VPS / 云服务器部署](#vps--云服务器部署)
- [环境变量说明](#环境变量说明)
- [生产环境建议](#生产环境建议)

---

## 环境要求

| 组件 | 最低版本 | 用途 | 下载 |
|------|----------|------|------|
| Python | 3.12+ | 后端运行 | https://www.python.org/downloads/ |
| Node.js | 20+ | 前端构建运行 | https://nodejs.org/（推荐 LTS 版本） |
| MySQL | 8.0+ | 数据库 | https://dev.mysql.com/downloads/mysql/ |
| Redis | 7+ | 缓存计数器 | https://redis.io/download/ |
| Docker | 24+ | Docker 部署（可选） | https://www.docker.com/ |
| Docker Compose | 2+ | Docker 部署（可选） | 随 Docker Desktop 附带 |

---

## 方式一：Docker 部署（推荐）

无需手动安装 Python、Node.js、MySQL、Redis，仅需安装 Docker。

### 1. 安装 Docker

**Windows：** 下载 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)，安装后重启。

**Linux（以 Ubuntu 为例）：**
```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sudo bash

# 安装 Docker Compose（如果没附带）
sudo apt install docker-compose-plugin -y

# 将当前用户加入 docker 组（避免每次加 sudo）
sudo usermod -aG docker $USER
# 注销重新登录生效
```

### 2. 创建数据目录（可选，方便持久化）

```bash
mkdir -p ./docker-data/mysql
mkdir -p ./docker-data/redis
```

### 3. 配置并启动

```bash
# 进入项目根目录
cd SmartFlow

# 复制并编辑环境变量
cp .env.example .env
nano .env    # 或用 vim / notepad 编辑
```

`.env` 中需要修改的项：
```ini
# ========== Docker 部署必须修改 ==========
MYSQL_ROOT_PASSWORD=你的安全密码    # Docker 自动创建 MySQL 时的 root 密码
MYSQL_DATABASE=people_counting      # 数据库名（一般不用改）

# ========== 安全配置 ==========
SECRET_KEY=随机生成的长字符串       # JWT 密钥，生产环境务必随机化

# ========== 业务配置（按需调整）==========
MAX_PEOPLE=500                      # 最大人数上限
```
> Docker 会自动用 `MYSQL_ROOT_PASSWORD` 和 `MYSQL_DATABASE` 拼接好 DATABASE_URL，不需要手动写 `DATABASE_URL=xxx`。

### 4. 启动所有服务

```bash
docker-compose up -d
```

首次启动会自动拉取镜像并构建项目，耐心等待 2-3 分钟。

### 5. 验证

```bash
# 查看容器状态（5 个服务都应显示 Up）
docker-compose ps

# 查看后端日志
docker-compose logs backend

# 查看前端日志
docker-compose logs frontend
```

### 6. 访问

| 地址 | 说明 | 权限 |
|------|------|------|
| http://你的IP | 游客进场（默认首页） | 公开 |
| http://你的IP/exit | 游客出场 | 公开 |
| http://你的IP/login | 工作人员登录 | 公开 |
| http://你的IP/screen | 大屏展示 | 公开 |
| http://你的IP/dashboard | 数据监控面板 | 需管理员 |
| http://你的IP/admin/users | 账号管理 | 需管理员 |
| http://你的IP/admin/logs | 操作日志审计 | 需管理员 |

> Docker 方式使用 Nginx 统一代理，**只对外暴露 80 端口**。

### 7. 首次启动后的必要操作

```bash
# 1. 创建数据库表结构（后端启动时会自动检查并创建，无需手动执行）
# 如果想确认表是否创建成功：
docker compose exec mysql mysql -u root -p${MYSQL_ROOT_PASSWORD} -e "USE people_counting; SHOW TABLES;"
# 应看到 users、activity_config、people_logs 三张表

# 2. 创建默认管理员账号（如果首次启动，后端会自动创建 admin/admin123）
# 确认后端已成功初始化：
docker compose logs backend | grep -i "init"
```

**3. 登录系统并修改默认密码**

浏览器访问 `http://你的IP/login`：
- 用户名：`admin`
- 密码：`admin123`
- 登录后立即在 Dashboard 或 Admin 页面修改默认密码

**4. 调整最大人数上限**

访问 `http://你的IP/dashboard`（需管理员登录），在仪表盘页面修改 `MAX_PEOPLE` 环境变量后重启服务。

**5. 验证 WebSocket 实时推送**

访问 `http://你的IP/dashboard` 并登录，页面应显示"已连接"状态和实时人数数据。

### 8. 添加工作人员账号

管理员登录后访问 `http://你的IP/admin/users` 即可在后台页面中新增、禁用、删除工作人员账号，无需手动操作数据库。

### 10. 常用 Docker 命令

```bash
docker-compose ps                   # 查看服务状态
docker-compose logs -f backend      # 查看后端实时日志
docker-compose restart backend      # 重启后端
docker-compose down                 # 停止并删除所有容器
docker-compose down -v              # 停止并删除容器+数据卷（清空数据库）
docker-compose up -d --build        # 重新构建并启动
```

---

## 方式二：手动部署

### Windows 完整步骤

#### 第一步：安装 Python 3.12+

1. 访问 https://www.python.org/downloads/ 下载 Windows Installer（64-bit）
2. 安装时**勾选 "Add Python to PATH"**
3. 打开 PowerShell 验证：
   ```powershell
   python --version
   # 应输出：Python 3.12.x
   ```

#### 第二步：安装 Node.js 18+

1. 访问 https://nodejs.org/ 下载 LTS 版本 Windows 安装包
2. 一路默认安装即可
3. 打开新的 PowerShell 验证：
   ```powershell
   node --version
   npm --version
   ```

#### 第三步：安装 MySQL 8.0

1. 下载 [MySQL Installer for Windows](https://dev.mysql.com/downloads/installer/)
2. 运行安装程序，选择 "Developer Default" 或 "Server only"
3. 安装过程中会要求设置 **root 密码**，**请务必记住这个密码**
4. 安装完成后，MySQL 会作为 Windows 服务自动运行
5. 验证：
   ```powershell
   # 检查服务是否在运行
   Get-Service MySQL80
   # 应显示 Status: Running
   ```

#### 第四步：安装 Redis

Windows 原生不支持 Redis，使用以下方式之一：

**方式 A：使用 Docker（推荐）**
```powershell
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

**方式 B：安装 Windows 版 Redis**
1. 从 https://github.com/microsoftarchive/redis/releases 下载 Redis-x64-3.0.504.msi
2. 安装，勾选"添加到 PATH"和"安装为 Windows 服务"
3. 验证：
   ```powershell
   redis-cli ping
   # 应返回：PONG
   ```

#### 第五步：创建数据库

```powershell
# 使用 MySQL 命令行客户端
# 可以先找到 mysql.exe 路径，一般在 C:\Program Files\MySQL\MySQL Server 8.0\bin\
# 或者直接打开 MySQL 8.0 Command Line Client（开始菜单中有快捷方式）

# 在 MySQL 命令行中输入 root 密码后执行：
CREATE DATABASE IF NOT EXISTS people_counting
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

# 验证
SHOW DATABASES;
# 应该能看到 people_counting
EXIT;
```

> **说明**：这里创建了一个名为 `people_counting` 的数据库，使用 `utf8mb4` 字符集确保中文支持。

#### 第六步：配置 .env 文件

```powershell
# 在项目根目录打开 PowerShell，复制模板
copy .env.example .env

# 用记事本编辑
notepad .env
```

修改 `.env` 中的以下内容为你实际的配置：
```ini
# 把 password 换成你第四步设置的 MySQL root 密码
DATABASE_URL=mysql+aiomysql://root:你的MySQL密码@localhost:3306/people_counting

# Redis 如果在本机默认端口不用改
REDIS_URL=redis://localhost:6379/0

# 生产环境改为随机字符串
SECRET_KEY=change-me-to-a-secure-random-secret-key
```

#### 第七步：安装 Python 后端依赖

```powershell
# 确保在项目根目录（有 backend/ 子目录的地方）
cd 项目根目录

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate

# 提示符前出现 (.venv) 表示激活成功

# 安装依赖
pip install -r backend\requirements.txt
```

> `.venv` 目录只需要创建一次。以后再启动只需要激活即可。

#### 第八步：安装前端依赖

```powershell
# 确保在项目根目录
cd frontend
npm install
cd ..
```

> `node_modules` 目录只需要安装一次。

#### 第九步：启动服务

需要**同时打开两个终端窗口**：

**终端 1 — 启动后端：**
```powershell
cd 项目根目录
.venv\Scripts\activate
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

看到 `Application startup complete.` 表示启动成功。

**终端 2 — 启动前端：**
```powershell
cd 项目根目录\frontend
npm run dev
```

> ⚠️ `npm run dev` 必须在 `frontend/` 目录下执行，不能在项目根目录执行。

看到 `Local: http://localhost:5173/` 表示启动成功。

#### 第十步：访问

打开浏览器访问：
- 游客进场：http://localhost:5173/entry
- 游客出场：http://localhost:5173/exit
- 登录页面：http://localhost:5173/login（admin / admin123）
- 工作人员进场：http://localhost:5173/staff/entry
- 数据监控面板：http://localhost:5173/dashboard
- 账号管理：http://localhost:5173/admin/users
- 大屏展示：http://localhost:5173/screen
- API 文档：http://localhost:8000/docs

---

### Linux 完整步骤

以 Ubuntu/Debian 为例，CentOS 使用 yum 替代 apt。

#### 第一步：安装 Python 3.12

```bash
# Ubuntu 22.04+
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip -y

# 验证
python3.12 --version
```

#### 第二步：安装 Node.js 18+

```bash
# 使用 NodeSource 官方源（Node.js 20）
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

# 验证
node --version
npm --version
```

#### 第三步：安装 MySQL 8.0

```bash
# 安装 MySQL Server
sudo apt update
sudo apt install mysql-server -y

# 启动 MySQL 服务
sudo systemctl start mysql
sudo systemctl enable mysql   # 开机自启

# 安全初始化（设置 root 密码等）
sudo mysql_secure_installation
# 按提示操作：
#   - 是否设置密码强度插件？按 Enter（跳过）
#   - 设置 root 密码：输入两次你想设的密码
#   - 是否移除匿名用户？输入 Y
#   - 是否禁止 root 远程登录？输入 Y（更安全）
#   - 是否删除 test 数据库？输入 Y
#   - 是否刷新权限？输入 Y

# 验证
sudo systemctl status mysql
# 应显示 active (running)
```

#### 第四步：安装 Redis

```bash
# 安装
sudo apt install redis-server -y

# 启动
sudo systemctl start redis
sudo systemctl enable redis

# 验证
redis-cli ping
# 返回 PONG
```

#### 第五步：创建数据库

```bash
# 使用 root 登录 MySQL（输入第三步设的密码）
sudo mysql -u root -p

# 在 MySQL 命令行中执行：
CREATE DATABASE IF NOT EXISTS people_counting
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

# 验证
SHOW DATABASES;
EXIT;
```

> **说明**：这里创建了名为 `people_counting` 的数据库，使用 `utf8mb4` 字符集（与 MySQL 的 `utf8mb4_unicode_ci` 排序规则配合，确保完美支持中文和 emoji）。

#### 第六步：配置 .env 文件

```bash
# 在项目根目录
cd /你的路径/SmartFlow
cp .env.example .env
nano .env    # 或用 vim 编辑
```

修改 `.env`：
```ini
# 密码填你第三步设置的 MySQL root 密码
DATABASE_URL=mysql+aiomysql://root:你的密码@localhost:3306/people_counting

# Redis 在本机默认端口不用改
REDIS_URL=redis://localhost:6379/0

# 改成随机长字符串
SECRET_KEY=change-me-to-a-secure-random-secret-key
```

#### 第七步：安装 Python 后端依赖

```bash
cd 项目根目录

# 创建虚拟环境
python3.12 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r backend/requirements.txt
```

#### 第八步：安装前端依赖

```bash
cd frontend
npm install
cd ..
```

#### 第九步：启动服务

打开**两个终端窗口**，都先 cd 到项目根目录：

**终端 1 — 启动后端：**
```bash
cd 项目根目录
source .venv/bin/activate
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**终端 2 — 启动前端：**
```bash
cd 项目根目录/frontend
npm run dev
```

> ⚠️ `npm run dev` 必须在 `frontend/` 目录下执行，不能在项目根目录执行。

#### 第十步：访问

- http://localhost:5173/entry — 游客进场
- http://localhost:5173/exit — 游客出场
- http://localhost:5173/login — 登录（admin / admin123）
- http://localhost:5173/staff/entry — 工作人员进场
- http://localhost:5173/dashboard — 数据监控面板
- http://localhost:5173/screen — 大屏展示
- http://localhost:5173/admin/users — 账号管理
- http://localhost:8000/docs — API 文档

---

## VPS / 云服务器部署

要在阿里云、腾讯云、AWS 等 VPS 上部署并通过公网访问，需额外注意以下步骤。

### 1. 放行云防火墙端口

在云服务商控制台的**安全组/防火墙**页面添加入站规则：

| 端口 | 协议 | 用途 | 来源 |
|------|------|------|------|
| 80 | TCP | Docker Nginx 前端 | 0.0.0.0/0 |
| 8000 | TCP | 后端 API | 0.0.0.0/0（仅手动部署需放行） |
| 5173 | TCP | 前端开发服务器 | 0.0.0.0/0（仅手动部署需放行） |

> Docker 方式只需要放行 80 端口。

### 2. 放行系统防火墙

```bash
# Ubuntu/Debian（ufw）
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 5173/tcp
sudo ufw enable

# CentOS（firewalld）
sudo firewall-cmd --add-port=80/tcp --permanent
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --reload
```

### 3. 绑定监听地址

项目已默认设置 `--host 0.0.0.0`，无需修改。此配置表示监听所有网络接口，可以接受来自公网的请求。

### 4. 访问

```
http://你的VPS公网IP:5173/entry    → 游客进场（手动部署）
http://你的VPS公网IP/screen        → 大屏展示（Docker 部署）
http://你的VPS公网IP:8000/docs     → API 文档
```

### 5. 使用 PM2 保持后台运行（Linux）

前端和后端直接启动会在关闭终端后停止，使用 PM2 可以让它们持续在后台运行：

```bash
# 安装 PM2
npm install -g pm2

# 启动后端
cd 项目根目录/backend
source ../.venv/bin/activate
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name "people-backend"

# 启动前端（生产构建 + 静态服务器）
cd 项目根目录/frontend
npm run build
pm2 start "npx serve dist -l 5173" --name "people-frontend"

# 设置开机自启
pm2 save
pm2 startup

# 常用管理命令
pm2 status           # 查看运行状态
pm2 logs             # 查看日志
pm2 restart all      # 重启所有
pm2 stop all         # 停止所有
```

---

## 环境变量说明

| 变量名 | 默认值 | 部署方式 | 说明 |
|--------|--------|----------|------|
| MYSQL_ROOT_PASSWORD | password | Docker 专用 | Docker 创建的 MySQL root 密码 |
| MYSQL_DATABASE | people_counting | Docker 专用 | Docker 自动创建的数据库名 |
| DATABASE_URL | mysql+aiomysql://root:password@localhost:3306/people_counting | 手动部署 | MySQL 连接字符串，格式：`mysql+aiomysql://用户名:密码@主机:端口/数据库名`。Docker 部署时由 docker-compose 自动用 MYSQL_ROOT_PASSWORD + MYSQL_DATABASE 拼接，无需手动填写 |
| REDIS_URL | redis://localhost:6379/0 | 通用 | Redis 连接字符串，有密码格式：`redis://:密码@主机:端口/0` |
| SECRET_KEY | change-me-in-production | 通用 | JWT 签名密钥，**生产环境务必改为随机字符串** |
| ALGORITHM | HS256 | 通用 | JWT 算法 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 480 | 通用 | JWT Token 有效期（分钟），默认 8 小时 |
| MAX_PEOPLE | 500 | 通用 | 区域最大人数上限（可在后台管理页面动态调整） |
| RATE_LIMIT_SECONDS | 10 | 通用 | 游客提交频率限制间隔（秒） |
| MAX_VISITOR_COUNT | 10 | 通用 | 游客单次登记最大人数 |
| MAX_STAFF_COUNT | 50 | 通用 | 工作人员单次登记最大人数 |
| DEFAULT_ADMIN_USERNAME | admin | 通用 | 默认管理员用户名（首次启动自动创建，已存在则忽略） |
| DEFAULT_ADMIN_PASSWORD | admin123 | 通用 | 默认管理员密码（首次启动自动创建，**生产环境务必修改**） |

---

## 生产环境建议

1. **修改默认密码**：登录后立即在后台修改 admin 的密码
2. **修改 SECRET_KEY**：`.env` 中改为随机长字符串（可用 `openssl rand -hex 32` 生成）
3. **首选 Docker 部署**：服务隔离、Nginx 统一代理、自带健康检查和重启
4. **关闭 API 文档**：在 `backend/main.py` 中设置 `docs_url=None` 禁止外部访问 /docs
5. **配置 HTTPS**：用 Nginx 反向代理 + Let's Encrypt 免费证书
6. **定期备份数据库**：`mysqldump -u root -p people_counting > backup.sql`
7. **使用域名**：将域名 A 记录指向 VPS IP，Nginx 中配置 server_name

---

## 大型活动部署建议

> 10 万人级别活动现场的额外注意事项。

### 服务器最低配置

| 配置项 | 最低要求 | 建议值 |
|--------|----------|--------|
| CPU | 4 核 | 8 核 |
| 内存 | 8 GB | 16 GB |
| 带宽 | 10 Mbps | 50 Mbps |

### 启动前检查

```bash
# 1. 确认 MySQL 最大连接数 >= 150
docker compose exec mysql mysql -u root -p -e "SHOW VARIABLES LIKE 'max_connections';"

# 2. 确认索引已创建
docker compose exec mysql mysql -u root -p -e "SHOW INDEX FROM people_counting.people_logs;"
# 应看到 created_at 索引

# 3. 确认 WebSocket 连接正常
# 浏览器访问 /dashboard 并登录，查看顶部"实时连接"状态标签

# 4. 检查所有容器健康状态
docker compose ps
# 所有服务应显示 healthy 或 running
```

### 活动前压力测试

```bash
# 安装 wrk
sudo apt install -y wrk

# 模拟并发进场请求
cat > /tmp/test_entry.lua << 'EOF'
wrk.method = "POST"
wrk.body   = '{"count": 3}'
wrk.headers["Content-Type"] = "application/json"
EOF

wrk -t4 -c50 -d30s -s /tmp/test_entry.lua http://localhost/api/v1/visitor/entry
```

### 系统已内置的高并发优化

| 优化项 | 说明 |
|--------|------|
| 数据库连接池 | pool_size=30 + max_overflow=50，最大 80 连接 |
| 日志索引 | people_logs 表 created_at 索引，聚合查询毫秒级 |
| Nginx 优化 | 4096 并发连接、keepalive 复用、gzip 压缩 |
| WebSocket | 并行广播，多屏同时推送不阻塞 |
| 原子计数 | Redis INCRBY/DECRBY 保证数据一致性 |
