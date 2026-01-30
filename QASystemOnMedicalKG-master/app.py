from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import subprocess
import sys  # 新增：用于获取当前Python解释器路径
import datetime
import os

# 导入自定义模块
from auth_manager import AuthManager, require_auth, require_permission
from audit_logger import AuditLogger, get_client_ip, get_user_agent
from sensitive_detector import SensitiveDetector
from config_manager import ConfigManager
from drug_lookup import DrugLookup

app = Flask(__name__)

# 初始化管理器
config_manager = ConfigManager()
auth_manager = AuthManager()
audit_logger = AuditLogger()
sensitive_detector = SensitiveDetector()
drug_lookup = DrugLookup()

# 从配置管理器获取配置
main_config = config_manager.get_config("main")
api_config = config_manager.get_config("api")
security_config = config_manager.get_config("security")

# 配置CORS
if api_config.get("cors", {}).get("enabled", True):
    cors_config = api_config["cors"]
    CORS(app, 
         origins=cors_config.get("origins", ["*"]),
         methods=cors_config.get("methods", ["GET", "POST"]),
         allow_headers=cors_config.get("allow_headers", ["Content-Type", "Authorization"]))
else:
    CORS(app)  # 默认CORS配置


# 调用外部 Python 脚本并获取输出
def get_answer_from_script(question):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_dir, 'chatbot_graph.py')
        # 优化：使用当前Python解释器路径，避免环境不一致问题
        result = subprocess.run(
            [sys.executable, script_path, question],
            text=True,
            capture_output=True,
            check=True,
            cwd=base_dir,
            timeout=120  # 新增：设置超时，防止脚本无响应
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        detail = (e.stderr or '').strip()
        if not detail:
            detail = (e.stdout or '').strip()
        if not detail:
            detail = str(e)
        return f"执行脚本错误：{detail}"
    except subprocess.TimeoutExpired:
        return "脚本执行超时，请稍后再试"
    except Exception as e:
        return f"发生错误：{str(e)}"


@app.route('/ask', methods=['POST'])
@require_auth
def ask():
    data = request.get_json()
    question = data.get('question', '').strip()  # 新增：去除首尾空格
    
    # 获取用户信息
    user_id = request.current_user.get('user_id')
    username = request.current_user.get('username')
    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)

    if not question:
        # 记录错误请求
        audit_logger.log_action(
            action="无效医疗查询请求",
            user_id=user_id,
            username=username,
            ip_address=client_ip,
            success=False,
            error_message="问题内容为空"
        )
        return jsonify({'error': '请提供问题'}), 400
    
    # 检查问题长度
    max_length = main_config.get('max_query_length', 500)
    if len(question) > max_length:
        audit_logger.log_action(
            action="医疗查询请求被拒绝",
            user_id=user_id,
            username=username,
            ip_address=client_ip,
            success=False,
            error_message=f"问题长度超过限制({max_length}字符)"
        )
        return jsonify({'error': f'问题长度不能超过{max_length}字符'}), 400
    
    # 敏感信息检测
    sensitive_detections = sensitive_detector.detect_sensitive_info(question)
    if sensitive_detections:
        risk_summary = sensitive_detector.get_risk_summary(sensitive_detections)
        
        # 记录敏感信息访问
        audit_logger.log_sensitive_access(
            user_id=user_id,
            username=username,
            sensitive_type=f"查询包含{len(sensitive_detections)}项敏感信息",
            ip_address=client_ip
        )
        
        # 如果包含极高风险敏感信息，拒绝处理
        if risk_summary['risk_level'] == 'critical':
            return jsonify({
                'error': '查询包含敏感信息，已被系统拒绝',
                'risk_level': 'critical'
            }), 403
        
        # 对问题进行脱敏处理
        masked_question, _ = sensitive_detector.mask_sensitive_info(question)
        # 在日志中使用脱敏后的问题
        log_question = masked_question
    else:
        log_question = question

    try:
        # 获取答案
        answer = get_answer_from_script(question)
        
        # 检测答案中的敏感信息
        answer_detections = sensitive_detector.detect_sensitive_info(answer)
        if answer_detections:
            # 对答案进行脱敏处理
            answer, _ = sensitive_detector.mask_sensitive_info(answer)
        
        # 记录成功的医疗查询
        audit_logger.log_medical_query(
            user_id=user_id,
            username=username,
            question=log_question,
            answer=answer,
            ip_address=client_ip
        )
        
        return jsonify({
            'answer': answer,
            'has_sensitive_info': len(sensitive_detections) > 0 or len(answer_detections) > 0
        })
        
    except Exception as e:
        # 记录错误
        audit_logger.log_action(
            action="医疗查询处理失败",
            user_id=user_id,
            username=username,
            ip_address=client_ip,
            success=False,
            error_message=str(e)
        )
        return jsonify({'error': '系统处理异常，请稍后重试'}), 500


# 新增：恢复/test路由，用于网页测试
@app.route('/test', methods=['GET'])
def test_page():
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>问答测试</title>
        <style>
            .container { max-width: 800px; margin: 20px auto; padding: 20px; }
            #question { width: 100%; padding: 10px; font-size: 16px; }
            #submit { margin-top: 10px; padding: 10px 20px; font-size: 16px; }
            #answer { margin-top: 20px; padding: 15px; border: 1px solid #ccc; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>医疗问答测试</h1>
            <input type="text" id="question" placeholder="请输入问题...">
            <button id="submit">提交</button>
            <div id="answer"></div>
        </div>
        <script>
            document.getElementById('submit').addEventListener('click', async () => {
                const question = document.getElementById('question').value.trim();
                const answerDiv = document.getElementById('answer');
                if (!question) {
                    answerDiv.textContent = '请输入问题内容';
                    return;
                }
                try {
                    const res = await fetch('/ask', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question })
                    });
                    const data = await res.json();
                    answerDiv.textContent = data.answer || '未获取到答案';
                } catch (err) {
                    answerDiv.textContent = '请求失败：' + err.message;
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(test_html)


# 认证API路由
@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    client_ip = get_client_ip(request)
    
    if not username or not password:
        audit_logger.log_action(
            action="用户注册失败",
            username=username,
            ip_address=client_ip,
            success=False,
            error_message="用户名或密码为空"
        )
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    # 密码强度检查
    password_policy = security_config.get('password_policy', {})
    if len(password) < password_policy.get('min_length', 8):
        return jsonify({'error': f'密码长度至少{password_policy.get("min_length", 8)}位'}), 400
    
    # 尝试注册
    result = auth_manager.register_user(username, password)
    
    # 记录注册尝试
    audit_logger.log_action(
        action="用户注册",
        username=username,
        ip_address=client_ip,
        success=result['success'],
        error_message=None if result['success'] else result['message']
    )
    
    if result['success']:
        return jsonify({'message': '注册成功'}), 201
    else:
        return jsonify({'error': result['message']}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    client_ip = get_client_ip(request)
    
    if not username or not password:
        audit_logger.log_user_login(
            username=username,
            ip_address=client_ip,
            success=False,
            error_message="用户名或密码为空"
        )
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    # 尝试登录
    result = auth_manager.login_user(username, password)
    
    # 记录登录尝试
    audit_logger.log_user_login(
        username=username,
        ip_address=client_ip,
        success=result['success'],
        error_message=None if result['success'] else result['message']
    )
    
    if result['success']:
        return jsonify({
            'message': '登录成功',
            'token': result['token'],
            'user': result['user']
        })
    else:
        return jsonify({'error': result['message']}), 401

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """用户登出"""
    user_id = request.current_user.get('user_id')
    username = request.current_user.get('username')
    client_ip = get_client_ip(request)
    
    # 记录登出
    audit_logger.log_user_logout(
        user_id=user_id,
        username=username,
        ip_address=client_ip
    )
    
    return jsonify({'message': '登出成功'})

@app.route('/api/auth/profile', methods=['GET'])
@require_auth
def get_profile():
    """获取用户信息"""
    return jsonify({
        'user': {
            'id': request.current_user.get('user_id'),
            'username': request.current_user.get('username'),
            'role': request.current_user.get('role')
        }
    })

# 管理员API路由
@app.route('/api/admin/stats', methods=['GET'])
@require_auth
@require_permission('admin')
def get_system_stats():
    """获取系统统计信息"""
    days = request.args.get('days', 7, type=int)
    stats = audit_logger.get_system_stats(days)
    return jsonify({'stats': stats})

@app.route('/api/admin/user-activity/<int:user_id>', methods=['GET'])
@require_auth
@require_permission('admin')
def get_user_activity(user_id):
    """获取用户活动记录"""
    limit = request.args.get('limit', 100, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    activities = audit_logger.get_user_activity(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    
    return jsonify({'activities': activities})

@app.route('/api/admin/export-logs', methods=['POST'])
@require_auth
@require_permission('admin')
def export_audit_logs():
    """导出审计日志"""
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"audit_logs_{timestamp}.json"
    
    if audit_logger.export_logs(filename, start_date, end_date):
        return jsonify({
            'message': '日志导出成功',
            'filename': filename
        })
    else:
        return jsonify({'error': '日志导出失败'}), 500

# 配置管理API
@app.route('/api/admin/config/<config_type>', methods=['GET'])
@require_auth
@require_permission('admin')
def get_config_endpoint(config_type):
    """获取配置"""
    try:
        config = config_manager.get_config(config_type)
        return jsonify({'config': config})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/admin/config/<config_type>', methods=['PUT'])
@require_auth
@require_permission('admin')
def update_config_endpoint(config_type):
    """更新配置"""
    data = request.get_json()
    updates = data.get('updates', {})
    
    if config_manager.update_config(config_type, updates):
        # 记录配置更新
        audit_logger.log_action(
            action=f"更新{config_type}配置",
            user_id=request.current_user.get('user_id'),
            username=request.current_user.get('username'),
            resource_type="config",
            resource_id=config_type,
            ip_address=get_client_ip(request)
        )
        return jsonify({'message': '配置更新成功'})
    else:
        return jsonify({'error': '配置更新失败'}), 500

# 敏感信息检测API
@app.route('/api/admin/check-sensitive', methods=['POST'])
@require_auth
@require_permission('admin')
def check_sensitive():
    """检测敏感信息"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': '请提供待检测文本'}), 400
    
    detections = sensitive_detector.detect_sensitive_info(text)
    risk_summary = sensitive_detector.get_risk_summary(detections)
    masked_text, _ = sensitive_detector.mask_sensitive_info(text)
    
    return jsonify({
        'detections': detections,
        'risk_summary': risk_summary,
        'masked_text': masked_text
    })

# 配置验证API
@app.route('/api/admin/validate-config', methods=['POST'])
@require_auth
@require_permission('admin')
def validate_config_endpoint():
    """验证配置"""
    data = request.get_json()
    config_type = data.get('config_type')
    config_data = data.get('config_data')
    
    if not config_type or not config_data:
        return jsonify({'error': '缺少配置类型或配置数据'}), 400
    
    try:
        # 临时保存当前配置进行验证
        temp_config_manager = ConfigManager()
        validation_result = temp_config_manager.validate_config(config_type)
        
        return jsonify({'validation_result': validation_result})
    except Exception as e:
        return jsonify({'error': f'验证失败: {str(e)}'}), 500

# 备份配置API
@app.route('/api/admin/backup-config', methods=['POST'])
@require_auth
@require_permission('admin')
def backup_config_endpoint():
    """创建配置备份"""
    data = request.get_json()
    config_type = data.get('config_type')
    
    if not config_type:
        return jsonify({'error': '缺少配置类型'}), 400
    
    try:
        backup_file = config_manager.backup_config(config_type)
        if backup_file:
            audit_logger.log_action(
                action=f"创建{config_type}配置备份",
                user_id=request.current_user.get('user_id'),
                username=request.current_user.get('username'),
                resource_type="config_backup",
                resource_id=backup_file,
                ip_address=get_client_ip(request)
            )
            return jsonify({'message': '备份创建成功', 'backup_file': backup_file})
        else:
            return jsonify({'error': '备份创建失败'}), 500
    except Exception as e:
        return jsonify({'error': f'备份失败: {str(e)}'}), 500

# 恢复配置API
@app.route('/api/admin/restore-config', methods=['POST'])
@require_auth
@require_permission('admin')
def restore_config_endpoint():
    """恢复配置备份"""
    data = request.get_json()
    config_type = data.get('config_type')
    backup_filename = data.get('backup_filename')
    
    if not config_type or not backup_filename:
        return jsonify({'error': '缺少配置类型或备份文件名'}), 400
    
    try:
        success = config_manager.restore_config(config_type, backup_filename)
        if success:
            audit_logger.log_action(
                action=f"恢复{config_type}配置",
                user_id=request.current_user.get('user_id'),
                username=request.current_user.get('username'),
                resource_type="config_restore",
                resource_id=backup_filename,
                ip_address=get_client_ip(request)
            )
            return jsonify({'message': '配置恢复成功'})
        else:
            return jsonify({'error': '配置恢复失败'}), 500
    except Exception as e:
        return jsonify({'error': f'恢复失败: {str(e)}'}), 500

# 列出备份API
@app.route('/api/admin/list-backups', methods=['GET'])
@require_auth
@require_permission('admin')
def list_backups_endpoint():
    """列出配置备份"""
    config_type = request.args.get('config_type')
    
    try:
        backups = config_manager.list_backups(config_type)
        return jsonify({'backups': backups})
    except Exception as e:
        return jsonify({'error': f'获取备份列表失败: {str(e)}'}), 500

# 导出配置API
@app.route('/api/admin/export-config', methods=['POST'])
@require_auth
@require_permission('admin')
def export_config_endpoint():
    """导出配置"""
    data = request.get_json()
    config_types = data.get('config_types')
    
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        export_filename = f"config_export_{timestamp}.json"
        
        success = config_manager.export_config(export_filename, config_types)
        if success:
            audit_logger.log_action(
                action="导出系统配置",
                user_id=request.current_user.get('user_id'),
                username=request.current_user.get('username'),
                resource_type="config_export",
                resource_id=export_filename,
                ip_address=get_client_ip(request)
            )
            
            # 返回文件内容
            try:
                with open(export_filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                response = app.response_class(
                    response=content,
                    status=200,
                    mimetype='application/json',
                    headers={'Content-Disposition': f'attachment; filename={export_filename}'}
                )
                
                # 删除临时文件
                import os
                os.remove(export_filename)
                
                return response
            except Exception as e:
                return jsonify({'error': f'读取导出文件失败: {str(e)}'}), 500
        else:
            return jsonify({'error': '配置导出失败'}), 500
    except Exception as e:
        return jsonify({'error': f'导出失败: {str(e)}'}), 500

# 导入配置API
@app.route('/api/admin/import-config', methods=['POST'])
@require_auth
@require_permission('admin')
def import_config_endpoint():
    """导入配置"""
    if 'config_file' not in request.files:
        return jsonify({'error': '未找到配置文件'}), 400
    
    file = request.files['config_file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    config_types = request.form.get('config_types')
    if config_types:
        try:
            config_types = json.loads(config_types)
        except:
            config_types = None
    
    try:
        # 保存临时文件
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.json', delete=False) as temp_file:
            file.save(temp_file.name)
            temp_filename = temp_file.name
        
        # 导入配置
        success = config_manager.import_config(temp_filename, config_types)
        
        # 删除临时文件
        os.unlink(temp_filename)
        
        if success:
            audit_logger.log_action(
                action="导入系统配置",
                user_id=request.current_user.get('user_id'),
                username=request.current_user.get('username'),
                resource_type="config_import",
                resource_id=file.filename,
                ip_address=get_client_ip(request)
            )
            return jsonify({'message': '配置导入成功'})
        else:
            return jsonify({'error': '配置导入失败'}), 500
    except Exception as e:
        return jsonify({'error': f'导入失败: {str(e)}'}), 500

# 重置配置API
@app.route('/api/admin/reset-config', methods=['POST'])
@require_auth
@require_permission('admin')
def reset_config_endpoint():
    """重置配置为默认值"""
    data = request.get_json()
    config_type = data.get('config_type')
    
    if not config_type:
        return jsonify({'error': '缺少配置类型'}), 400
    
    try:
        # 先备份当前配置
        config_manager.backup_config(config_type)
        
        # 重置配置（通过删除配置文件让系统重新创建默认配置）
        config_files = {
            "main": config_manager.main_config_file,
            "database": config_manager.db_config_file,
            "api": config_manager.api_config_file,
            "security": config_manager.security_config_file
        }
        
        if config_type in config_files:
            config_file = config_files[config_type]
            if config_file.exists():
                config_file.unlink()
            
            # 重新初始化默认配置
            config_manager._init_default_configs()
            
            audit_logger.log_action(
                action=f"重置{config_type}配置为默认值",
                user_id=request.current_user.get('user_id'),
                username=request.current_user.get('username'),
                resource_type="config_reset",
                resource_id=config_type,
                ip_address=get_client_ip(request)
            )
            
            return jsonify({'message': '配置重置成功'})
        else:
            return jsonify({'error': '无效的配置类型'}), 400
    except Exception as e:
        return jsonify({'error': f'重置失败: {str(e)}'}), 500

# 获取配置哈希API
@app.route('/api/admin/config-hash/<config_type>', methods=['GET'])
@require_auth
@require_permission('admin')
def get_config_hash_endpoint(config_type):
    """获取配置哈希值"""
    try:
        hash_value = config_manager.get_config_hash(config_type)
        return jsonify({'hash': hash_value})
    except Exception as e:
        return jsonify({'error': f'获取配置哈希失败: {str(e)}'}), 500

# 新增：处理根路径访问，提供API文档
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': '医疗知识图谱问答系统API',
        'version': main_config.get('version', '1.0.0'),
        'endpoints': {
            'auth': {
                'register': 'POST /api/auth/register',
                'login': 'POST /api/auth/login',
                'logout': 'POST /api/auth/logout',
                'profile': 'GET /api/auth/profile'
            },
            'main': {
                'ask': 'POST /ask (需要认证)',
                'test_page': 'GET /test'
            },
            'admin': {
                'stats': 'GET /api/admin/stats',
                'user_activity': 'GET /api/admin/user-activity/<user_id>',
                'export_logs': 'POST /api/admin/export-logs',
                'config': 'GET/PUT /api/admin/config/<type>',
                'check_sensitive': 'POST /api/admin/check-sensitive'
            }
        }
    })

# ============ 药品补全接口（用于拍药盒识别） ============
@app.route('/api/drug/lookup', methods=['POST'])
@require_auth
def drug_lookup_api():
    """
    药品补全查询接口
    请求体:
    {
        "query": "国药准字H20000001" 或 "阿莫西林",
        "enterprise": "某某制药有限公司"  // 可选，提高匹配精度
    }
    返回:
    {
        "match_type": "approval_no" | "name_enterprise" | "fuzzy" | "none",
        "drug": {...},           // 精确匹配时返回完整药品信息
        "candidates": [...],     // 模糊匹配时返回候选列表
        "query": "原始查询"
    }
    """
    try:
        data = request.get_json() or {}
        query = (data.get('query') or '').strip()
        enterprise = (data.get('enterprise') or '').strip() or None

        if not query:
            return jsonify({'error': '请提供查询内容（批准文号或药品名称）'}), 400

        result = drug_lookup.lookup(query, enterprise)

        # 审计日志
        audit_logger.log(
            user_id=request.current_user.get('user_id'),
            action='drug_lookup',
            details={
                'query': query,
                'enterprise': enterprise,
                'match_type': result.get('match_type'),
                'found': result.get('drug') is not None or bool(result.get('candidates'))
            },
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'药品查询失败: {str(e)}'}), 500


@app.route('/api/drug/lookup', methods=['GET'])
def drug_lookup_get():
    """GET 方式的药品查询（无需认证，用于快速测试）"""
    query = request.args.get('q') or request.args.get('query') or ''
    enterprise = request.args.get('enterprise') or None

    if not query.strip():
        return jsonify({'error': '请提供查询参数 ?q=药品名或批准文号'}), 400

    result = drug_lookup.lookup(query.strip(), enterprise)
    return jsonify(result)


# 错误处理
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': '未授权访问，请先登录'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': '权限不足'}), 403

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    # 使用配置管理器的配置
    host = main_config.get('host', '0.0.0.0')
    port = main_config.get('port', 5000)
    debug = main_config.get('debug', False)
    
    print(f"🏥 医疗知识图谱问答系统启动中...")
    print(f"📍 地址: http://{host}:{port}")
    print(f"🔍 调试模式: {'开启' if debug else '关闭'}")
    print(f"🔐 认证系统: 已启用")
    print(f"📊 审计日志: 已启用")
    print(f"🛡️ 敏感信息检测: 已启用")
    print(f"⚙️ 配置管理: 已启用")
    
    app.run(host=host, port=port, debug=debug)
