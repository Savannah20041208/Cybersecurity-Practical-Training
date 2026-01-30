#!/usr/bin/env python3
# coding: utf-8
"""
从现有 medical.json 中提取药品数据
并从网络补充药品详细信息（适应症、用法用量、禁忌等）

用法:
    python extract_drugs_from_medical.py                    # 仅提取基础信息
    python extract_drugs_from_medical.py --enrich           # 补充详细信息
    python extract_drugs_from_medical.py --enrich --limit 100  # 限制补充数量
"""

import os
import sys
import json
import time
import random
import argparse
import re
import hashlib
from datetime import datetime
from collections import defaultdict

try:
    import requests
except ImportError:
    print("请先安装依赖: pip install requests")
    sys.exit(1)

# ============ 配置 ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MEDICAL_JSON = os.path.join(DATA_DIR, 'medical.json')
OUTPUT_FILE = os.path.join(DATA_DIR, 'drugs_extracted.jsonl')

REQUEST_DELAY = 2.0
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


def load_medical_data():
    """加载 medical.json"""
    print(f"加载数据: {MEDICAL_JSON}")
    with open(MEDICAL_JSON, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f if line.strip()]
    print(f"  共 {len(data)} 条疾病记录")
    return data


def extract_drugs(medical_data):
    """
    从疾病数据中提取药品信息
    包括：药品名称、关联疾病、药品详情
    """
    drugs = {}  # drug_name -> drug_info
    drug_diseases = defaultdict(set)  # drug_name -> set of diseases

    for disease in medical_data:
        disease_name = disease.get('name', '')

        # 提取常用药品
        for drug_name in (disease.get('common_drug') or []):
            drug_name = drug_name.strip()
            if drug_name:
                drug_diseases[drug_name].add(disease_name)
                if drug_name not in drugs:
                    drugs[drug_name] = {'name': drug_name, 'type': 'common_drug'}

        # 提取推荐药品
        for drug_name in (disease.get('recommand_drug') or []):
            drug_name = drug_name.strip()
            if drug_name:
                drug_diseases[drug_name].add(disease_name)
                if drug_name not in drugs:
                    drugs[drug_name] = {'name': drug_name, 'type': 'recommand_drug'}

        # 提取药品详情（如果有）
        drug_detail = disease.get('drug_detail') or []
        for detail in drug_detail:
            if isinstance(detail, str):
                # 格式可能是 "药品名(功效说明)" 或 "药品名：说明"
                match = re.match(r'^([^(（:：]+)[(（:：](.+)[)）]?$', detail)
                if match:
                    drug_name = match.group(1).strip()
                    drug_desc = match.group(2).strip()
                    if drug_name in drugs:
                        drugs[drug_name]['description'] = drug_desc
                    else:
                        drugs[drug_name] = {
                            'name': drug_name,
                            'type': 'drug_detail',
                            'description': drug_desc
                        }
                    drug_diseases[drug_name].add(disease_name)

    # 合并关联疾病
    for drug_name, disease_set in drug_diseases.items():
        if drug_name in drugs:
            drugs[drug_name]['related_diseases'] = list(disease_set)

    print(f"  提取到 {len(drugs)} 种药品")
    return drugs


def generate_approval_no(drug_name):
    """
    为没有批准文号的药品生成唯一标识
    基于药品名称的哈希值
    """
    # 判断药品类型
    if any(kw in drug_name for kw in ['片', '胶囊', '颗粒', '口服液', '注射', '软膏', '滴眼', '喷雾']):
        prefix = 'H'  # 化学药
    elif any(kw in drug_name for kw in ['丸', '散', '膏', '丹', '酒', '露', '汤', '饮']):
        prefix = 'Z'  # 中成药
    else:
        prefix = 'H'

    # 生成数字部分
    hash_val = int(hashlib.md5(drug_name.encode('utf-8')).hexdigest()[:8], 16) % 100000000
    return f"LOCAL{prefix}{hash_val:08d}"


def parse_drug_name(drug_name):
    """
    解析药品名称，提取通用名、剂型、规格等
    例如：阿莫西林胶囊 -> 通用名=阿莫西林, 剂型=胶囊剂
    """
    result = {
        'generic_name': drug_name,
        'dosage_form': None,
        'brand_name': None,
    }

    # 剂型关键词
    dosage_forms = {
        '片': '片剂', '胶囊': '胶囊剂', '颗粒': '颗粒剂', '口服液': '口服液',
        '注射液': '注射液', '注射用': '注射剂', '软膏': '软膏剂', '乳膏': '乳膏剂',
        '滴眼液': '滴眼液', '滴鼻液': '滴鼻液', '喷雾剂': '喷雾剂', '气雾剂': '气雾剂',
        '栓': '栓剂', '丸': '丸剂', '散': '散剂', '膏': '膏剂', '糖浆': '糖浆剂',
        '合剂': '合剂', '酊': '酊剂', '搽剂': '搽剂', '洗剂': '洗剂', '贴': '贴剂',
        '缓释片': '缓释片', '分散片': '分散片', '肠溶片': '肠溶片', '泡腾片': '泡腾片',
    }

    for suffix, form in dosage_forms.items():
        if drug_name.endswith(suffix):
            result['dosage_form'] = form
            result['generic_name'] = drug_name[:-len(suffix)] + suffix
            break

    return result


def format_drug_for_import(drug_info):
    """
    将提取的药品信息格式化为导入格式
    """
    name = drug_info['name']
    parsed = parse_drug_name(name)

    # 生成批准文号（本地标识）
    approval_no = generate_approval_no(name)

    # 构建适应症（基于关联疾病）
    related_diseases = drug_info.get('related_diseases', [])
    indications = None
    if related_diseases:
        if len(related_diseases) <= 5:
            indications = f"用于{', '.join(related_diseases)}等疾病的治疗。"
        else:
            indications = f"用于{', '.join(related_diseases[:5])}等{len(related_diseases)}种疾病的治疗。"

    return {
        'approval_no': approval_no,
        'generic_name': parsed['generic_name'],
        'brand_name': parsed.get('brand_name'),
        'dosage_form': parsed.get('dosage_form'),
        'spec': None,
        'otc_type': None,
        'enterprise': None,
        'ingredients': None,
        'indications': indications or drug_info.get('description'),
        'usage': None,
        'contraindications': None,
        'warnings': None,
        'adverse_reactions': None,
        'interactions': None,
        'special_population': None,
        'storage': None,
        'validity': None,
        'aliases': [name],
        'related_diseases': related_diseases,
        'source': 'medical.json',
        'source_type': drug_info.get('type', 'extracted'),
        'updated_at': datetime.now().strftime('%Y-%m-%d'),
    }


def enrich_drug_info(drug, session=None):
    """
    从网络补充药品详细信息
    使用百度百科或其他公开来源
    """
    if session is None:
        session = requests.Session()

    drug_name = drug['generic_name']

    # 这里可以添加从百度百科、用药助手等获取详细信息的逻辑
    # 由于这些网站可能有反爬措施，这里只提供框架

    # 示例：尝试从百度百科获取
    try:
        url = f"https://baike.baidu.com/item/{drug_name}"
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        resp = session.get(url, headers=headers, timeout=10, allow_redirects=True)

        if resp.status_code == 200:
            # 简单提取（实际需要更复杂的解析）
            text = resp.text

            # 尝试提取适应症
            if not drug.get('indications'):
                match = re.search(r'适应症[：:]\s*([^<]+)', text)
                if match:
                    drug['indications'] = match.group(1).strip()[:500]

            # 尝试提取用法用量
            if not drug.get('usage'):
                match = re.search(r'用法用量[：:]\s*([^<]+)', text)
                if match:
                    drug['usage'] = match.group(1).strip()[:500]

    except Exception as e:
        pass  # 忽略错误，继续处理

    return drug


def save_drugs(drugs, output_file):
    """保存药品数据"""
    print(f"\n保存到: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        for drug in drugs:
            f.write(json.dumps(drug, ensure_ascii=False) + '\n')

    print(f"  共保存 {len(drugs)} 条药品记录")


def main():
    parser = argparse.ArgumentParser(description='从 medical.json 提取药品数据')
    parser.add_argument('--enrich', '-e', action='store_true', help='从网络补充详细信息')
    parser.add_argument('--limit', '-l', type=int, default=0, help='限制补充数量（0=全部）')
    parser.add_argument('--output', '-o', default=OUTPUT_FILE, help='输出文件')
    args = parser.parse_args()

    # 1. 加载数据
    medical_data = load_medical_data()

    # 2. 提取药品
    drugs_raw = extract_drugs(medical_data)

    # 3. 格式化
    print("\n格式化药品数据...")
    drugs_formatted = []
    for drug_info in drugs_raw.values():
        formatted = format_drug_for_import(drug_info)
        drugs_formatted.append(formatted)

    # 4. 补充详细信息（可选）
    if args.enrich:
        print("\n从网络补充详细信息...")
        session = requests.Session()
        limit = args.limit if args.limit > 0 else len(drugs_formatted)

        for i, drug in enumerate(drugs_formatted[:limit]):
            if i % 50 == 0:
                print(f"  进度: {i}/{limit}")
            drug = enrich_drug_info(drug, session)
            time.sleep(REQUEST_DELAY)

    # 5. 保存
    save_drugs(drugs_formatted, args.output)

    # 6. 统计
    print(f"\n{'='*50}")
    print("提取完成！")
    print(f"  药品总数: {len(drugs_formatted)}")
    print(f"  输出文件: {args.output}")
    print(f"\n下一步：导入到 Neo4j")
    print(f"  python import_drugs.py --file {args.output}")
    print(f"{'='*50}")


if __name__ == '__main__':
    main()
