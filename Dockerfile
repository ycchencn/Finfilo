# ===== 阶段二：构建 Python 后端 =====
FROM finfilo-base
WORKDIR /app
# 安装pip包
COPY . .
CMD ["python3","run_app.py"]