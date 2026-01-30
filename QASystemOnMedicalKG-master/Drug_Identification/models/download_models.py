#!/usr/bin/env python3
# coding: utf-8
"""
下载预训练模型脚本
"""

import os
import urllib.request
import sys

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

# 模型下载配置
MODELS = {
    'east': {
        'filename': 'frozen_east_text_detection.pb',
        'url': 'https://github.com/oyyd/frozen_east_text_detection.pb/raw/master/frozen_east_text_detection.pb',
        'size_mb': 95,
    },
}


def download_file(url, output_path, desc=""):
    """下载文件并显示进度"""
    print(f"下载 {desc}: {url}")
    print(f"保存到: {output_path}")
    
    try:
        def progress_hook(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\r下载进度: {percent}%")
            sys.stdout.flush()
        
        urllib.request.urlretrieve(url, output_path, progress_hook)
        print("\n下载完成!")
        return True
    except Exception as e:
        print(f"\n下载失败: {e}")
        return False


def download_east():
    """下载 EAST 模型"""
    config = MODELS['east']
    output_path = os.path.join(MODELS_DIR, config['filename'])
    
    if os.path.exists(output_path):
        print(f"EAST 模型已存在: {output_path}")
        return True
    
    print(f"EAST 模型大小约 {config['size_mb']} MB")
    return download_file(config['url'], output_path, "EAST 文本检测模型")


def download_all():
    """下载所有模型"""
    print("=" * 60)
    print("药品识别系统 - 模型下载工具")
    print("=" * 60)
    
    # 下载 EAST
    print("\n[1/1] 下载 EAST 模型...")
    download_east()
    
    print("\n" + "=" * 60)
    print("模型下载完成!")
    print("=" * 60)


if __name__ == '__main__':
    download_all()
