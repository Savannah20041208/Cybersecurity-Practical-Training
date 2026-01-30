#!/usr/bin/env python3
# coding: utf-8
"""
药品匹配模块
基于解析出的信息匹配药品数据库，补全缺失信息
"""

import os
import sys
import re
from typing import Dict, List, Optional

# 添加父目录到路径，以便导入 drug_lookup
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

try:
    from drug_lookup import DrugLookup
    DRUG_LOOKUP_AVAILABLE = True
except ImportError:
    DRUG_LOOKUP_AVAILABLE = False
    print("[Warning] drug_lookup 模块不可用")


class DrugMatcher:
    """药品匹配器"""

    def __init__(self):
        """初始化匹配器"""
        self.drug_lookup = None
        if DRUG_LOOKUP_AVAILABLE:
            try:
                self.drug_lookup = DrugLookup()
                print("[DrugMatcher] 已连接药品数据库")
            except Exception as e:
                print(f"[DrugMatcher] 连接药品数据库失败: {e}")

    def match(self, parsed_info: Dict) -> Dict:
        """
        匹配药品并补全信息
        
        Args:
            parsed_info: 从 TextParser 解析出的信息
            
        Returns:
            {
                'success': True/False,
                'match_type': 'approval_no' | 'name_enterprise' | 'fuzzy' | 'none',
                'matched_drug': {...},      # 匹配到的药品完整信息
                'candidates': [...],        # 候选列表（模糊匹配时）
                'merged_info': {...},       # 合并后的完整信息
                'confidence': 0.95,
            }
        """
        result = {
            'success': False,
            'match_type': 'none',
            'matched_drug': None,
            'candidates': [],
            'merged_info': parsed_info.copy(),
            'confidence': 0.0,
        }

        if not self.drug_lookup:
            result['error'] = '药品数据库不可用'
            return result

        # 策略1：批准文号精确匹配
        if parsed_info.get('approval_no'):
            match_result = self.drug_lookup.lookup(parsed_info['approval_no'])
            if match_result.get('match_type') == 'approval_no' and match_result.get('drug'):
                result['success'] = True
                result['match_type'] = 'approval_no'
                result['matched_drug'] = match_result['drug']
                result['confidence'] = 0.98
                result['merged_info'] = self._merge_info(parsed_info, match_result['drug'])
                return result

        # 策略2：药品名 + 企业名组合匹配
        if parsed_info.get('drug_name'):
            enterprise = parsed_info.get('enterprise')
            match_result = self.drug_lookup.lookup(parsed_info['drug_name'], enterprise)
            
            if match_result.get('match_type') == 'name_enterprise' and match_result.get('drug'):
                result['success'] = True
                result['match_type'] = 'name_enterprise'
                result['matched_drug'] = match_result['drug']
                result['confidence'] = 0.90
                result['merged_info'] = self._merge_info(parsed_info, match_result['drug'])
                return result

        # 策略3：模糊匹配
        search_terms = self._get_search_terms(parsed_info)
        
        for term in search_terms:
            match_result = self.drug_lookup.lookup(term)
            
            if match_result.get('match_type') == 'fuzzy' and match_result.get('candidates'):
                result['match_type'] = 'fuzzy'
                result['candidates'] = match_result['candidates'][:10]
                
                # 如果有高分候选，选择第一个
                if result['candidates'] and result['candidates'][0].get('score', 0) >= 80:
                    result['success'] = True
                    result['matched_drug'] = result['candidates'][0]
                    result['confidence'] = result['candidates'][0].get('score', 0) / 100
                    result['merged_info'] = self._merge_info(parsed_info, result['candidates'][0])
                
                return result

        # 策略4：尝试从所有提取的文本中搜索
        all_texts = parsed_info.get('all_texts', [])
        for text in all_texts:
            # 清理文本
            cleaned = self._clean_text(text)
            if len(cleaned) < 2 or len(cleaned) > 20:
                continue
            
            match_result = self.drug_lookup.lookup(cleaned)
            if match_result.get('candidates'):
                result['match_type'] = 'fuzzy'
                result['candidates'] = match_result['candidates'][:10]
                if result['candidates'] and result['candidates'][0].get('score', 0) >= 70:
                    result['success'] = True
                    result['matched_drug'] = result['candidates'][0]
                    result['confidence'] = result['candidates'][0].get('score', 0) / 100
                    result['merged_info'] = self._merge_info(parsed_info, result['candidates'][0])
                return result

        return result

    def _get_search_terms(self, parsed_info: Dict) -> List[str]:
        """获取搜索词列表"""
        terms = []
        
        # 药品名
        if parsed_info.get('drug_name'):
            terms.append(parsed_info['drug_name'])
            # 去掉剂型后缀
            name = parsed_info['drug_name']
            for suffix in ['片', '胶囊', '颗粒', '口服液', '注射液', '软膏', '乳膏']:
                if name.endswith(suffix):
                    terms.append(name[:-len(suffix)])
                    break
        
        # 商品名
        if parsed_info.get('brand_name'):
            terms.append(parsed_info['brand_name'])
        
        return terms

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 去除特殊字符
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', text)
        return text.strip()

    def _merge_info(self, parsed_info: Dict, matched_drug: Dict) -> Dict:
        """
        合并解析信息和匹配到的药品信息
        优先使用匹配到的权威数据，OCR 数据作为补充
        """
        merged = {}
        
        # 字段映射：(目标字段, OCR字段, 数据库字段)
        field_mapping = [
            ('approval_no', 'approval_no', 'approval_no'),
            ('generic_name', 'drug_name', 'generic_name'),
            ('brand_name', 'brand_name', 'brand_name'),
            ('dosage_form', 'dosage_form', 'dosage_form'),
            ('spec', 'spec', 'spec'),
            ('enterprise', 'enterprise', 'enterprise'),
            ('otc_type', 'otc_type', 'otc_type'),
            ('indications', None, 'indications'),
            ('usage', None, 'usage'),
            ('contraindications', None, 'contraindications'),
            ('warnings', None, 'warnings'),
            ('adverse_reactions', None, 'adverse_reactions'),
            ('interactions', None, 'interactions'),
            ('special_population', None, 'special_population'),
            ('storage', None, 'storage'),
            ('validity', None, 'validity'),
            ('ingredients', None, 'ingredients'),
            ('packing', None, 'packing'),
        ]
        
        for target, ocr_field, db_field in field_mapping:
            # 优先使用数据库数据
            db_value = matched_drug.get(db_field)
            if db_value and str(db_value).strip() and str(db_value) != 'None':
                merged[target] = db_value
            # 其次使用 OCR 数据
            elif ocr_field:
                ocr_value = parsed_info.get(ocr_field)
                if ocr_value and str(ocr_value).strip():
                    merged[target] = ocr_value
        
        # 添加来源信息
        merged['source'] = 'merged'
        merged['ocr_raw_text'] = parsed_info.get('raw_text', '')
        
        return merged

    def search_by_keyword(self, keyword: str) -> Dict:
        """
        直接按关键词搜索
        """
        if not self.drug_lookup:
            return {'success': False, 'error': '药品数据库不可用'}
        
        result = self.drug_lookup.lookup(keyword)
        return {
            'success': result.get('drug') is not None or bool(result.get('candidates')),
            'match_type': result.get('match_type', 'none'),
            'drug': result.get('drug'),
            'candidates': result.get('candidates', []),
        }
