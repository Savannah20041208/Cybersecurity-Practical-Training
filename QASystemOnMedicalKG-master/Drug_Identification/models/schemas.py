#!/usr/bin/env python3
# coding: utf-8
"""
数据模型定义
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class DrugIdentifyRequest:
    """药品识别请求"""
    image_data: bytes = None          # 图片二进制数据
    image_path: str = None            # 图片路径
    image_url: str = None             # 图片 URL
    enhance: bool = True              # 是否增强图片
    auto_rotate: bool = False         # 是否自动旋转


@dataclass
class OCRResult:
    """OCR 结果"""
    raw_text: str = ''
    lines: List[Dict] = field(default_factory=list)
    engine: str = 'unknown'
    regions: Dict = field(default_factory=dict)


@dataclass
class ParsedInfo:
    """解析后的药品信息"""
    approval_no: Optional[str] = None
    drug_name: Optional[str] = None
    brand_name: Optional[str] = None
    enterprise: Optional[str] = None
    spec: Optional[str] = None
    dosage_form: Optional[str] = None
    otc_type: Optional[str] = None
    raw_text: str = ''
    confidence: float = 0.0


@dataclass
class MatchedDrug:
    """匹配到的药品"""
    approval_no: str = ''
    generic_name: str = ''
    brand_name: Optional[str] = None
    dosage_form: Optional[str] = None
    spec: Optional[str] = None
    enterprise: Optional[str] = None
    otc_type: Optional[str] = None
    indications: Optional[str] = None
    usage: Optional[str] = None
    contraindications: Optional[str] = None
    warnings: Optional[str] = None
    adverse_reactions: Optional[str] = None
    interactions: Optional[str] = None
    special_population: Optional[str] = None
    storage: Optional[str] = None
    validity: Optional[str] = None
    ingredients: Optional[List[str]] = None
    packing: Optional[str] = None
    source: str = ''
    updated_at: str = ''


@dataclass
class DrugIdentifyResponse:
    """药品识别响应"""
    success: bool = False
    message: str = ''
    
    # OCR 结果
    ocr_text: str = ''
    ocr_lines: List[Dict] = field(default_factory=list)
    
    # 解析结果
    parsed_info: Dict = field(default_factory=dict)
    
    # 匹配结果
    match_type: str = 'none'  # approval_no | name_enterprise | fuzzy | none
    matched_drug: Optional[Dict] = None
    candidates: List[Dict] = field(default_factory=list)
    
    # 合并后的完整信息
    drug_info: Dict = field(default_factory=dict)
    
    # 置信度
    confidence: float = 0.0
    
    # 处理时间
    process_time_ms: int = 0
    
    # 时间戳
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def error(cls, message: str) -> 'DrugIdentifyResponse':
        """创建错误响应"""
        return cls(success=False, message=message)

    @classmethod
    def from_results(cls, ocr_result: Dict, parsed_info: Dict, 
                     match_result: Dict, process_time: int) -> 'DrugIdentifyResponse':
        """从处理结果创建响应"""
        return cls(
            success=match_result.get('success', False),
            message='识别成功' if match_result.get('success') else '未找到匹配药品',
            ocr_text=ocr_result.get('raw_text', ''),
            ocr_lines=ocr_result.get('lines', []),
            parsed_info=parsed_info,
            match_type=match_result.get('match_type', 'none'),
            matched_drug=match_result.get('matched_drug'),
            candidates=match_result.get('candidates', []),
            drug_info=match_result.get('merged_info', {}),
            confidence=match_result.get('confidence', 0.0),
            process_time_ms=process_time,
        )
