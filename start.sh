#!/bin/bash
# 区域人数管控统计系统 - 一键启动脚本 (Linux/macOS)

echo "============================================"
echo "  区域人数管控统计系统 - 一键启动"
echo "============================================"
echo ""

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "[警告] 未找到 .env 文件，请先配置 .env"
    echo "请复制 .env.example 为 .env 并修改配置"
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.12+"
    exit 1
fi

# 激活虚拟环境
if [ -f ".venv/bin/activate" ]; then
    echo "[信息] 激活虚拟环境..."
    source .venv/bin/activate
else
    echo "[警告] 未找到虚拟环境，正在创建..."
    uv venv .venv --python 3.12
    source .venv/bin/activate
fi

# 安装后端依赖
echo "[信息] 检查并安装后端依赖..."
uv pip install -r backend/requirements.txt --quiet

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "[错误] 未找到 Node.js，请先安装 Node.js 18+"
    exit 1
fi

# 安装前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "[信息] 安装前端依赖..."
    cd frontend && npm install && cd ..
fi

echo "[提示] 请确保 Redis 和 MySQL 服务已启动"
echo "Redis 默认地址: localhost:6379"
echo "MySQL 默认地址: localhost:3306"
echo ""

# 启动后端
echo "[信息] 启动后端 API 服务..."
cd backend && ../.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 启动前端
echo "[信息] 启动前端开发服务器..."
cd ../frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "============================================"
echo "  系统启动完成！"
echo "============================================"
echo ""
echo "  后端服务:"
echo "    API 接口:   http://localhost:8000"
echo "    Swagger 文档: http://localhost:8000/docs"
echo ""
echo "  默认管理员账号（首次启动自动创建）:"
echo "    用户名: ${DEFAULT_ADMIN_USERNAME:-admin}"
echo "    密  码: ${DEFAULT_ADMIN_PASSWORD:-admin123}"
echo ""
echo "  前端页面 (http://localhost:5173):"
echo "    游客进场登记:        /entry"
echo "    游客出场登记:        /exit"
echo "    工作人员登录:        /login"
echo "    工作人员进场:        /staff/entry  (需登录)"
echo "    工作人员出场:        /staff/exit   (需登录)"
echo "    数据监控面板:        /dashboard    (需登录)"
echo "    大屏展示:            /screen       (1920x1080 全屏)"
echo ""
echo "============================================"

# 等待子进程
wait $BACKEND_PID $FRONTEND_PID
