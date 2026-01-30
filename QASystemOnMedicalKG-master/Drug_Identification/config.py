#!/usr/bin/env python3
# coding: utf-8
"""
药品识别系统配置
"""

import os

# 基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

# 上传配置
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Neo4j 配置（从父项目读取）
NEO4J_CONFIG_PATH = os.path.join(PARENT_DIR, 'config', 'database_config.json')

def load_neo4j_config():
    """加载 Neo4j 配置"""
    import json
    if os.path.exists(NEO4J_CONFIG_PATH):
        with open(NEO4J_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return {
                'uri': config.get('neo4j', {}).get('uri', 'bolt://localhost:7687'),
                'user': config.get('neo4j', {}).get('username', 'neo4j'),
                'password': config.get('neo4j', {}).get('password', 'password'),
            }
    return {
        'uri': 'bolt://localhost:7687',
        'user': 'neo4j',
        'password': 'password',
    }

NEO4J_CONFIG = load_neo4j_config()

# OCR 配置
OCR_CONFIG = {
    'use_angle_cls': True,      # 使用方向分类器
    'lang': 'ch',               # 中文
    'use_gpu': False,           # 是否使用 GPU
    'show_log': False,          # 是否显示日志
}

# 服务配置
SERVER_CONFIG = {
    'host': '0.0.0.0',
    'port': 5001,
    'debug': True,
}

# 图像预处理配置
IMAGE_CONFIG = {
    'max_size': 2048,           # 最大边长
    'min_size': 100,            # 最小边长
    'enhance_contrast': True,   # 增强对比度
    'denoise': True,            # 去噪
}

# 匹配配置
MATCH_CONFIG = {
    'fuzzy_threshold': 0.6,     # 模糊匹配阈值
    'max_candidates': 10,       # 最大候选数
}
