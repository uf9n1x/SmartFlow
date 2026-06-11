@echo off
chcp 65001 >nul
title 区域人数管控统计系统 - 启动

echo ============================================
echo   区域人数管控统计系统 - 一键启动
echo ============================================
echo.

:: 检查 .env 文件
if not exist ".env" (
    echo [警告] 未找到 .env 文件，请先配置 .env
    echo 请复制 .env.example 为 .env 并修改配置
    pause
    exit /b 1
)

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.12+
    pause
    exit /b 1
)

:: 激活虚拟环境
if exist ".venv\Scripts\activate.bat" (
    echo [信息] 激活虚拟环境...
    call .venv\Scripts\activate.bat
) else (
    echo [警告] 未找到虚拟环境，正在创建...
    uv venv .venv --python 3.12
    call .venv\Scripts\activate.bat
)

:: 安装后端依赖
echo [信息] 检查并安装后端依赖...
uv pip install -r backend\requirements.txt --quiet

:: 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

:: 安装前端依赖
if not exist "frontend\node_modules" (
    echo [信息] 安装前端依赖...
    cd frontend
    call npm install
    cd ..
)

:: 检查 Redis 连接
echo [信息] 检查 Redis 连接 (localhost:6379)...
echo.
:: 使用 curl 或 PowerShell 检查端口是否可达
powershell -Command "try { $tcp = New-Object System.Net.Sockets.TcpClient('localhost', 6379); $tcp.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
    echo [错误] 无法连接 Redis 服务 (localhost:6379)
    echo [提示] 请确保 Redis 已安装并启动，或修改 .env 中的 REDIS_URL 配置
    echo.
    echo 是否仍然继续启动？(Y/N)
    choice /c YN /n /m "请输入 Y 或 N: "
    if errorlevel 2 exit /b 1
) else (
    echo [成功] Redis 连接正常
)

:: 检查 MySQL 连接
echo [信息] 检查 MySQL 连接 (localhost:3306)...
powershell -Command "try { $tcp = New-Object System.Net.Sockets.TcpClient('localhost', 3306); $tcp.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
    echo [错误] 无法连接 MySQL 服务 (localhost:3306)
    echo [提示] 请确保 MySQL 已安装并启动，或修改 .env 中的 DATABASE_URL 配置
    echo.
    echo 是否仍然继续启动？(Y/N)
    choice /c YN /n /m "请输入 Y 或 N: "
    if errorlevel 2 exit /b 1
) else (
    echo [成功] MySQL 连接正常
)
echo.
echo 按任意键启动后端和前端服务...
pause >nul

:: 启动后端
echo [信息] 启动后端 API 服务 (端口 8000)...
start "Backend-API" cmd /c "cd /d %cd%\backend && %cd%\.venv\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000 --reload"

:: 等待后端启动
echo 等待后端服务启动...
timeout /t 3 /nobreak >nul

:: 启动前端
echo [信息] 启动前端开发服务器 (端口 5173)...
start "Frontend-Dev" cmd /c "cd /d %cd%\frontend && npm run dev"

echo.
echo ============================================
echo   系统启动完成！
echo ============================================
echo.
echo   默认管理员账号（首次启动自动创建）:
echo     见 .env 中 DEFAULT_ADMIN_USERNAME / DEFAULT_ADMIN_PASSWORD 配置
echo.
echo   后端服务:
echo     API 接口:       http://localhost:8000
echo     Swagger 文档:   http://localhost:8000/docs
echo.
echo   前端页面 (http://localhost:5173):
echo     游客进场登记:        /entry
echo     游客出场登记:        /exit
echo     工作人员登录:        /login
echo     工作人员进场:        /staff/entry  (需登录)
echo     工作人员出场:        /staff/exit   (需登录)
echo     数据监控面板:        /dashboard    (需登录)
echo     大屏展示:            /screen       (1920x1080 全屏)
echo.
echo ============================================
echo.
echo 按任意键关闭此窗口...
pause >nul
