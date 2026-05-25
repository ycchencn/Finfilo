# ===== 阶段一：构建 Vue 前端 =====
FROM node:24-slim AS frontend-builder
WORKDIR /build
COPY . .
RUN npm install
RUN npm run build

# ===== 阶段二：构建 Python 后端 =====
FROM finfilo-base
WORKDIR /app
# 安装pip包
COPY . .
COPY --from=frontend-builder /build/dist /app/dist
CMD ["python3","run_app.py"]