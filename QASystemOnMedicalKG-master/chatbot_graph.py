#!/usr/bin/env python3
# coding: utf-8
# File: chatbot_graph.py

import sys
import io
import contextlib

from question_classifier import *
from question_parser import *
from answer_search import *

'''问答类'''
class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        answer = '您好，我是小兔智医药智能助理，希望可以帮到您。如果没答上来，我会继续努力学习。祝您身体棒棒！'
        res_classify = self.classifier.classify(sent)
        if not res_classify:
            return answer
        res_sql = self.parser.parser_main(res_classify)
        final_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            qtypes = res_classify.get('question_types') or []
            args = res_classify.get('args') or {}
            is_drug_intent = any(t in ('drug_disease', 'disease_drug') for t in qtypes)
            has_drug_entity = any('drug' in (types or []) for types in args.values())
            if is_drug_intent and has_drug_entity:
                drug_terms = [k for k, types in args.items() if 'drug' in (types or [])]
                term = drug_terms[0] if drug_terms else ''
                cands = self.searcher.suggest_similar_drugs(term, limit=5)
                if cands:
                    return '我没有查到“{0}”的直接结果。你是不是想问：{1}？\n\n你可以这样问：\n- {2}有什么作用？\n- {2}主治什么病？'.format(term, '；'.join(cands), cands[0])
                return '我暂时没查到“{0}”相关药物信息。请尝试补全药名（如“{0}片/胶囊/注射液”）或换一个更完整的药品名称。'.format(term)

            return answer
        else:
            return '\n'.join(final_answers)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        question = ' '.join(sys.argv[1:]).strip()
        if not question:
            sys.exit(0)
        with contextlib.redirect_stdout(io.StringIO()):
            handler = ChatBotGraph()
            answer = handler.chat_main(question)
        print(answer)
        sys.exit(0)

    handler = ChatBotGraph()
    while 1:
        question = input('用户:')
        answer = handler.chat_main(question)
        print('小兔智:', answer)

