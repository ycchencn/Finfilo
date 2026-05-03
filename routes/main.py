"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

# routes/main.py
from flask import Blueprint, send_from_directory
from app import app

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return send_from_directory(app.static_folder, './index.html')

@main_bp.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)
