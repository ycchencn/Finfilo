FROM finfilo-base
WORKDIR /app
# 安装pip包
COPY install .
CMD ["python3","run_app.py"]