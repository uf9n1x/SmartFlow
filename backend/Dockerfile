# 后端 Dockerfile
# 基于 Python 3.12 构建 FastAPI 应用镜像
FROM python:3.12-slim

WORKDIR /app

# 替换 Debian APT 源为阿里云镜像（国内 VPS 加速）
RUN sed -i 's@http://deb.debian.org@http://mirrors.aliyun.com@g' /etc/apt/sources.list.d/debian.sources \
    && sed -i 's@http://security.debian.org@http://mirrors.aliyun.com/debian-security@g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 配置 pip 国内镜像源（阿里云 PyPI）
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 复制依赖文件并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露后端服务端口
EXPOSE 8000

# 使用 uvicorn 启动 FastAPI 应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
