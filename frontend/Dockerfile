# 前端 Dockerfile - 多阶段构建
# 第一阶段：Node.js 构建 Vue3 + Vite 应用
FROM node:22-alpine AS build-stage

WORKDIR /app

# 设置 npm 国内镜像源（国内 VPS 加速下载）
RUN npm config set registry https://registry.npmmirror.com/

# 复制依赖文件（需要 devDependencies 用于 vue-tsc、vite 等构建工具）
COPY package*.json ./
RUN npm ci

# 复制源代码并构建
COPY . .
RUN npm run build

# 第二阶段：Nginx 运行阶段
FROM nginx:alpine

# 复制构建产物到 Nginx 静态文件目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制 Nginx 配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露前端端口
EXPOSE 80

# 前台运行 Nginx
CMD ["nginx", "-g", "daemon off;"]
