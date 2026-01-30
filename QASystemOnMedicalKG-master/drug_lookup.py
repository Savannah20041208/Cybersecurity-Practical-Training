#!/usr/bin/env python3
# coding: utf-8
"""
药品补全查询模块 - 用于拍药盒识别后的信息补全
支持：批准文号精确匹配 -> 企业+名称组合 -> 模糊候选

用法示例:
    from drug_lookup import DrugLookup
    lookup = DrugLookup()
    result = lookup.lookup("国药准字H20000001")  # 精确匹配
    result = lookup.lookup("阿莫西林")           # 模糊匹配，返回候选
"""

import os
import re
import json
from py2neo import Graph

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
    database = neo4j_cfg.get('database')
    if database:
        return Graph(uri, auth=(username, password), name=database)
    return Graph(uri, auth=(username, password))


class DrugLookup:
    """药品补全查询类"""

    def __init__(self, graph=None):
        self.graph = graph or get_graph()

    # ============ 归一化 ============
    @staticmethod
    def normalize_approval_no(s):
        """归一化批准文号：去空格、统一大写"""
        if not s:
            return None
        return s.strip().upper().replace(' ', '').replace('　', '')

    @staticmethod
    def normalize_name(s):
        """归一化药品名：去空格、去括号内容、去常见剂型后缀"""
        if not s:
            return None
        s = s.strip()
        # 去括号内容
        s = re.sub(r'[（(][^）)]*[）)]', '', s)
        # 去常见剂型后缀
        s = re.sub(r'(片|胶囊|颗粒|缓释片|缓释胶囊|分散片|肠溶片|滴丸|口服液|注射液|注射用|软膏|乳膏|凝胶|贴剂|喷雾剂|气雾剂|滴眼液|滴鼻液|栓剂|散剂|丸剂|糖浆|合剂|酊剂|搽剂|洗剂|膏剂|贴膏|橡胶膏)$', '', s)
        s = s.strip()
        return s if s else None

    # ============ 查询方法 ============
    def lookup_by_approval_no(self, approval_no):
        """通过批准文号精确查询"""
        approval_no = self.normalize_approval_no(approval_no)
        if not approval_no:
            return None
        cypher = """
        MATCH (d:DrugProduct {approval_no: $approval_no})
        OPTIONAL MATCH (d)-[:MADE_BY]->(e:Enterprise)
        RETURN d, e.name as enterprise_name
        LIMIT 1
        """
        result = self.graph.run(cypher, approval_no=approval_no).data()
        if result:
            return self._format_drug(result[0]['d'], result[0].get('enterprise_name'))
        return None

    def lookup_by_name_and_enterprise(self, name, enterprise_name):
        """通过名称+企业组合查询"""
        name = self.normalize_name(name)
        if not name or not enterprise_name:
            return None
        cypher = """
        MATCH (d:DrugProduct)-[:MADE_BY]->(e:Enterprise {name: $enterprise_name})
        WHERE d.generic_name CONTAINS $name OR d.brand_name CONTAINS $name
        RETURN d, e.name as enterprise_name
        LIMIT 1
        """
        result = self.graph.run(cypher, name=name, enterprise_name=enterprise_name.strip()).data()
        if result:
            return self._format_drug(result[0]['d'], result[0].get('enterprise_name'))
        return None

    def lookup_fuzzy(self, query, limit=10):
        """
        模糊查询：通过别名/通用名/商品名模糊匹配，返回候选列表
        """
        query_normalized = self.normalize_name(query)
        if not query_normalized:
            return []

        # 1. 先通过别名表查
        cypher_alias = """
        MATCH (a:DrugAlias)
        WHERE a.name CONTAINS $query
        MATCH (d:DrugProduct)-[:HAS_ALIAS]->(a)
        OPTIONAL MATCH (d)-[:MADE_BY]->(e:Enterprise)
        RETURN DISTINCT d, e.name as enterprise_name,
               CASE WHEN a.name = $query THEN 100
                    WHEN a.name STARTS WITH $query THEN 80
                    ELSE 60 END as score
        ORDER BY score DESC
        LIMIT $limit
        """
        results = self.graph.run(cypher_alias, query=query_normalized, limit=limit).data()

        # 2. 如果别名表没结果，直接查 DrugProduct 的 generic_name / brand_name
        if not results:
            cypher_direct = """
            MATCH (d:DrugProduct)
            WHERE d.generic_name CONTAINS $query OR d.brand_name CONTAINS $query
            OPTIONAL MATCH (d)-[:MADE_BY]->(e:Enterprise)
            RETURN DISTINCT d, e.name as enterprise_name,
                   CASE WHEN d.generic_name = $query OR d.brand_name = $query THEN 100
                        WHEN d.generic_name STARTS WITH $query OR d.brand_name STARTS WITH $query THEN 80
                        ELSE 60 END as score
            ORDER BY score DESC
            LIMIT $limit
            """
            results = self.graph.run(cypher_direct, query=query_normalized, limit=limit).data()

        candidates = []
        for row in results:
            drug = self._format_drug(row['d'], row.get('enterprise_name'))
            drug['score'] = row.get('score', 60)
            candidates.append(drug)
        return candidates

    def lookup(self, query, enterprise_name=None):
        """
        统一入口：自动判断查询类型
        返回格式:
        {
            "match_type": "approval_no" | "name_enterprise" | "fuzzy" | "none",
            "drug": {...} | None,          # 精确匹配时返回
            "candidates": [...] | None,    # 模糊匹配时返回候选列表
            "query": "原始查询"
        }
        """
        query = (query or '').strip()
        if not query:
            return {"match_type": "none", "drug": None, "candidates": None, "query": query}

        # 1. 判断是否像批准文号（国药准字 + 字母 + 数字）
        approval_pattern = re.compile(r'国药准字[A-Za-zHZSJBhzsjb]\d{6,}', re.IGNORECASE)
        if approval_pattern.search(query):
            drug = self.lookup_by_approval_no(query)
            if drug:
                return {"match_type": "approval_no", "drug": drug, "candidates": None, "query": query}

        # 2. 如果提供了企业名，尝试组合匹配
        if enterprise_name:
            drug = self.lookup_by_name_and_enterprise(query, enterprise_name)
            if drug:
                return {"match_type": "name_enterprise", "drug": drug, "candidates": None, "query": query}

        # 3. 模糊匹配
        candidates = self.lookup_fuzzy(query)
        if candidates:
            # 如果只有一个候选且得分很高，直接返回
            if len(candidates) == 1 and candidates[0].get('score', 0) >= 100:
                return {"match_type": "fuzzy", "drug": candidates[0], "candidates": None, "query": query}
            return {"match_type": "fuzzy", "drug": None, "candidates": candidates, "query": query}

        return {"match_type": "none", "drug": None, "candidates": None, "query": query}

    # ============ 格式化 ============
    def _format_drug(self, node, enterprise_name=None):
        """将 Neo4j 节点转为前端友好的 dict"""
        if node is None:
            return None
        d = dict(node)
        # 确保关键字段存在
        result = {
            "approval_no": d.get("approval_no"),
            "generic_name": d.get("generic_name"),
            "brand_name": d.get("brand_name"),
            "dosage_form": d.get("dosage_form"),
            "spec": d.get("spec"),
            "otc_type": d.get("otc_type"),
            "packing": d.get("packing"),
            "ingredients": d.get("ingredients") or [],
            "indications": d.get("indications"),
            "usage": d.get("usage"),
            "contraindications": d.get("contraindications"),
            "warnings": d.get("warnings"),
            "adverse_reactions": d.get("adverse_reactions"),
            "interactions": d.get("interactions"),
            "special_population": d.get("special_population"),
            "storage": d.get("storage"),
            "validity": d.get("validity"),
            "source": d.get("source"),
            "updated_at": d.get("updated_at"),
        }
        if enterprise_name:
            result["enterprise"] = enterprise_name
        return result


# ============ CLI 测试 ============
if __name__ == '__main__':
    import sys
    lookup = DrugLookup()
    if len(sys.argv) > 1:
        query = sys.argv[1]
        enterprise = sys.argv[2] if len(sys.argv) > 2 else None
        result = lookup.lookup(query, enterprise)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("用法: python drug_lookup.py <查询内容> [企业名]")
        print("示例: python drug_lookup.py 国药准字H20000001")
        print("      python drug_lookup.py 阿莫西林")
        print("      python drug_lookup.py 阿莫西林 某某制药有限公司")
