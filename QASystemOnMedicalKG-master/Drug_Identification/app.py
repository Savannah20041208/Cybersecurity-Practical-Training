#!/usr/bin/env python3
# coding: utf-8
"""
药品拍照识别系统 - 应用入口
"""

import os
import sys

# ========== 必须在任何 paddle 相关导入之前设置 ==========
# 禁用 oneDNN 以避免 PaddlePaddle 兼容性问题
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['PADDLE_DISABLE_MKLDNN'] = '1'
os.environ['FLAGS_enable_pir_api'] = '0'
os.environ['DISABLE_MODEL_SOURCE_CHECK'] = 'True'
# ======================================================

# 添加当前目录到路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS

from api import api_bp
from config import SERVER_CONFIG, UPLOAD_FOLDER

# 创建 Flask 应用
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# 配置
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 启用 CORS
CORS(app)

# 注册 API 蓝图
app.register_blueprint(api_bp)


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """访问上传的文件"""
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.errorhandler(413)
def too_large(e):
    """文件过大"""
    return {'error': '文件过大，最大支持 16MB'}, 413


@app.errorhandler(404)
def not_found(e):
    """404"""
    return {'error': '接口不存在'}, 404


@app.errorhandler(500)
def server_error(e):
    """500"""
    return {'error': '服务器内部错误'}, 500


if __name__ == '__main__':
    print(f"""
╔══════════════════════════════════════════════════════════╗
║           药品拍照识别系统 (Drug Identification)           ║
╠══════════════════════════════════════════════════════════╣
║  访问地址: http://localhost:{SERVER_CONFIG['port']}                          ║
║  API 文档: http://localhost:{SERVER_CONFIG['port']}/api/health               ║
╠══════════════════════════════════════════════════════════╣
║  接口说明:                                                ║
║  - POST /api/identify  : 上传图片识别药品                 ║
║  - GET  /api/search?q= : 搜索药品                         ║
║  - POST /api/ocr       : 仅 OCR 提取                      ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    app.run(
        host=SERVER_CONFIG['host'],
        port=SERVER_CONFIG['port'],
        debug=SERVER_CONFIG['debug']
    )
