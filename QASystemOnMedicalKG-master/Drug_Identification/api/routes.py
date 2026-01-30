#!/usr/bin/env python3
# coding: utf-8
"""
API 路由定义
"""

import os
import time
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import ImageProcessor, OCRExtractor, TextParser, DrugMatcher, TextDetector
from models.schemas import DrugIdentifyResponse
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 初始化组件（延迟加载）
_image_processor = None
_ocr_extractor = None
_text_parser = None
_drug_matcher = None
_text_detector = None


def get_image_processor():
    global _image_processor
    if _image_processor is None:
        _image_processor = ImageProcessor()
    return _image_processor


def get_ocr_extractor():
    global _ocr_extractor
    if _ocr_extractor is None:
        _ocr_extractor = OCRExtractor()
    return _ocr_extractor


def get_text_parser():
    global _text_parser
    if _text_parser is None:
        _text_parser = TextParser()
    return _text_parser


def get_drug_matcher():
    global _drug_matcher
    if _drug_matcher is None:
        _drug_matcher = DrugMatcher()
    return _drug_matcher


def get_text_detector():
    global _text_detector
    if _text_detector is None:
        _text_detector = TextDetector()
    return _text_detector


def allowed_file(filename):
    """检查文件扩展名"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api_bp.route('/identify', methods=['POST'])
def identify_drug():
    """
    药品识别接口（支持多图上传）
    
    请求方式：
    1. multipart/form-data: 上传图片文件
       - image: 单张图片文件（兼容旧版）
       - images: 多张图片文件（1-6张，新版多图上传）
       - enhance: 是否增强 (可选, 默认 true)
       
    2. application/json: 传入图片 URL 或 base64
       - image_url: 图片 URL
       - image_base64: base64 编码的图片
       - enhance: 是否增强
    
    返回：
    {
        "success": true,
        "ocr_text": "提取的文字",
        "parsed_info": {...},
        "match_type": "approval_no",
        "matched_drug": {...},
        "drug_info": {...},
        "confidence": 0.95,
        "process_time_ms": 1234,
        "images_processed": 3
    }
    """
    start_time = time.time()
    
    try:
        # 获取图片数据
        image_data_list = []
        enhance = True
        
        if request.content_type and 'multipart/form-data' in request.content_type:
            enhance = request.form.get('enhance', 'true').lower() == 'true'
            
            # 支持多图上传（新版）
            if 'images' in request.files:
                files = request.files.getlist('images')
                for file in files:
                    if file.filename == '':
                        continue
                    if not allowed_file(file.filename):
                        continue
                    image_data = file.read()
                    image_data_list.append(image_data)
                    
                    # 保存上传的图片
                    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                    save_path = os.path.join(UPLOAD_FOLDER, filename)
                    with open(save_path, 'wb') as f:
                        f.write(image_data)
            
            # 兼容单图上传（旧版）
            elif 'image' in request.files:
                file = request.files['image']
                if file.filename == '':
                    return jsonify(DrugIdentifyResponse.error('未选择文件').to_dict()), 400
                
                if not allowed_file(file.filename):
                    return jsonify(DrugIdentifyResponse.error('不支持的文件格式').to_dict()), 400
                
                image_data = file.read()
                image_data_list.append(image_data)
                
                # 保存上传的图片
                filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                with open(save_path, 'wb') as f:
                    f.write(image_data)
            else:
                return jsonify(DrugIdentifyResponse.error('请上传图片文件').to_dict()), 400
        
        elif request.is_json:
            data = request.get_json()
            enhance = data.get('enhance', True)
            
            if data.get('image_base64'):
                import base64
                image_data = base64.b64decode(data['image_base64'])
                image_data_list.append(image_data)
            elif data.get('image_url'):
                import requests as req
                resp = req.get(data['image_url'], timeout=10)
                resp.raise_for_status()
                image_data_list.append(resp.content)
            else:
                return jsonify(DrugIdentifyResponse.error('请提供图片').to_dict()), 400
        else:
            return jsonify(DrugIdentifyResponse.error('不支持的请求格式').to_dict()), 400
        
        if not image_data_list:
            return jsonify(DrugIdentifyResponse.error('未找到有效图片').to_dict()), 400
        
        # 多图处理流程
        processor = get_image_processor()
        ocr = get_ocr_extractor()
        parser = get_text_parser()
        matcher = get_drug_matcher()
        
        # 收集所有图片的OCR结果
        all_ocr_texts = []
        all_ocr_lines = []
        all_parsed_infos = []
        all_ocr_errors = []
        
        for image_data in image_data_list:
            # 1. 图片预处理
            processed_image = processor.preprocess(image_data, enhance=enhance)
            
            # 2. OCR 提取
            ocr_result = ocr.extract(processed_image)
            all_ocr_texts.append(ocr_result.get('raw_text', '') or '')
            all_ocr_lines.extend(ocr_result.get('lines', []) or [])
            if ocr_result.get('error'):
                all_ocr_errors.append(str(ocr_result.get('error')))
            
            # 3. 文字解析
            parsed_info = parser.parse(ocr_result)
            all_parsed_infos.append(parsed_info)
        
        # 4. 合并多图解析结果
        merged_parsed_info = merge_parsed_infos(all_parsed_infos)
        merged_ocr_text = '\n---\n'.join(all_ocr_texts)
        
        # 5. 药品匹配（使用合并后的信息）
        match_result = matcher.match(merged_parsed_info)
        
        # 计算处理时间
        process_time = int((time.time() - start_time) * 1000)
        
        # 构建响应
        merged_ocr_result = {
            'raw_text': merged_ocr_text,
            'lines': all_ocr_lines,
        }
        response = DrugIdentifyResponse.from_results(
            merged_ocr_result, merged_parsed_info, match_result, process_time
        )
        
        # 添加多图处理信息
        response_dict = response.to_dict()
        response_dict['images_processed'] = len(image_data_list)

        # 便于排查：返回 OCR 引擎与错误信息
        response_dict['ocr_engine'] = getattr(ocr, 'engine', 'unknown')
        if all_ocr_errors:
            response_dict['ocr_error'] = '; '.join(sorted(set(all_ocr_errors)))

        # 便于排查：数据库不可用/连接失败时，把真实原因透出
        if (not match_result.get('success')) and match_result.get('error'):
            response_dict['message'] = str(match_result.get('error'))
        
        return jsonify(response_dict)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify(DrugIdentifyResponse.error(f'处理失败: {str(e)}').to_dict()), 500


@api_bp.route('/ocr/batch', methods=['POST'])
def ocr_batch():
    start_time = time.time()

    try:
        image_data_list = []
        enhance = True

        if request.content_type and 'multipart/form-data' in request.content_type:
            enhance = request.form.get('enhance', 'true').lower() == 'true'

            if 'images' in request.files:
                files = request.files.getlist('images')
                for file in files:
                    if file.filename == '':
                        continue
                    if not allowed_file(file.filename):
                        continue
                    image_data_list.append(file.read())
            elif 'image' in request.files:
                file = request.files['image']
                if file.filename == '':
                    return jsonify({'success': False, 'error': '未选择文件'}), 400
                if not allowed_file(file.filename):
                    return jsonify({'success': False, 'error': '不支持的文件格式'}), 400
                image_data_list.append(file.read())
            else:
                return jsonify({'success': False, 'error': '请上传图片文件'}), 400
        else:
            return jsonify({'success': False, 'error': '不支持的请求格式'}), 400

        if not image_data_list:
            return jsonify({'success': False, 'error': '未找到有效图片'}), 400

        processor = get_image_processor()
        ocr = get_ocr_extractor()
        parser = get_text_parser()

        all_ocr_texts = []
        all_ocr_lines = []
        all_parsed_infos = []
        all_ocr_errors = []

        for image_data in image_data_list:
            processed_image = processor.preprocess(image_data, enhance=enhance)
            ocr_result = ocr.extract(processed_image)
            all_ocr_texts.append(ocr_result.get('raw_text', '') or '')
            all_ocr_lines.extend(ocr_result.get('lines', []) or [])
            if ocr_result.get('error'):
                all_ocr_errors.append(str(ocr_result.get('error')))
            all_parsed_infos.append(parser.parse(ocr_result))

        merged_parsed_info = merge_parsed_infos(all_parsed_infos)
        merged_ocr_text = '\n---\n'.join(all_ocr_texts)

        process_time = int((time.time() - start_time) * 1000)

        resp = {
            'success': bool(merged_ocr_text.strip()) or bool(merged_parsed_info),
            'message': 'OCR 完成' if (merged_ocr_text.strip() or merged_parsed_info) else 'OCR 未识别到有效文字',
            'match_type': 'ocr_only',
            'confidence': float(merged_parsed_info.get('confidence', 0.0) or 0.0),
            'ocr_text': merged_ocr_text,
            'ocr_lines': all_ocr_lines,
            'parsed_info': merged_parsed_info,
            'drug_info': merged_parsed_info,
            'matched_drug': None,
            'candidates': [],
            'process_time_ms': process_time,
            'images_processed': len(image_data_list),
            'ocr_engine': getattr(ocr, 'engine', 'unknown'),
        }
        if all_ocr_errors:
            resp['ocr_error'] = '; '.join(sorted(set(all_ocr_errors)))
        return jsonify(resp)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


def merge_parsed_infos(parsed_infos):
    """
    合并多张图片的解析结果
    优先使用非空值，多个值时选择置信度最高或最完整的
    """
    if not parsed_infos:
        return {}
    
    if len(parsed_infos) == 1:
        return parsed_infos[0]
    
    merged = {}

    for info in parsed_infos:
        if not isinstance(info, dict):
            continue
        for k, v in info.items():
            if v is None:
                continue
            if isinstance(v, str):
                vv = v.strip()
                if not vv or vv in ('None', 'null'):
                    continue
                cur = merged.get(k)
                if not cur:
                    merged[k] = vv
                else:
                    merged[k] = max(str(cur), vv, key=len)
            elif isinstance(v, (int, float)):
                if k == 'confidence':
                    merged[k] = max(float(merged.get(k, 0.0)), float(v))
                elif k not in merged:
                    merged[k] = v
            elif isinstance(v, list):
                cur = merged.get(k)
                if not isinstance(cur, list):
                    cur = []
                for item in v:
                    if item not in cur:
                        cur.append(item)
                if cur:
                    merged[k] = cur
            else:
                if k not in merged:
                    merged[k] = v

    return merged


@api_bp.route('/search', methods=['GET', 'POST'])
def search_drug():
    """
    药品搜索接口
    
    GET /api/search?q=阿莫西林
    POST /api/search {"keyword": "阿莫西林"}
    """
    try:
        if request.method == 'GET':
            keyword = request.args.get('q') or request.args.get('keyword', '')
        else:
            data = request.get_json() or {}
            keyword = data.get('keyword', '')
        
        keyword = keyword.strip()
        if not keyword:
            return jsonify({'success': False, 'error': '请提供搜索关键词'}), 400
        
        matcher = get_drug_matcher()
        result = matcher.search_by_keyword(keyword)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'service': 'Drug Identification API',
        'version': '1.0.0',
    })


@api_bp.route('/ocr', methods=['POST'])
def ocr_only():
    """
    仅 OCR 提取（不匹配药品库）
    用于调试或查看 OCR 效果
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': '请上传图片'}), 400
        
        file = request.files['image']
        image_data = file.read()
        
        # 预处理
        processor = get_image_processor()
        processed = processor.preprocess(image_data)
        
        # OCR
        ocr = get_ocr_extractor()
        result = ocr.extract(processed)
        
        # 解析
        parser = get_text_parser()
        parsed = parser.parse(result)
        
        return jsonify({
            'ocr_result': result,
            'parsed_info': parsed,
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/detect', methods=['POST'])
def detect_text():
    """
    文本区域检测（使用 CRAFT 或 OpenCV）
    返回图像中的文字区域边界框
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': '请上传图片'}), 400
        
        file = request.files['image']
        image_data = file.read()
        
        # 预处理
        processor = get_image_processor()
        processed = processor.preprocess(image_data)
        
        # 文本检测
        detector = get_text_detector()
        result = detector.detect(processed)
        
        return jsonify({
            'success': True,
            'boxes': result.get('boxes', []),
            'num_regions': len(result.get('boxes', [])),
            'method': result.get('method', 'craft'),
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/ocr/engines', methods=['GET'])
def get_ocr_engines():
    """
    获取可用的 OCR 引擎列表
    """
    ocr = get_ocr_extractor()
    engines = ocr.get_available_engines()
    return jsonify({
        'engines': engines,
        'current': ocr.engine,
    })


@api_bp.route('/ocr/multi', methods=['POST'])
def ocr_multi_engine():
    """
    多引擎融合 OCR
    使用多个 OCR 引擎识别，返回最佳结果
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': '请上传图片'}), 400
        
        file = request.files['image']
        image_data = file.read()
        
        # 预处理
        processor = get_image_processor()
        processed = processor.preprocess(image_data)
        
        # 多引擎 OCR
        ocr = get_ocr_extractor()
        result = ocr.extract_multi_engine(processed)
        
        # 解析
        parser = get_text_parser()
        parsed = parser.parse(result)
        
        return jsonify({
            'success': True,
            'ocr_result': result,
            'parsed_info': parsed,
            'engines_used': result.get('fusion_engines', [ocr.engine]),
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/ocr/drug', methods=['POST'])
def ocr_drug_box():
    """
    药盒专用 OCR
    针对药盒优化的 OCR 提取，包含文字清理和格式修复
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': '请上传图片'}), 400
        
        file = request.files['image']
        image_data = file.read()
        
        # 预处理
        processor = get_image_processor()
        processed = processor.preprocess(image_data)
        
        # 药盒专用 OCR
        ocr = get_ocr_extractor()
        result = ocr.extract_for_drug_box(processed)
        
        # 解析
        parser = get_text_parser()
        parsed = parser.parse(result)
        
        return jsonify({
            'success': True,
            'ocr_result': result,
            'parsed_info': parsed,
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
