# app.py
from flask import Flask
import os

app = Flask(__name__, static_folder='public')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    """统一静态文件路由：支持根目录及子路径回退到 index.html"""
    # 尝试查找对应静态文件
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        resp = app.send_static_file(path)
        # 生产环境建议开启浏览器缓存
        resp.headers['Cache-Control'] = 'public, max-age=86400'
        return resp

    # 无匹配文件时，默认返回首页（兼容 SPA 路由或单页应用模式）
    return app.send_static_file('./index.html')


if __name__ == '__main__':
    # 生产部署建议使用 gunicorn 或 uWSGI，此处保留 Flask 开发模式配置示例
    app.run(host='0.0.0.0', port=8080, debug=False)
