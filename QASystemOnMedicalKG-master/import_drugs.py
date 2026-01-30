#!/usr/bin/env python3
# coding: utf-8
"""
药品数据导入脚本 - 用于拍药盒识别后的信息补全
支持 JSONL / CSV 增量导入，批准文号做唯一键，MERGE 语义去重

用法:
    python import_drugs.py --file data/drugs_structured.jsonl
    python import_drugs.py --file data/drugs_structured.csv
    python import_drugs.py --init-schema   # 仅初始化约束和索引
"""

import os
import sys
import json
import csv
import argparse
from py2neo import Graph

# ============ 配置 ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'database_config.json')

def get_graph():
    """读取配置并连接 Neo4j"""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        db_config = json.load(f)
    neo4j_cfg = db_config.get('neo4j', {})
    uri = neo4j_cfg.get('uri') or 'bolt://localhost:7687'
    username = neo4j_cfg.get('username') or 'neo4j'
    password = neo4j_cfg.get('password') or 'password'
    return Graph(uri, auth=(username, password))

# ============ Schema 初始化 ============
def init_schema(graph):
    """
    创建约束和索引（幂等，可重复执行）
    - DrugProduct: 药品产品节点（以批准文号为唯一键）
    - DrugAlias: 药品别名节点（商品名/通用名的变体）
    - Enterprise: 生产企业
    """
    print("[Schema] 初始化约束和索引...")

    # Neo4j 3.x 语法（如果你用 4.x+ 可改成 CREATE CONSTRAINT ... IF NOT EXISTS）
    constraints = [
        # 批准文号唯一约束
        "CREATE CONSTRAINT ON (d:DrugProduct) ASSERT d.approval_no IS UNIQUE",
        # 企业名唯一
        "CREATE CONSTRAINT ON (e:Enterprise) ASSERT e.name IS UNIQUE",
    ]
    indexes = [
        # 通用名索引（高频查询）
        "CREATE INDEX ON :DrugProduct(generic_name)",
        # 商品名索引
        "CREATE INDEX ON :DrugProduct(brand_name)",
        # 别名索引
        "CREATE INDEX ON :DrugAlias(name)",
        # 企业名索引（已有唯一约束会自动建索引，这里显式写一下）
    ]

    for cypher in constraints:
        try:
            graph.run(cypher)
            print(f"  [OK] {cypher[:60]}...")
        except Exception as e:
            if 'already exists' in str(e).lower() or 'equivalent' in str(e).lower():
                print(f"  [SKIP] 约束已存在")
            else:
                print(f"  [WARN] {e}")

    for cypher in indexes:
        try:
            graph.run(cypher)
            print(f"  [OK] {cypher[:60]}...")
        except Exception as e:
            if 'already exists' in str(e).lower() or 'equivalent' in str(e).lower():
                print(f"  [SKIP] 索引已存在")
            else:
                print(f"  [WARN] {e}")

    print("[Schema] 完成\n")

# ============ 数据读取 ============
def read_jsonl(filepath):
    """逐行读取 JSONL 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def read_csv_file(filepath):
    """读取 CSV 文件，首行为表头"""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 把空字符串转为 None
            yield {k: (v.strip() if v and v.strip() else None) for k, v in row.items()}

def read_data(filepath):
    """根据后缀自动选择读取方式"""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.jsonl':
        return read_jsonl(filepath)
    elif ext == '.csv':
        return read_csv_file(filepath)
    elif ext == '.json':
        # 整个文件是一个 JSON 数组
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return iter(data)
    else:
        raise ValueError(f"不支持的文件格式: {ext}，请使用 .jsonl / .csv / .json")

# ============ 导入逻辑 ============
def normalize_approval_no(s):
    """归一化批准文号：去空格、统一大写"""
    if not s:
        return None
    return s.strip().upper().replace(' ', '').replace('　', '')

def import_drug(graph, drug_dict):
    """
    导入单条药品记录（MERGE 语义）
    drug_dict 字段参考 drugs_structured.jsonl 模板
    """
    approval_no = normalize_approval_no(drug_dict.get('approval_no'))
    if not approval_no:
        return False, "缺少批准文号"

    generic_name = (drug_dict.get('generic_name') or '').strip() or None
    brand_name = (drug_dict.get('brand_name') or '').strip() or None
    dosage_form = (drug_dict.get('dosage_form') or '').strip() or None
    spec = (drug_dict.get('spec') or '').strip() or None
    otc_type = (drug_dict.get('otc_type') or '').strip() or None
    packing = (drug_dict.get('packing') or '').strip() or None
    ingredients = drug_dict.get('ingredients')  # 可以是字符串或列表
    indications = (drug_dict.get('indications') or '').strip() or None
    usage = (drug_dict.get('usage') or '').strip() or None
    contraindications = (drug_dict.get('contraindications') or '').strip() or None
    warnings = (drug_dict.get('warnings') or '').strip() or None
    adverse_reactions = (drug_dict.get('adverse_reactions') or '').strip() or None
    interactions = (drug_dict.get('interactions') or '').strip() or None
    special_population = (drug_dict.get('special_population') or '').strip() or None
    storage = (drug_dict.get('storage') or '').strip() or None
    validity = (drug_dict.get('validity') or '').strip() or None
    enterprise_name = (drug_dict.get('enterprise') or drug_dict.get('enterprise_name') or '').strip() or None
    aliases = drug_dict.get('aliases') or []  # 别名列表
    source = (drug_dict.get('source') or '').strip() or None
    updated_at = (drug_dict.get('updated_at') or '').strip() or None

    # 成分处理：如果是字符串则按逗号/顿号拆分
    if isinstance(ingredients, str):
        ingredients = [x.strip() for x in ingredients.replace('、', ',').split(',') if x.strip()]
    elif not isinstance(ingredients, list):
        ingredients = []

    # 1. MERGE DrugProduct 节点
    cypher_drug = """
    MERGE (d:DrugProduct {approval_no: $approval_no})
    ON CREATE SET
        d.generic_name = $generic_name,
        d.brand_name = $brand_name,
        d.dosage_form = $dosage_form,
        d.spec = $spec,
        d.otc_type = $otc_type,
        d.packing = $packing,
        d.ingredients = $ingredients,
        d.indications = $indications,
        d.usage = $usage,
        d.contraindications = $contraindications,
        d.warnings = $warnings,
        d.adverse_reactions = $adverse_reactions,
        d.interactions = $interactions,
        d.special_population = $special_population,
        d.storage = $storage,
        d.validity = $validity,
        d.source = $source,
        d.updated_at = $updated_at,
        d.created_at = datetime()
    ON MATCH SET
        d.generic_name = COALESCE($generic_name, d.generic_name),
        d.brand_name = COALESCE($brand_name, d.brand_name),
        d.dosage_form = COALESCE($dosage_form, d.dosage_form),
        d.spec = COALESCE($spec, d.spec),
        d.otc_type = COALESCE($otc_type, d.otc_type),
        d.packing = COALESCE($packing, d.packing),
        d.ingredients = CASE WHEN size($ingredients) > 0 THEN $ingredients ELSE d.ingredients END,
        d.indications = COALESCE($indications, d.indications),
        d.usage = COALESCE($usage, d.usage),
        d.contraindications = COALESCE($contraindications, d.contraindications),
        d.warnings = COALESCE($warnings, d.warnings),
        d.adverse_reactions = COALESCE($adverse_reactions, d.adverse_reactions),
        d.interactions = COALESCE($interactions, d.interactions),
        d.special_population = COALESCE($special_population, d.special_population),
        d.storage = COALESCE($storage, d.storage),
        d.validity = COALESCE($validity, d.validity),
        d.source = COALESCE($source, d.source),
        d.updated_at = COALESCE($updated_at, d.updated_at)
    RETURN d
    """
    graph.run(cypher_drug,
              approval_no=approval_no,
              generic_name=generic_name,
              brand_name=brand_name,
              dosage_form=dosage_form,
              spec=spec,
              otc_type=otc_type,
              packing=packing,
              ingredients=ingredients,
              indications=indications,
              usage=usage,
              contraindications=contraindications,
              warnings=warnings,
              adverse_reactions=adverse_reactions,
              interactions=interactions,
              special_population=special_population,
              storage=storage,
              validity=validity,
              source=source,
              updated_at=updated_at)

    # 2. MERGE Enterprise 节点并建立关系
    if enterprise_name:
        cypher_ent = """
        MERGE (e:Enterprise {name: $name})
        WITH e
        MATCH (d:DrugProduct {approval_no: $approval_no})
        MERGE (d)-[:MADE_BY]->(e)
        """
        graph.run(cypher_ent, name=enterprise_name, approval_no=approval_no)

    # 3. 处理别名（DrugAlias 节点 + HAS_ALIAS 关系）
    # 自动把 generic_name / brand_name 也加入别名（去重）
    all_aliases = set(aliases)
    if generic_name:
        all_aliases.add(generic_name)
    if brand_name:
        all_aliases.add(brand_name)
    for alias in all_aliases:
        alias = alias.strip()
        if not alias:
            continue
        cypher_alias = """
        MERGE (a:DrugAlias {name: $alias_name})
        WITH a
        MATCH (d:DrugProduct {approval_no: $approval_no})
        MERGE (d)-[:HAS_ALIAS]->(a)
        """
        graph.run(cypher_alias, alias_name=alias, approval_no=approval_no)

    return True, None

def import_drugs_batch(graph, filepath, batch_size=500):
    """批量导入药品数据"""
    print(f"[Import] 开始导入: {filepath}")
    success_count = 0
    fail_count = 0
    fail_reasons = []

    for i, drug_dict in enumerate(read_data(filepath), start=1):
        ok, reason = import_drug(graph, drug_dict)
        if ok:
            success_count += 1
        else:
            fail_count += 1
            if len(fail_reasons) < 10:
                fail_reasons.append((i, reason, drug_dict.get('approval_no') or drug_dict.get('generic_name')))

        if i % batch_size == 0:
            print(f"  已处理 {i} 条，成功 {success_count}，失败 {fail_count}")

    print(f"[Import] 完成！共 {success_count + fail_count} 条，成功 {success_count}，失败 {fail_count}")
    if fail_reasons:
        print("[Import] 部分失败示例:")
        for idx, reason, identifier in fail_reasons:
            print(f"  行 {idx}: {reason} ({identifier})")

# ============ 主入口 ============
def main():
    parser = argparse.ArgumentParser(description='药品数据导入 Neo4j')
    parser.add_argument('--file', '-f', help='数据文件路径（.jsonl / .csv / .json）')
    parser.add_argument('--init-schema', action='store_true', help='仅初始化约束和索引')
    args = parser.parse_args()

    graph = get_graph()

    if args.init_schema:
        init_schema(graph)
        return

    if not args.file:
        print("请指定数据文件，例如: python import_drugs.py --file data/drugs_structured.jsonl")
        print("或使用 --init-schema 仅初始化数据库约束")
        sys.exit(1)

    if not os.path.exists(args.file):
        print(f"文件不存在: {args.file}")
        sys.exit(1)

    # 先确保 schema 存在
    init_schema(graph)
    # 导入数据
    import_drugs_batch(graph, args.file)

if __name__ == '__main__':
    main()
