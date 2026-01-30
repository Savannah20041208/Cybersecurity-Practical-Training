#!/usr/bin/env python3
# coding: utf-8
"""
文字解析模块
从 OCR 提取的原始文字中解析出药品相关信息
"""

import re
from typing import Dict, List, Optional


class TextParser:
    """药盒文字解析器"""

    # 批准文号正则表达式
    APPROVAL_NO_PATTERNS = [
        # 国药准字 H/Z/S/J/B + 8位数字
        r'国药准字\s*[HZSJB]\s*\d{8}',
        r'国药准字\s*[HZSJB]\s*\d{4}\s*\d{4}',
        # 简写形式
        r'准字\s*[HZSJB]\s*\d{8}',
        # 进口药品
        r'进口药品注册证号\s*[A-Z]*\d+',
        r'注册证号\s*[A-Z]*\d+',
        # 医疗器械
        r'[国械注准|国械注进]\s*\d+',
    ]

    # 规格正则
    SPEC_PATTERNS = [
        r'\d+\.?\d*\s*[mμ]?[gG克毫微][\s/×xX*]*\d*\s*[片粒袋支瓶盒]*',
        r'\d+\.?\d*\s*[mM][lL毫升][\s/×xX*]*\d*\s*[支瓶盒]*',
        r'\d+\.?\d*\s*[IiUu单位][\s/×xX*]*\d*',
        r'每[片粒袋支][含有]?\s*\d+\.?\d*\s*[mμ]?[gG克毫微]',
    ]

    # 剂型关键词
    DOSAGE_FORMS = [
        '片', '胶囊', '颗粒', '口服液', '注射液', '注射用', '软膏', '乳膏',
        '滴眼液', '滴鼻液', '喷雾剂', '气雾剂', '栓', '丸', '散', '膏',
        '糖浆', '合剂', '酊', '搽剂', '洗剂', '贴', '缓释片', '分散片',
        '肠溶片', '泡腾片', '咀嚼片', '含片', '滴丸', '胶丸', '软胶囊',
        '硬胶囊', '干混悬剂', '混悬液', '溶液', '乳剂', '凝胶',
    ]

    # OTC 标识
    OTC_PATTERNS = [
        r'OTC',
        r'非处方药',
        r'甲类\s*OTC',
        r'乙类\s*OTC',
    ]

    # 企业名称特征词
    ENTERPRISE_KEYWORDS = [
        '制药', '药业', '药厂', '生物', '医药', '集团', '有限公司',
        '股份', '科技', '实业', '工业', '化学', '中药',
    ]

    def __init__(self):
        # 编译正则表达式
        self.approval_regex = [re.compile(p, re.IGNORECASE) for p in self.APPROVAL_NO_PATTERNS]
        self.spec_regex = [re.compile(p) for p in self.SPEC_PATTERNS]
        self.otc_regex = [re.compile(p, re.IGNORECASE) for p in self.OTC_PATTERNS]

    def parse(self, ocr_result: Dict) -> Dict:
        """
        解析 OCR 结果，提取药品信息
        
        Args:
            ocr_result: OCR 提取结果 {'raw_text': ..., 'lines': [...]}
            
        Returns:
            {
                'approval_no': '国药准字H20000001',
                'drug_name': '阿莫西林胶囊',
                'brand_name': '阿莫仙',
                'enterprise': '某某制药有限公司',
                'spec': '0.25g*24粒',
                'dosage_form': '胶囊剂',
                'otc_type': 'OTC甲类',
                'raw_text': '原始文字',
                'confidence': 0.85,
            }
        """
        raw_text = ocr_result.get('raw_text', '')
        lines = ocr_result.get('lines', [])
        
        # 提取各字段
        result = {
            'approval_no': self._extract_approval_no(raw_text),
            'spec': self._extract_spec(raw_text),
            'dosage_form': self._extract_dosage_form(raw_text),
            'otc_type': self._extract_otc(raw_text),
            'enterprise': self._extract_enterprise(raw_text, lines),
            'drug_name': None,
            'brand_name': None,
            'raw_text': raw_text,
            'all_texts': [line['text'] for line in lines],
        }
        
        # 提取药品名称（通用名和商品名）
        names = self._extract_drug_names(raw_text, lines, result)
        result['drug_name'] = names.get('generic_name')
        result['brand_name'] = names.get('brand_name')
        
        # 计算整体置信度
        result['confidence'] = self._calculate_confidence(result, lines)
        
        return result

    def _extract_approval_no(self, text: str) -> Optional[str]:
        """提取批准文号"""
        for regex in self.approval_regex:
            match = regex.search(text)
            if match:
                # 清理空格
                return re.sub(r'\s+', '', match.group())
        return None

    def _extract_spec(self, text: str) -> Optional[str]:
        """提取规格"""
        for regex in self.spec_regex:
            match = regex.search(text)
            if match:
                return match.group().strip()
        return None

    def _extract_dosage_form(self, text: str) -> Optional[str]:
        """提取剂型"""
        for form in self.DOSAGE_FORMS:
            if form in text:
                return form + ('剂' if form not in ['片', '丸', '散', '膏', '栓', '贴'] else '')
        return None

    def _extract_otc(self, text: str) -> Optional[str]:
        """提取 OTC 分类"""
        for regex in self.otc_regex:
            match = regex.search(text)
            if match:
                matched = match.group()
                if '甲' in matched or '甲类' in text:
                    return 'OTC甲类'
                elif '乙' in matched or '乙类' in text:
                    return 'OTC乙类'
                else:
                    return 'OTC'
        
        if '处方药' in text and 'OTC' not in text.upper():
            return '处方药'
        
        return None

    def _extract_enterprise(self, text: str, lines: List[Dict]) -> Optional[str]:
        """提取生产企业"""
        # 方法1：查找包含企业关键词的行
        for line in lines:
            line_text = line.get('text', '')
            if any(kw in line_text for kw in self.ENTERPRISE_KEYWORDS):
                # 清理前缀
                cleaned = re.sub(r'^(生产企业|生产厂家|企业名称|制造商)[：:]\s*', '', line_text)
                if len(cleaned) >= 4:  # 企业名至少4个字
                    return cleaned.strip()
        
        # 方法2：正则匹配
        patterns = [
            r'([\u4e00-\u9fa5]+(?:制药|药业|药厂|医药|生物)[\u4e00-\u9fa5]*(?:有限公司|股份|集团)[\u4e00-\u9fa5]*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None

    def _extract_drug_names(self, text: str, lines: List[Dict], parsed: Dict) -> Dict:
        """
        提取药品名称
        
        策略：
        1. 排除已识别的批准文号、企业、规格等
        2. 查找包含剂型关键词的文本作为通用名
        3. 较短的独立文本可能是商品名
        """
        result = {'generic_name': None, 'brand_name': None}
        
        # 收集候选名称
        candidates = []
        
        for line in lines:
            line_text = line.get('text', '').strip()
            confidence = line.get('confidence', 0)
            
            # 跳过太短或太长的
            if len(line_text) < 2 or len(line_text) > 30:
                continue
            
            # 跳过已识别的内容
            if parsed.get('approval_no') and parsed['approval_no'] in line_text:
                continue
            if parsed.get('enterprise') and line_text in parsed['enterprise']:
                continue
            if parsed.get('spec') and parsed['spec'] in line_text:
                continue
            
            # 跳过明显不是药名的
            skip_keywords = ['生产', '批准', '有效期', '批号', '规格', '成份', '用法', '用量', 
                           '适应', '禁忌', '注意', '贮藏', '包装', '执行标准', '说明书']
            if any(kw in line_text for kw in skip_keywords):
                continue
            
            candidates.append({
                'text': line_text,
                'confidence': confidence,
                'has_dosage_form': any(form in line_text for form in self.DOSAGE_FORMS),
            })
        
        # 排序：优先选择包含剂型的、置信度高的
        candidates.sort(key=lambda x: (x['has_dosage_form'], x['confidence']), reverse=True)
        
        # 第一个包含剂型的作为通用名
        for c in candidates:
            if c['has_dosage_form']:
                result['generic_name'] = c['text']
                break
        
        # 其他短文本作为商品名候选
        for c in candidates:
            if c['text'] != result.get('generic_name'):
                if 2 <= len(c['text']) <= 10 and not c['has_dosage_form']:
                    result['brand_name'] = c['text']
                    break
        
        # 如果没找到通用名，取第一个候选
        if not result['generic_name'] and candidates:
            result['generic_name'] = candidates[0]['text']
        
        return result

    def _calculate_confidence(self, result: Dict, lines: List[Dict]) -> float:
        """计算整体置信度"""
        score = 0.0
        weights = {
            'approval_no': 0.3,
            'drug_name': 0.25,
            'enterprise': 0.15,
            'spec': 0.1,
            'dosage_form': 0.1,
            'otc_type': 0.1,
        }
        
        for field, weight in weights.items():
            if result.get(field):
                score += weight
        
        # 加上 OCR 平均置信度
        if lines:
            avg_conf = sum(l.get('confidence', 0) for l in lines) / len(lines)
            score = score * 0.7 + avg_conf * 0.3
        
        return round(score, 2)

    def get_search_keywords(self, parsed: Dict) -> List[str]:
        """
        获取用于搜索药品数据库的关键词
        按优先级排序
        """
        keywords = []
        
        # 批准文号最优先
        if parsed.get('approval_no'):
            keywords.append(parsed['approval_no'])
        
        # 药品名称
        if parsed.get('drug_name'):
            keywords.append(parsed['drug_name'])
        
        # 商品名
        if parsed.get('brand_name'):
            keywords.append(parsed['brand_name'])
        
        # 企业名
        if parsed.get('enterprise'):
            keywords.append(parsed['enterprise'])
        
        return keywords
