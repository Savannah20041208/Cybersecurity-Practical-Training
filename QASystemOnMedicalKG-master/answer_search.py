#!/usr/bin/env python3
# coding: utf-8
# File: answer_search.py

from py2neo import Graph
import json
import os

class AnswerSearcher:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(base_dir, "data", "medical.json")
        print(f"数据文件路径: {self.data_path}")

        config_path = os.path.join(base_dir, "config", "database_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            db_config = json.load(f)
        neo4j_cfg = (db_config or {}).get("neo4j", {})
        uri = neo4j_cfg.get("uri") or "bolt://localhost:7687"
        username = neo4j_cfg.get("username") or "neo4j"
        password = neo4j_cfg.get("password") or "password"
        database = neo4j_cfg.get("database")

        self._neo4j_uri = uri
        self._neo4j_username = username
        self._neo4j_password = password
        self._neo4j_database = database
        self._neo4j_database_supported = True

        if database:
            self.g = Graph(uri, name=database, auth=(username, password))
        else:
            self.g = Graph(uri, auth=(username, password))
        self.num_limit = 5

    def suggest_similar_drugs(self, term: str, limit: int = 5):
        if not term:
            return []
        try:
            q = (term or '').strip()
            cypher = (
                "MATCH (n:Drug) "
                "WHERE replace(n.name,' ','') CONTAINS replace($q,' ','') "
                "   OR replace($q,' ','') CONTAINS replace(n.name,' ','') "
                "RETURN n.name as name "
                "LIMIT $limit"
            )
            rows = self.g.run(cypher, q=q, limit=int(limit)).data()
            return [r.get('name') for r in rows if r.get('name')]
        except Exception:
            return []

    '''执行cypher查询，并返回相应结果'''
    def search_main(self, sqls):
        final_answers = []
        for sql_ in sqls:
            question_type = sql_['question_type']
            queries = sql_['sql']
            answers = []
            for query in queries:
                try:
                    ress = self.g.run(query).data()
                    answers += ress
                except TypeError as e:
                    msg = str(e)
                    if (
                        self._neo4j_database
                        and self._neo4j_database_supported
                        and 'Database selection is not supported' in msg
                    ):
                        self._neo4j_database_supported = False
                        self.g = Graph(self._neo4j_uri, auth=(self._neo4j_username, self._neo4j_password))
                        ress = self.g.run(query).data()
                        answers += ress
                    else:
                        raise
            final_answer = self.answer_prettify(question_type, answers)
            if final_answer:
                final_answers.append(final_answer)
        return final_answers

    '''根据对应的qustion_type，调用相应的回复模板'''
    def answer_prettify(self, question_type, answers):
        final_answer = []
        if not answers:
            return ''
        if question_type == 'disease_symptom':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的症状包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'symptom_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '症状{0}可能染上的疾病有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_cause':
            desc = [i['m.cause'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}可能的成因有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_prevent':
            desc = [i['m.prevent'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的预防措施包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_lasttime':
            desc = [str(i.get('m.cure_lasttime')) for i in answers if i.get('m.cure_lasttime') is not None]
            subject = answers[0]['m.name']
            final_answer = '{0}治疗可能持续的周期为：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_cureway':
            desc = []
            for i in answers:
                if 'n.name' in i and i.get('n.name'):
                    desc.append(i.get('n.name'))
                    continue
                v = i.get('m.cure_way')
                if isinstance(v, (list, tuple)):
                    desc.append(';'.join([str(x) for x in v if x is not None]))
                else:
                    desc.append(str(v) if v is not None else '')
            subject = answers[0]['m.name']
            final_answer = '{0}可以尝试如下治疗：{1}'.format(subject, '；'.join([x for x in list(set(desc)) if x][:self.num_limit]))

        elif question_type == 'disease_cureprob':
            desc = [str(i.get('m.cured_prob')) for i in answers if i.get('m.cured_prob') is not None]
            subject = answers[0]['m.name']
            final_answer = '{0}治愈的概率为（仅供参考）：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_easyget':
            desc = []
            for i in answers:
                v = i.get('m.easy_get')
                if v is None:
                    continue
                if isinstance(v, (list, tuple)):
                    desc.append('；'.join([str(x) for x in v if x is not None]))
                else:
                    desc.append(str(v))
            subject = answers[0]['m.name']

            final_answer = '{0}的易感人群包括：{1}'.format(subject, '；'.join([x for x in list(set(desc)) if x][:self.num_limit]))

        elif question_type == 'disease_desc':
            desc = []
            for i in answers:
                v = i.get('m.description')
                if v is None:
                    v = i.get('m.desc')
                if v is not None:
                    desc.append(v)
            subject = answers[0]['m.name']
            final_answer = '{0},熟悉一下：{1}'.format(subject,  '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_acompany':
            desc1 = [i['n.name'] for i in answers]
            desc2 = [i['m.name'] for i in answers]
            subject = answers[0]['m.name']
            desc = [i for i in desc1 + desc2 if i != subject]
            final_answer = '{0}的症状包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_not_food':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}忌食的食物包括有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_do_food':
            do_desc = [i['n.name'] for i in answers if i['r.name'] == '宜吃']
            recommand_desc = [i['n.name'] for i in answers if i['r.name'] == '推荐食谱']
            subject = answers[0]['m.name']
            final_answer = '{0}宜食的食物包括有：{1}\n推荐食谱包括有：{2}'.format(subject, ';'.join(list(set(do_desc))[:self.num_limit]), ';'.join(list(set(recommand_desc))[:self.num_limit]))

        elif question_type == 'food_not_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '患有{0}的人最好不要吃{1}'.format('；'.join(list(set(desc))[:self.num_limit]), subject)

        elif question_type == 'food_do_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '患有{0}的人建议多试试{1}'.format('；'.join(list(set(desc))[:self.num_limit]), subject)

        elif question_type == 'disease_drug':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}通常的使用的药品包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'drug_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '{0}主治的疾病有{1},可以试试'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_check':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}通常可以通过以下方式检查出来：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'check_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '通常可以通过{0}检查出来的疾病有{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_department':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}建议挂号科室：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        return final_answer


if __name__ == '__main__':
    searcher = AnswerSearcher()