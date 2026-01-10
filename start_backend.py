#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
启动智慧医疗知识服务平台后端
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import json

app = Flask(__name__)
CORS(app)

# 用户数据库
users = {
    "admin": "medical_admin_2024",
    "Savannah": "password",
    "user": "123456",
    "test": "test123"
}

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        print(f"登录尝试: 用户名={username}, 密码={'*' * len(password)}")
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400
        
        # 验证用户凭据
        if username in users and users[username] == password:
            # 生成token
            token = f"token_{username}_{datetime.datetime.now().timestamp()}"
            
            return jsonify({
                'success': True,
                'message': '登录成功',
                'token': token,
                'user': {
                    'username': username,
                    'role': 'admin' if username == 'admin' else 'user'
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
            
    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500

@app.route('/api/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'message': '问题不能为空'
            }), 400
        
        # 模拟医疗问答
        answer = generate_medical_answer(question)
        
        return jsonify({
            'success': True,
            'answer': answer,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"问答错误: {e}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500

def generate_medical_answer(question):
    """生成医疗问答回复"""
    question_lower = question.lower()
    
    # 疾病相关问答
    if '感冒' in question_lower:
        return "感冒是常见的呼吸道感染疾病。主要症状包括发热、咳嗽、流鼻涕、头痛等。建议多休息、多喝水，必要时可服用感冒药。如症状严重或持续时间长，请及时就医。"
    elif '高血压' in question_lower:
        return "高血压是血压持续升高的慢性疾病。主要症状可能包括头痛、头晕、心悸等。治疗方法包括控制饮食、适量运动、按时服药。建议定期监测血压，遵医嘱用药。"
    elif '糖尿病' in question_lower:
        return "糖尿病是血糖代谢异常的慢性疾病。典型症状包括多饮、多尿、多食、体重下降。治疗包括控制血糖、饮食管理、胰岛素治疗等。建议定期检查血糖，保持健康生活方式。"
    elif '发热' in question_lower or '发烧' in question_lower:
        return "发热是身体对感染或疾病的正常反应。轻度发热可通过物理降温、多喝水来缓解。如体温超过38.5°C或持续不退，建议及时就医检查原因。"
    elif '咳嗽' in question_lower:
        return "咳嗽可能由多种原因引起，如感冒、过敏、肺炎等。建议多喝温水、保持室内湿润。如咳嗽持续超过一周或伴有其他症状，请及时就医。"
    elif '头痛' in question_lower:
        return "头痛可能由多种因素引起，如紧张、疲劳、高血压等。建议充分休息、放松心情。如头痛频繁或剧烈，建议就医检查。"
    elif '失眠' in question_lower:
        return "失眠是指难以入睡或睡眠质量差的症状。可能由压力、焦虑、不良生活习惯等引起。建议保持规律作息、避免睡前使用电子设备、适量运动。如持续失眠，请咨询医生。"
    elif '便秘' in question_lower:
        return "便秘是指排便困难或排便次数减少。建议多喝水、增加膳食纤维摄入、适量运动。可多吃蔬菜水果、全谷物食品。如症状持续，请就医检查。"
    
    # 食物营养相关问答
    elif '蜂蜜' in question_lower:
        return "蜂蜜具有抗菌、润燥、止咳的功效。含有多种维生素和矿物质，有助于增强免疫力。但糖尿病患者应适量食用，1岁以下婴儿不宜食用蜂蜜。"
    elif '柠檬' in question_lower:
        return "柠檬富含维生素C和柠檬酸，有助于增强免疫力、促进铁吸收。柠檬水有助于消化和排毒。但胃酸过多者应谨慎食用，避免空腹大量饮用。"
    elif '生姜' in question_lower:
        return "生姜具有温中散寒、止呕、化痰的功效。对于感冒初期、恶心呕吐、消化不良有一定帮助。孕妇可适量食用缓解孕吐，但不宜过量。"
    elif '大蒜' in question_lower:
        return "大蒜含有大蒜素，具有抗菌、抗病毒、降血脂的作用。有助于预防心血管疾病和某些癌症。但胃溃疡患者应避免生食大蒜，服用抗凝药物者需谨慎。"
    elif '绿茶' in question_lower:
        return "绿茶富含茶多酚和儿茶素，具有抗氧化、降血脂、防癌的功效。适量饮用有助于心血管健康。但不宜空腹饮用，失眠者应避免晚间饮用。"
    elif '核桃' in question_lower:
        return "核桃富含不饱和脂肪酸、蛋白质和维生素E，有益于大脑健康和心血管系统。适量食用可改善记忆力。但热量较高，每日建议食用2-3个即可。"
    elif '燕麦' in question_lower:
        return "燕麦富含β-葡聚糖，有助于降低胆固醇、稳定血糖。含有丰富的膳食纤维，有利于消化健康。适合糖尿病患者和减肥人群食用。"
    elif '菠菜' in question_lower:
        return "菠菜富含铁、叶酸、维生素K等营养素，有助于预防贫血、促进骨骼健康。但含有草酸，肾结石患者应适量食用，建议焯水后食用。"
    elif '胡萝卜' in question_lower:
        return "胡萝卜富含β-胡萝卜素，在体内可转化为维生素A，有益于视力健康和免疫系统。建议与油脂一起烹饪，有助于营养吸收。"
    elif '西红柿' in question_lower or '番茄' in question_lower:
        return "西红柿富含番茄红素、维生素C和叶酸，具有抗氧化、防癌的功效。熟食比生食更有利于番茄红素的吸收。对前列腺健康特别有益。"
    
    # 医学专有名词解释
    elif 'dna' in question_lower or '脱氧核糖核酸' in question_lower:
        return "DNA（脱氧核糖核酸）是携带遗传信息的生物大分子，由四种碱基（A、T、G、C）组成。它存储着生物体的遗传指令，决定了生物的性状和特征。"
    elif 'rna' in question_lower or '核糖核酸' in question_lower:
        return "RNA（核糖核酸）是参与蛋白质合成和基因表达调控的核酸分子。主要包括mRNA（信使RNA）、tRNA（转运RNA）和rRNA（核糖体RNA）等类型。"
    elif '胆固醇' in question_lower:
        return "胆固醇是人体必需的脂质分子，参与细胞膜构成和激素合成。分为HDL（好胆固醇）和LDL（坏胆固醇）。高LDL胆固醇是心血管疾病的危险因素。"
    elif '血红蛋白' in question_lower:
        return "血红蛋白是红细胞中的蛋白质，负责运输氧气和二氧化碳。正常值：男性120-160g/L，女性110-150g/L。低于正常值可能提示贫血。"
    elif '胰岛素' in question_lower:
        return "胰岛素是胰腺β细胞分泌的激素，调节血糖水平。它促进葡萄糖进入细胞，降低血糖浓度。糖尿病患者胰岛素分泌不足或作用异常。"
    elif '抗生素' in question_lower:
        return "抗生素是用于治疗细菌感染的药物，对病毒感染无效。使用时需遵医嘱，按时按量服用，不可随意停药，以免产生耐药性。"
    elif '疫苗' in question_lower:
        return "疫苗是用于预防传染病的生物制品，通过刺激免疫系统产生抗体来获得免疫力。接种疫苗是预防传染病最有效、最经济的方法。"
    elif '基因' in question_lower:
        return "基因是DNA上具有特定功能的片段，是遗传的基本单位。基因决定了生物体的性状，如身高、血型等。基因突变可能导致遗传性疾病。"
    elif '免疫力' in question_lower or '免疫系统' in question_lower:
        return "免疫系统是机体抵御外来病原体的防御系统，包括先天性免疫和获得性免疫。良好的免疫力有助于预防感染和疾病。"
    elif '新陈代谢' in question_lower:
        return "新陈代谢是机体内所有生化反应的总称，包括合成代谢和分解代谢。它维持生命活动所需的能量和物质交换，影响体重和健康状态。"
    
    else:
        return f"您询问的是关于'{question}'的问题。智慧医疗知识服务平台正在为您分析相关信息。建议您详细描述症状，以便获得更准确的建议。如有严重不适，请及时就医咨询专业医生。"

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': '智慧医疗知识服务平台',
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'success',
        'message': '智慧医疗知识服务平台API运行正常',
        'version': '1.0.0',
        'endpoints': [
            '/api/auth/login - POST - 用户登录',
            '/api/ask - POST - 医疗问答',
            '/api/health - GET - 服务状态检查',
            '/test - GET - 服务器测试'
        ]
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': '智慧医疗知识服务平台',
        'status': 'running',
        'version': '1.0.0',
        'description': '基于知识图谱的智能医疗问答服务'
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🏥 智慧医疗知识服务平台后端启动中...")
    print("=" * 60)
    print("📍 服务地址: http://localhost:5000")
    print("🔑 登录接口: http://localhost:5000/api/auth/login")
    print("💬 问答接口: http://localhost:5000/api/ask")
    print("🧪 测试接口: http://localhost:5000/test")
    print("=" * 60)
    print("👤 可用账号:")
    print("   用户名: admin, 密码: medical_admin_2024")
    print("   用户名: Savannah, 密码: password")
    print("   用户名: user, 密码: 123456")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
