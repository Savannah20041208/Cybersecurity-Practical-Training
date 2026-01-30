#!/usr/bin/env python3
# coding: utf-8
"""
OCR 文字提取模块
支持多引擎：PaddleOCR、EasyOCR、Tesseract
"""

import os
import sys
import numpy as np
from typing import List, Dict, Tuple, Optional

# 设置环境变量
os.environ['DISABLE_MODEL_SOURCE_CHECK'] = 'True'
# 禁用 oneDNN 以避免 PaddlePaddle 在某些 CPU 上的兼容性问题
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['PADDLE_DISABLE_MKLDNN'] = '1'
os.environ['FLAGS_enable_pir_api'] = '0'

# 尝试导入 PaddleOCR
PADDLE_AVAILABLE = False
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
    print("[OCR] PaddleOCR 模块加载成功")
except ImportError as e:
    print(f"[Warning] PaddleOCR 未安装: {e}")
except Exception as e:
    print(f"[Warning] PaddleOCR 加载失败: {e}")

# 尝试导入 EasyOCR
EASYOCR_AVAILABLE = False
try:
    import easyocr
    EASYOCR_AVAILABLE = True
    print("[OCR] EasyOCR 模块加载成功")
except ImportError as e:
    print(f"[Warning] EasyOCR 未安装: {e}")
except Exception as e:
    print(f"[Warning] EasyOCR 加载失败: {e}")

# 备用方案：Tesseract
TESSERACT_AVAILABLE = False
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    print("[OCR] Tesseract 模块加载成功")
except ImportError:
    pass


class OCRExtractor:
    """OCR 文字提取器"""

    def __init__(self, use_gpu=False, lang='ch'):
        """
        初始化 OCR 提取器
        
        Args:
            use_gpu: 是否使用 GPU
            lang: 语言，'ch' 中文，'en' 英文
        """
        self.use_gpu = use_gpu
        self.lang = lang
        self.ocr = None
        self.engine = 'none'
        self.init_error = None
        self._init_ocr()

    def _init_ocr(self):
        """初始化 OCR 引擎 - 按优先级尝试：PaddleOCR > EasyOCR > Tesseract"""
        last_error = None
        
        # 1. 尝试 PaddleOCR
        if PADDLE_AVAILABLE:
            # 不同版本的 PaddleOCR 对参数支持不同，按兼容性从高到低尝试
            # 注意：use_angle_cls 在某些版本会导致内部 predict() 报错
            configs = [
                {'lang': self.lang, 'use_angle_cls': False, 'show_log': False},
                {'lang': self.lang, 'show_log': False},
                {'use_angle_cls': False, 'show_log': False},
                {'show_log': False},
                {},
            ]
            
            for i, config in enumerate(configs):
                try:
                    self.ocr = PaddleOCR(**config)
                    self.engine = 'paddleocr'
                    self.init_error = None
                    print(f"[OCR] 使用 PaddleOCR 引擎（配置{i+1}）")
                    return
                except Exception as e:
                    print(f"[OCR] PaddleOCR 配置{i+1}失败: {e}")
                    last_error = f"PaddleOCR 初始化失败: {e}"
                    continue

        # 2. 尝试 EasyOCR
        if EASYOCR_AVAILABLE:
            try:
                # EasyOCR 语言映射
                lang_map = {'ch': ['ch_sim', 'en'], 'en': ['en']}
                langs = lang_map.get(self.lang, ['ch_sim', 'en'])
                self.ocr = easyocr.Reader(langs, gpu=self.use_gpu)
                self.engine = 'easyocr'
                self.init_error = None
                print(f"[OCR] 使用 EasyOCR 引擎（语言: {langs}）")
                return
            except Exception as e:
                print(f"[OCR] EasyOCR 初始化失败: {e}")
                last_error = f"EasyOCR 初始化失败: {e}"

        # 3. 尝试 Tesseract
        if TESSERACT_AVAILABLE:
            self.engine = 'tesseract'
            self.init_error = None
            print("[OCR] 使用 Tesseract 引擎")
            return

        self.engine = 'none'
        self.init_error = last_error or '没有可用的 OCR 引擎（请检查 paddleocr/easyocr/pytesseract 安装情况）'
        print("[OCR] 警告：没有可用的 OCR 引擎")

    def extract(self, image) -> Dict:
        """
        从图片中提取文字
        
        Args:
            image: numpy 数组 (BGR 格式) 或图片路径
            
        Returns:
            {
                'raw_text': '完整的原始文字',
                'lines': [{'text': '文字', 'confidence': 0.95, 'box': [[x1,y1], ...]}],
                'engine': 'paddleocr'
            }
        """
        if self.engine == 'paddleocr':
            return self._extract_paddle(image)
        elif self.engine == 'easyocr':
            return self._extract_easyocr(image)
        elif self.engine == 'tesseract':
            return self._extract_tesseract(image)
        else:
            return {
                'raw_text': '',
                'lines': [],
                'engine': 'none',
                'error': self.init_error or 'OCR 引擎不可用',
            }

    def _extract_paddle(self, image) -> Dict:
        """使用 PaddleOCR 提取"""
        try:
            # PaddleOCR 的调用签名在不同版本间存在差异。
            # 我们初始化时已经通过 use_angle_cls 控制角度分类器，因此这里优先不传 cls，避免
            # 在部分版本里触发 PaddleOCR.predict(...) 不支持 cls 的异常。
            try:
                result = self.ocr.ocr(image)
            except TypeError:
                # 旧/特殊版本可能需要显式参数
                result = self.ocr.ocr(image, det=True, rec=True)
            
            lines = []
            texts = []
            
            if result and result[0]:
                for line in result[0]:
                    box = line[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    text = line[1][0]
                    confidence = line[1][1]
                    
                    lines.append({
                        'text': text,
                        'confidence': float(confidence),
                        'box': box,
                    })
                    texts.append(text)
            
            return {
                'raw_text': '\n'.join(texts),
                'lines': lines,
                'engine': 'paddleocr',
            }
            
        except Exception as e:
            print(f"[OCR] PaddleOCR 提取失败: {e}")
            return {
                'raw_text': '',
                'lines': [],
                'engine': 'paddleocr',
                'error': f"PaddleOCR 提取失败: {e}",
            }

    def _extract_easyocr(self, image) -> Dict:
        """使用 EasyOCR 提取"""
        try:
            # EasyOCR 接受 numpy 数组或文件路径
            result = self.ocr.readtext(image)
            
            lines = []
            texts = []
            
            for detection in result:
                box = detection[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                text = detection[1]
                confidence = detection[2]
                
                lines.append({
                    'text': text,
                    'confidence': float(confidence),
                    'box': box,
                })
                texts.append(text)
            
            return {
                'raw_text': '\n'.join(texts),
                'lines': lines,
                'engine': 'easyocr',
            }
            
        except Exception as e:
            print(f"[OCR] EasyOCR 提取失败: {e}")
            return {
                'raw_text': '',
                'lines': [],
                'engine': 'easyocr',
                'error': f"EasyOCR 提取失败: {e}",
            }

    def _extract_tesseract(self, image) -> Dict:
        """使用 Tesseract 提取"""
        try:
            import cv2
            from PIL import Image
            
            # 转换为 PIL Image
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            else:
                pil_image = Image.open(image)
            
            # OCR
            text = pytesseract.image_to_string(pil_image, lang='chi_sim+eng')
            
            # 获取详细信息
            data = pytesseract.image_to_data(pil_image, lang='chi_sim+eng', output_type=pytesseract.Output.DICT)
            
            lines = []
            for i, txt in enumerate(data['text']):
                if txt.strip():
                    conf = data['conf'][i]
                    if conf > 0:
                        lines.append({
                            'text': txt,
                            'confidence': float(conf) / 100,
                            'box': [[data['left'][i], data['top'][i]]],
                        })
            
            return {
                'raw_text': text,
                'lines': lines,
                'engine': 'tesseract',
            }
            
        except Exception as e:
            print(f"[OCR] Tesseract 提取失败: {e}")
            return {
                'raw_text': '',
                'lines': [],
                'engine': 'tesseract',
                'error': f"Tesseract 提取失败: {e}",
            }

    def _extract_fallback(self, image) -> Dict:
        """备用方案：返回空结果"""
        return {
            'raw_text': '',
            'lines': [],
            'engine': 'none',
            'error': 'OCR 引擎不可用',
        }

    def extract_with_regions(self, image) -> Dict:
        """
        提取文字并按区域分组
        
        将文字按位置分为：顶部、中部、底部
        药盒通常：顶部=品牌/商品名，中部=通用名/规格，底部=企业/批准文号
        """
        result = self.extract(image)
        
        if not result['lines']:
            return result
        
        # 获取图片高度
        if isinstance(image, np.ndarray):
            height = image.shape[0]
        else:
            from PIL import Image
            img = Image.open(image)
            height = img.height
        
        # 按 Y 坐标分组
        top_lines = []
        middle_lines = []
        bottom_lines = []
        
        for line in result['lines']:
            if line['box']:
                y = line['box'][0][1] if isinstance(line['box'][0], list) else line['box'][0]
                
                if y < height * 0.33:
                    top_lines.append(line)
                elif y < height * 0.66:
                    middle_lines.append(line)
                else:
                    bottom_lines.append(line)
        
        result['regions'] = {
            'top': top_lines,
            'middle': middle_lines,
            'bottom': bottom_lines,
        }
        
        return result

    def get_high_confidence_text(self, result: Dict, threshold=0.8) -> List[str]:
        """获取高置信度的文字"""
        return [
            line['text'] 
            for line in result.get('lines', []) 
            if line.get('confidence', 0) >= threshold
        ]

    def extract_with_engine(self, image, engine: str = 'auto') -> Dict:
        """
        使用指定引擎提取文字
        
        Args:
            image: 图片
            engine: 'paddleocr', 'easyocr', 'tesseract', 'auto'
        """
        if engine == 'auto':
            return self.extract(image)
        elif engine == 'paddleocr' and PADDLE_AVAILABLE:
            return self._extract_paddle(image)
        elif engine == 'easyocr' and EASYOCR_AVAILABLE:
            return self._extract_easyocr(image)
        elif engine == 'tesseract' and TESSERACT_AVAILABLE:
            return self._extract_tesseract(image)
        else:
            return self.extract(image)

    def extract_multi_engine(self, image) -> Dict:
        """
        多引擎融合识别 - 提高准确率
        使用多个 OCR 引擎识别，合并结果
        """
        results = []
        
        # 尝试所有可用引擎
        if PADDLE_AVAILABLE:
            try:
                paddle_result = self._extract_paddle(image)
                if paddle_result.get('lines'):
                    results.append(('paddleocr', paddle_result))
            except:
                pass
        
        if EASYOCR_AVAILABLE and self.engine != 'paddleocr':
            try:
                # 临时创建 EasyOCR reader
                lang_map = {'ch': ['ch_sim', 'en'], 'en': ['en']}
                langs = lang_map.get(self.lang, ['ch_sim', 'en'])
                reader = easyocr.Reader(langs, gpu=self.use_gpu)
                easy_result = reader.readtext(image)
                
                lines = []
                texts = []
                for detection in easy_result:
                    lines.append({
                        'text': detection[1],
                        'confidence': float(detection[2]),
                        'box': detection[0],
                    })
                    texts.append(detection[1])
                
                if lines:
                    results.append(('easyocr', {
                        'raw_text': '\n'.join(texts),
                        'lines': lines,
                        'engine': 'easyocr',
                    }))
            except:
                pass
        
        if not results:
            return self._extract_fallback(image)
        
        # 如果只有一个引擎结果，直接返回
        if len(results) == 1:
            return results[0][1]
        
        # 多引擎融合：选择置信度最高的结果
        best_result = max(results, key=lambda x: self._calc_avg_confidence(x[1]))
        best_result[1]['fusion_engines'] = [r[0] for r in results]
        
        return best_result[1]

    def _calc_avg_confidence(self, result: Dict) -> float:
        """计算平均置信度"""
        lines = result.get('lines', [])
        if not lines:
            return 0.0
        return sum(l.get('confidence', 0) for l in lines) / len(lines)

    def extract_for_drug_box(self, image) -> Dict:
        """
        专门针对药盒的 OCR 提取
        优化参数和后处理
        """
        result = self.extract(image)
        
        if not result.get('lines'):
            return result
        
        # 药盒特定的后处理
        processed_lines = []
        for line in result['lines']:
            text = line['text']
            
            # 清理常见的 OCR 错误
            text = self._clean_drug_text(text)
            
            if text.strip():
                line['text'] = text
                processed_lines.append(line)
        
        result['lines'] = processed_lines
        result['raw_text'] = '\n'.join([l['text'] for l in processed_lines])
        
        return result

    def _clean_drug_text(self, text: str) -> str:
        """清理药盒文字的常见 OCR 错误"""
        import re
        
        # 常见替换
        replacements = {
            '囯': '国',
            '薬': '药',
            '製': '制',
            '処': '处',
            '醫': '医',
            '療': '疗',
            '號': '号',
            '準': '准',
            '許': '许',
            '証': '证',
            '廠': '厂',
            '業': '业',
            '産': '产',
            '進': '进',
            '適': '适',
            '應': '应',
            '劑': '剂',
            '錠': '片',
            '膠': '胶',
            '囊': '囊',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # 修复批准文号格式
        # 国药准字H12345678 -> 标准化
        text = re.sub(r'[国國]药[准準]字\s*([A-Za-z])\s*(\d+)', r'国药准字\1\2', text)
        
        return text

    def get_available_engines(self) -> List[str]:
        """获取可用的 OCR 引擎列表"""
        engines = []
        if PADDLE_AVAILABLE:
            engines.append('paddleocr')
        if EASYOCR_AVAILABLE:
            engines.append('easyocr')
        if TESSERACT_AVAILABLE:
            engines.append('tesseract')
        return engines
