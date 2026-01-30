#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
医疗知识图谱 - 用户认证授权管理系统
基于PHP代码逻辑转换为Python Flask版本
"""

import hashlib
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
import sqlite3
import os

class AuthManager:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "medical_users.db")
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化用户数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                permissions TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # 创建默认管理员账户
        admin_exists = cursor.execute(
            "SELECT COUNT(*) FROM users WHERE username = 'admin'"
        ).fetchone()[0]
        
        if admin_exists == 0:
            admin_password = self.hash_password('medical_admin_2024')
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, permissions)
                VALUES (?, ?, ?, ?)
            ''', ('admin', admin_password, 'admin', 'all'))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """密码哈希处理"""
        return hashlib.sha256((password + "medical_kg_salt").encode()).hexdigest()
    
    def register_user(self, username, password, role='user'):
        """用户注册"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查用户名是否已存在
            existing = cursor.execute(
                "SELECT COUNT(*) FROM users WHERE username = ?", (username,)
            ).fetchone()[0]
            
            if existing > 0:
                return {"success": False, "message": "用户名已存在"}
            
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            ''', (username, password_hash, role))
            
            conn.commit()
            conn.close()
            return {"success": True, "message": "注册成功"}
            
        except Exception as e:
            return {"success": False, "message": f"注册失败: {str(e)}"}
    
    def login_user(self, username, password):
        """用户登录验证"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            user = cursor.execute('''
                SELECT id, username, role, permissions FROM users 
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash)).fetchone()
            
            if user:
                # 更新最后登录时间
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP 
                    WHERE username = ?
                ''', (username,))
                conn.commit()
                
                # 生成JWT token
                token = self.generate_token({
                    'user_id': user[0],
                    'username': user[1],
                    'role': user[2],
                    'permissions': user[3]
                })
                
                conn.close()
                return {
                    "success": True, 
                    "token": token,
                    "user": {
                        "id": user[0],
                        "username": user[1],
                        "role": user[2]
                    }
                }
            else:
                conn.close()
                return {"success": False, "message": "用户名或密码错误"}
                
        except Exception as e:
            return {"success": False, "message": f"登录失败: {str(e)}"}
    
    def generate_token(self, payload):
        """生成JWT令牌"""
        payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        return jwt.encode(payload, "medical_kg_secret_key", algorithm='HS256')

    def validate_token(self, token: str):
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, "medical_kg_secret_key", algorithms=['HS256'])
            return {
                "success": True,
                "data": {
                    "user_id": payload.get('user_id'),
                    "username": payload.get('username'),
                    "role": payload.get('role'),
                    "permissions": payload.get('permissions')
                }
            }
        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "令牌已过期"}
        except jwt.InvalidTokenError:
            return {"success": False, "message": "无效令牌"}
        except Exception as e:
            return {"success": False, "message": f"令牌验证失败: {str(e)}"}
    
    def verify_token(self, token: str):
        """验证令牌的别名方法，保持兼容性"""
        return self.validate_token(token)

    def check_permission(self, user_id, required_permission):
        """检查用户权限"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            user = cursor.execute('''
                SELECT role, permissions FROM users WHERE id = ?
            ''', (user_id,)).fetchone()
            
            conn.close()
            
            if not user:
                return False
            
            role, permissions = user
            
            # 管理员拥有所有权限
            if role == 'admin':
                return True
            
            # 检查特定权限
            if permissions and required_permission in permissions.split(','):
                return True
                
            return False
            
        except Exception:
            return False

# Flask装饰器
def require_auth(f):
    """需要认证的装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            demo_mode = (request.headers.get('X-Demo-Mode') or '').lower() == 'true'
            if demo_mode and request.remote_addr in ('127.0.0.1', '::1'):
                request.current_user = {
                    'user_id': 0,
                    'username': 'demo_user',
                    'role': 'user',
                    'permissions': ''
                }
                return f(*args, **kwargs)
            return jsonify({"error": "缺少认证令牌"}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]  # 移除 'Bearer ' 前缀
        
        auth_manager = AuthManager()
        result = auth_manager.verify_token(token)
        
        if not result["success"]:
            return jsonify({"error": result["message"]}), 401
        
        request.current_user = result["data"]
        return f(*args, **kwargs)
    
    return decorated

def require_permission(permission):
    """需要特定权限的装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({"error": "未认证"}), 401
            
            auth_manager = AuthManager()
            user_id = request.current_user.get('user_id')
            
            if not auth_manager.check_permission(user_id, permission):
                return jsonify({"error": "权限不足"}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator
