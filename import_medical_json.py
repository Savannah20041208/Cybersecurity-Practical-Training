#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
医疗知识图谱JSON数据导入脚本
处理medical.json中的详细医疗数据并导入到Neo4j
"""

from neo4j import GraphDatabase
import json
import re
from pathlib import Path

class MedicalJSONImporter:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.json_file = Path("QASystemOnMedicalKG-master/data/medical.json")
        
    def close(self):
        self.driver.close()
    
    def load_medical_data(self):
        """加载medical.json数据"""
        print("正在加载medical.json数据...")
        
        with open(self.json_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 处理JSON Lines格式（每行一个JSON对象）
        medical_data = []
        for line in content.strip().split('\n'):
            if line.strip():
                try:
                    data = json.loads(line)
                    medical_data.append(data)
                except json.JSONDecodeError as e:
                    print(f"解析JSON行时出错: {e}")
                    continue
        
        print(f"成功加载 {len(medical_data)} 条医疗数据")
        return medical_data
    
    def clear_database(self):
        """清空数据库"""
        with self.driver.session() as session:
            print("正在清空数据库...")
            session.run("MATCH (n) DETACH DELETE n")
            print("数据库已清空")
    
    def create_constraints(self):
        """创建约束"""
        with self.driver.session() as session:
            print("正在创建约束...")
            constraints = [
                "CREATE CONSTRAINT ON (d:Disease) ASSERT d.name IS UNIQUE",
                "CREATE CONSTRAINT ON (s:Symptom) ASSERT s.name IS UNIQUE", 
                "CREATE CONSTRAINT ON (c:Category) ASSERT c.name IS UNIQUE",
                "CREATE CONSTRAINT ON (dept:Department) ASSERT dept.name IS UNIQUE",
                "CREATE CONSTRAINT ON (drug:Drug) ASSERT drug.name IS UNIQUE",
                "CREATE CONSTRAINT ON (check:Check) ASSERT check.name IS UNIQUE",
                "CREATE CONSTRAINT ON (cure:CureWay) ASSERT cure.name IS UNIQUE"
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    if "already exists" not in str(e):
                        print(f"创建约束失败: {e}")
            
            print("约束创建完成")
    
    def clean_text(self, text):
        """清理文本数据"""
        if not text:
            return ""
        if isinstance(text, list):
            return [self.clean_text(item) for item in text if item]
        
        # 移除特殊字符和多余空格
        text = re.sub(r'[^\w\s\u4e00-\u9fff，。、；：！？（）【】""''《》]', '', str(text))
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:500]  # 限制长度
    
    def extract_list_from_text(self, text, max_items=10):
        """从文本中提取列表项"""
        if not text:
            return []
        
        if isinstance(text, list):
            return [self.clean_text(item) for item in text[:max_items] if item]
        
        # 尝试按常见分隔符分割
        items = []
        for separator in ['、', '，', ',', '；', ';', '\n']:
            if separator in text:
                items = [item.strip() for item in text.split(separator) if item.strip()]
                break
        
        if not items:
            items = [text]
        
        return [self.clean_text(item) for item in items[:max_items] if item]
    
    def import_diseases(self, medical_data):
        """导入疾病数据"""
        with self.driver.session() as session:
            print("正在导入疾病数据...")
            
            for i, disease_data in enumerate(medical_data):
                try:
                    # 基本疾病信息
                    name = self.clean_text(disease_data.get('name', ''))
                    desc = self.clean_text(disease_data.get('desc', ''))
                    cause = self.clean_text(disease_data.get('cause', ''))
                    prevent = self.clean_text(disease_data.get('prevent', ''))
                    
                    if not name:
                        continue
                    
                    # 创建疾病节点
                    session.run("""
                        CREATE (d:Disease {
                            name: $name,
                            description: $desc,
                            cause: $cause,
                            prevent: $prevent,
                            get_prob: $get_prob,
                            get_way: $get_way,
                            cure_lasttime: $cure_lasttime,
                            cured_prob: $cured_prob,
                            cost_money: $cost_money,
                            yibao_status: $yibao_status
                        })
                    """, 
                        name=name,
                        desc=desc,
                        cause=cause,
                        prevent=prevent,
                        get_prob=self.clean_text(disease_data.get('get_prob', '')),
                        get_way=self.clean_text(disease_data.get('get_way', '')),
                        cure_lasttime=self.clean_text(disease_data.get('cure_lasttime', '')),
                        cured_prob=self.clean_text(disease_data.get('cured_prob', '')),
                        cost_money=self.clean_text(disease_data.get('cost_money', '')),
                        yibao_status=self.clean_text(disease_data.get('yibao_status', ''))
                    )
                    
                    # 处理症状
                    symptoms = disease_data.get('symptom', [])
                    if isinstance(symptoms, str):
                        symptoms = self.extract_list_from_text(symptoms)
                    elif isinstance(symptoms, list):
                        symptoms = [self.clean_text(s) for s in symptoms if s]
                    
                    for symptom in symptoms[:10]:  # 限制症状数量
                        if symptom:
                            # 创建症状节点
                            session.run("MERGE (s:Symptom {name: $name})", name=symptom)
                            # 创建关系
                            session.run("""
                                MATCH (d:Disease {name: $disease_name})
                                MATCH (s:Symptom {name: $symptom_name})
                                CREATE (d)-[:HAS_SYMPTOM]->(s)
                            """, disease_name=name, symptom_name=symptom)
                    
                    # 处理科室
                    departments = disease_data.get('cure_department', [])
                    if isinstance(departments, str):
                        departments = self.extract_list_from_text(departments)
                    elif isinstance(departments, list):
                        departments = [self.clean_text(d) for d in departments if d]
                    
                    for dept in departments[:5]:  # 限制科室数量
                        if dept:
                            session.run("MERGE (dept:Department {name: $name})", name=dept)
                            session.run("""
                                MATCH (d:Disease {name: $disease_name})
                                MATCH (dept:Department {name: $dept_name})
                                CREATE (d)-[:BELONGS_TO_DEPT]->(dept)
                            """, disease_name=name, dept_name=dept)
                    
                    # 处理治疗方法
                    cure_ways = disease_data.get('cure_way', [])
                    if isinstance(cure_ways, str):
                        cure_ways = self.extract_list_from_text(cure_ways)
                    elif isinstance(cure_ways, list):
                        cure_ways = [self.clean_text(c) for c in cure_ways if c]
                    
                    for cure_way in cure_ways[:5]:
                        if cure_way:
                            session.run("MERGE (c:CureWay {name: $name})", name=cure_way)
                            session.run("""
                                MATCH (d:Disease {name: $disease_name})
                                MATCH (c:CureWay {name: $cure_name})
                                CREATE (d)-[:TREATED_BY]->(c)
                            """, disease_name=name, cure_name=cure_way)
                    
                    # 处理药物
                    drugs = disease_data.get('common_drug', [])
                    if isinstance(drugs, str):
                        drugs = self.extract_list_from_text(drugs)
                    elif isinstance(drugs, list):
                        drugs = [self.clean_text(dr) for dr in drugs if dr]
                    
                    for drug in drugs[:8]:
                        if drug:
                            session.run("MERGE (dr:Drug {name: $name})", name=drug)
                            session.run("""
                                MATCH (d:Disease {name: $disease_name})
                                MATCH (dr:Drug {name: $drug_name})
                                CREATE (d)-[:USES_DRUG]->(dr)
                            """, disease_name=name, drug_name=drug)
                    
                    # 处理检查项目
                    checks = disease_data.get('check', [])
                    if isinstance(checks, str):
                        checks = self.extract_list_from_text(checks)
                    elif isinstance(checks, list):
                        checks = [self.clean_text(ch) for ch in checks if ch]
                    
                    for check in checks[:8]:
                        if check:
                            session.run("MERGE (ch:Check {name: $name})", name=check)
                            session.run("""
                                MATCH (d:Disease {name: $disease_name})
                                MATCH (ch:Check {name: $check_name})
                                CREATE (d)-[:NEED_CHECK]->(ch)
                            """, disease_name=name, check_name=check)
                    
                    # 处理疾病分类
                    categories = disease_data.get('category', [])
                    if isinstance(categories, list):
                        for category in categories:
                            if category:
                                category = self.clean_text(category)
                                session.run("MERGE (cat:Category {name: $name})", name=category)
                                session.run("""
                                    MATCH (d:Disease {name: $disease_name})
                                    MATCH (cat:Category {name: $cat_name})
                                    CREATE (d)-[:BELONGS_TO_CATEGORY]->(cat)
                                """, disease_name=name, cat_name=category)
                    
                    if (i + 1) % 100 == 0:
                        print(f"已导入疾病: {i + 1}/{len(medical_data)}")
                        
                except Exception as e:
                    print(f"导入疾病 {disease_data.get('name', 'Unknown')} 时出错: {e}")
                    continue
            
            print(f"疾病数据导入完成，共处理 {len(medical_data)} 条记录")
    
    def get_statistics(self):
        """获取数据统计"""
        with self.driver.session() as session:
            print("\n=== 医疗知识图谱数据统计 ===")
            
            # 节点统计
            result = session.run("MATCH (n) RETURN labels(n) as labels, count(*) as count")
            total_nodes = 0
            for record in result:
                labels = record["labels"][0] if record["labels"] else "Unknown"
                count = record["count"]
                total_nodes += count
                print(f"{labels}: {count} 个节点")
            
            # 关系统计
            result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(*) as count")
            total_rels = 0
            print("\n关系统计:")
            for record in result:
                rel_type = record["type"]
                count = record["count"]
                total_rels += count
                print(f"{rel_type}: {count} 个关系")
            
            print(f"\n总计: {total_nodes} 个节点, {total_rels} 个关系")
    
    def import_all(self):
        """导入所有数据"""
        try:
            print("开始导入详细医疗知识图谱数据...")
            
            # 加载数据
            medical_data = self.load_medical_data()
            
            if not medical_data:
                print("没有找到医疗数据，请检查文件路径")
                return
            
            # 清空数据库
            self.clear_database()
            
            # 创建约束
            self.create_constraints()
            
            # 导入疾病数据
            self.import_diseases(medical_data)
            
            # 显示统计信息
            self.get_statistics()
            
            print("\n🎉 详细医疗知识图谱数据导入完成！")
            
        except Exception as e:
            print(f"导入过程中出现错误: {e}")
            import traceback
            traceback.print_exc()

def main():
    importer = MedicalJSONImporter()
    try:
        importer.import_all()
    finally:
        importer.close()

if __name__ == "__main__":
    main()
