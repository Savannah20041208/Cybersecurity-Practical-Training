#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
医疗知识图谱 - 敏感信息检测系统
检测和保护医疗数据中的敏感信息
"""

import re
import json
import hashlib
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class SensitivePattern:
    """敏感信息模式定义"""
    name: str
    pattern: str
    category: str
    risk_level: str  # low, medium, high, critical
    description: str

class SensitiveDetector:
    def __init__(self):
        self.patterns = self._init_patterns()
        self.whitelist = set()  # 白名单词汇
        self.load_medical_terms()
    
    def _init_patterns(self) -> List[SensitivePattern]:
        """初始化敏感信息检测模式"""
        patterns = [
            # 身份证号
            SensitivePattern(
                name="身份证号",
                pattern=r'\b\d{15}|\d{18}|\d{17}[Xx]\b',
                category="personal_id",
                risk_level="critical",
                description="中国身份证号码"
            ),
            
            # 手机号码
            SensitivePattern(
                name="手机号码",
                pattern=r'\b1[3-9]\d{9}\b',
                category="contact",
                risk_level="high",
                description="中国手机号码"
            ),
            
            # 银行卡号
            SensitivePattern(
                name="银行卡号",
                pattern=r'\b\d{16,19}\b',
                category="financial",
                risk_level="critical",
                description="银行卡或信用卡号"
            ),
            
            # 医保卡号
            SensitivePattern(
                name="医保卡号",
                pattern=r'\b[A-Z0-9]{15,20}\b',
                category="medical_id",
                risk_level="high",
                description="医保卡号码"
            ),
            
            # 邮箱地址
            SensitivePattern(
                name="邮箱地址",
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                category="contact",
                risk_level="medium",
                description="电子邮箱地址"
            ),
            
            # 患者姓名模式（中文姓名）
            SensitivePattern(
                name="中文姓名",
                pattern=r'患者[：:]?([王李张刘陈杨黄赵吴周徐孙马朱胡郭何高林罗郑梁谢宋余唐许韩冯邓曹彭曾萧田董袁潘于蒋蔡余杜叶程苏魏吕丁任沈姚卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔向汤][\u4e00-\u9fa5]{1,3})',
                category="patient_name",
                risk_level="critical",
                description="患者中文姓名"
            ),
            
            # 病历号
            SensitivePattern(
                name="病历号",
                pattern=r'病历号[：:]?\s*([A-Z0-9]{6,15})',
                category="medical_id",
                risk_level="high",
                description="医院病历号"
            ),
            
            # 住院号
            SensitivePattern(
                name="住院号",
                pattern=r'住院号[：:]?\s*([A-Z0-9]{6,15})',
                category="medical_id",
                risk_level="high",
                description="住院号码"
            ),
            
            # 处方药物剂量（可能泄露具体病情）
            SensitivePattern(
                name="具体药物剂量",
                pattern=r'(\d+(?:\.\d+)?)\s*(mg|g|ml|片|粒|支|瓶)\s*(每日|每天|tid|bid|qd|q8h|q12h)',
                category="prescription",
                risk_level="medium",
                description="具体药物剂量信息"
            ),
            
            # 检查结果数值
            SensitivePattern(
                name="检查数值",
                pattern=r'(血压|血糖|血脂|肌酐|尿酸|白细胞|红细胞|血红蛋白)[：:]?\s*(\d+(?:\.\d+)?)\s*(mmHg|mg/dl|mmol/L|μmol/L)',
                category="lab_result",
                risk_level="medium",
                description="具体检查结果数值"
            )
        ]
        return patterns
    
    def load_medical_terms(self):
        """加载医学术语白名单"""
        # 常见医学术语，这些不应被标记为敏感信息
        medical_terms = {
            "高血压", "糖尿病", "冠心病", "脑梗死", "肺炎", "胃炎",
            "阿司匹林", "美托洛尔", "二甲双胍", "硝苯地平",
            "头痛", "发热", "咳嗽", "胸痛", "腹痛", "恶心",
            "内科", "外科", "妇科", "儿科", "急诊科"
        }
        self.whitelist.update(medical_terms)
    
    def detect_sensitive_info(self, text: str) -> List[Dict[str, Any]]:
        """检测文本中的敏感信息"""
        detections = []
        
        for pattern in self.patterns:
            matches = re.finditer(pattern.pattern, text, re.IGNORECASE)
            
            for match in matches:
                matched_text = match.group()
                
                # 检查是否在白名单中
                if matched_text.lower() in self.whitelist:
                    continue
                
                # 对于银行卡号，进行额外验证（Luhn算法）
                if pattern.name == "银行卡号" and not self._validate_card_number(matched_text):
                    continue
                
                detection = {
                    "type": pattern.name,
                    "category": pattern.category,
                    "risk_level": pattern.risk_level,
                    "matched_text": matched_text,
                    "start_pos": match.start(),
                    "end_pos": match.end(),
                    "description": pattern.description,
                    "confidence": self._calculate_confidence(pattern, matched_text)
                }
                detections.append(detection)
        
        return detections
    
    def _validate_card_number(self, card_number: str) -> bool:
        """使用Luhn算法验证银行卡号"""
        def luhn_checksum(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            return checksum % 10
        
        return luhn_checksum(card_number) == 0
    
    def _calculate_confidence(self, pattern: SensitivePattern, matched_text: str) -> float:
        """计算检测置信度"""
        base_confidence = 0.8
        
        # 根据匹配长度调整置信度
        if pattern.name == "身份证号":
            if len(matched_text) == 18:
                return 0.95
            elif len(matched_text) == 15:
                return 0.85
        
        if pattern.name == "手机号码":
            return 0.9
        
        if pattern.name == "银行卡号":
            return 0.85
        
        return base_confidence
    
    def mask_sensitive_info(self, text: str, mask_char: str = '*') -> Tuple[str, List[Dict]]:
        """遮蔽敏感信息"""
        detections = self.detect_sensitive_info(text)
        masked_text = text
        offset = 0
        
        # 按位置排序，从后往前处理避免位置偏移
        detections.sort(key=lambda x: x['start_pos'], reverse=True)
        
        for detection in detections:
            start = detection['start_pos']
            end = detection['end_pos']
            matched_text = detection['matched_text']
            
            # 根据敏感信息类型决定遮蔽策略
            if detection['risk_level'] == 'critical':
                # 完全遮蔽
                mask = mask_char * len(matched_text)
            elif detection['risk_level'] == 'high':
                # 部分遮蔽（保留前后几位）
                if len(matched_text) > 6:
                    mask = matched_text[:2] + mask_char * (len(matched_text) - 4) + matched_text[-2:]
                else:
                    mask = mask_char * len(matched_text)
            else:
                # 轻度遮蔽
                mask = matched_text[:1] + mask_char * (len(matched_text) - 2) + matched_text[-1:]
            
            masked_text = masked_text[:start] + mask + masked_text[end:]
        
        return masked_text, detections
    
    def generate_hash_id(self, sensitive_text: str) -> str:
        """为敏感信息生成哈希ID用于日志记录"""
        return hashlib.sha256(sensitive_text.encode()).hexdigest()[:16]
    
    def get_risk_summary(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成风险摘要"""
        if not detections:
            return {
                "total_count": 0,
                "risk_level": "safe",
                "categories": {},
                "recommendation": "未检测到敏感信息"
            }
        
        risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        categories = {}
        
        for detection in detections:
            risk_level = detection['risk_level']
            category = detection['category']
            
            risk_counts[risk_level] += 1
            categories[category] = categories.get(category, 0) + 1
        
        # 确定整体风险等级
        if risk_counts['critical'] > 0:
            overall_risk = "critical"
            recommendation = "检测到极高风险敏感信息，建议立即处理"
        elif risk_counts['high'] > 0:
            overall_risk = "high"
            recommendation = "检测到高风险敏感信息，需要谨慎处理"
        elif risk_counts['medium'] > 0:
            overall_risk = "medium"
            recommendation = "检测到中等风险敏感信息，建议脱敏处理"
        else:
            overall_risk = "low"
            recommendation = "检测到低风险敏感信息，可考虑脱敏"
        
        return {
            "total_count": len(detections),
            "risk_level": overall_risk,
            "risk_counts": risk_counts,
            "categories": categories,
            "recommendation": recommendation
        }
    
    def is_safe_for_logging(self, text: str) -> bool:
        """判断文本是否可以安全记录到日志"""
        detections = self.detect_sensitive_info(text)
        critical_detections = [d for d in detections if d['risk_level'] == 'critical']
        return len(critical_detections) == 0

# 使用示例函数
def demo():
    """演示敏感信息检测功能"""
    detector = SensitiveDetector()
    
    test_texts = [
        "患者王小明，身份证号：110101199001011234，手机：13812345678",
        "血压：140/90mmHg，血糖：7.5mmol/L",
        "处方：阿司匹林100mg每日一次",
        "普通的医学咨询：什么是高血压？"
    ]
    
    for text in test_texts:
        print(f"\n原文: {text}")
        
        detections = detector.detect_sensitive_info(text)
        print(f"检测结果: {len(detections)}项敏感信息")
        
        for detection in detections:
            print(f"  - {detection['type']}: {detection['matched_text']} (风险级别: {detection['risk_level']})")
        
        masked_text, _ = detector.mask_sensitive_info(text)
        print(f"脱敏后: {masked_text}")
        
        summary = detector.get_risk_summary(detections)
        print(f"风险摘要: {summary['recommendation']}")

if __name__ == "__main__":
    demo()
