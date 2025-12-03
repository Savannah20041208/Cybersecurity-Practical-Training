#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
医疗知识图谱 - 审计日志系统
记录所有用户操作，满足医疗系统合规要求
"""

import sqlite3
import datetime
import json
import os
from typing import Optional, List, Dict, Any

class AuditLogger:
    def __init__(self, db_path="medical_audit.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化审计日志数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建审计日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT
            )
        ''')
        
        # 创建索引提高查询性能
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_id ON audit_logs(user_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_logs(timestamp)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_action ON audit_logs(action)
        ''')
        
        conn.commit()
        conn.close()
    
    def log_action(self, 
                   action: str,
                   user_id: Optional[int] = None,
                   username: Optional[str] = None,
                   resource_type: Optional[str] = None,
                   resource_id: Optional[str] = None,
                   details: Optional[Dict[str, Any]] = None,
                   ip_address: Optional[str] = None,
                   user_agent: Optional[str] = None,
                   success: bool = True,
                   error_message: Optional[str] = None):
        """记录审计日志"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            details_json = json.dumps(details, ensure_ascii=False) if details else None
            
            cursor.execute('''
                INSERT INTO audit_logs 
                (user_id, username, action, resource_type, resource_id, 
                 details, ip_address, user_agent, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, action, resource_type, resource_id,
                  details_json, ip_address, user_agent, success, error_message))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"审计日志记录失败: {str(e)}")
            return False
    
    def log_medical_query(self, user_id: int, username: str, 
                         question: str, answer: str, 
                         ip_address: str = None):
        """记录医疗查询操作"""
        return self.log_action(
            action="医疗知识查询",
            user_id=user_id,
            username=username,
            resource_type="knowledge_graph",
            details={
                "question": question,
                "answer_length": len(answer),
                "has_answer": bool(answer.strip())
            },
            ip_address=ip_address
        )
    
    def log_user_login(self, username: str, ip_address: str = None, 
                      success: bool = True, error_message: str = None):
        """记录用户登录"""
        return self.log_action(
            action="用户登录",
            username=username,
            resource_type="authentication",
            ip_address=ip_address,
            success=success,
            error_message=error_message
        )
    
    def log_user_logout(self, user_id: int, username: str, ip_address: str = None):
        """记录用户登出"""
        return self.log_action(
            action="用户登出",
            user_id=user_id,
            username=username,
            resource_type="authentication",
            ip_address=ip_address
        )
    
    def log_disease_query(self, user_id: int, username: str, 
                         disease_name: str, ip_address: str = None):
        """记录疾病查询"""
        return self.log_action(
            action="疾病信息查询",
            user_id=user_id,
            username=username,
            resource_type="disease",
            resource_id=disease_name,
            ip_address=ip_address
        )
    
    def log_drug_query(self, user_id: int, username: str, 
                      drug_name: str, ip_address: str = None):
        """记录药物查询"""
        return self.log_action(
            action="药物信息查询",
            user_id=user_id,
            username=username,
            resource_type="drug",
            resource_id=drug_name,
            ip_address=ip_address
        )
    
    def log_sensitive_access(self, user_id: int, username: str,
                           sensitive_type: str, ip_address: str = None):
        """记录敏感信息访问"""
        return self.log_action(
            action="敏感信息访问",
            user_id=user_id,
            username=username,
            resource_type="sensitive_data",
            resource_id=sensitive_type,
            ip_address=ip_address,
            details={"alert_level": "high"}
        )
    
    def get_user_activity(self, user_id: int, 
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         limit: int = 100) -> List[Dict]:
        """获取用户活动记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT action, resource_type, resource_id, details, 
                       timestamp, success, error_message
                FROM audit_logs 
                WHERE user_id = ?
            '''
            params = [user_id]
            
            if start_date:
                query += ' AND timestamp >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND timestamp <= ?'
                params.append(end_date)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            activities = []
            for row in rows:
                activity = {
                    "action": row[0],
                    "resource_type": row[1],
                    "resource_id": row[2],
                    "details": json.loads(row[3]) if row[3] else None,
                    "timestamp": row[4],
                    "success": bool(row[5]),
                    "error_message": row[6]
                }
                activities.append(activity)
            
            conn.close()
            return activities
            
        except Exception as e:
            print(f"获取用户活动记录失败: {str(e)}")
            return []
    
    def get_system_stats(self, days: int = 7) -> Dict[str, Any]:
        """获取系统统计信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 计算统计时间范围
            start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
            
            # 总操作次数
            total_operations = cursor.execute('''
                SELECT COUNT(*) FROM audit_logs 
                WHERE timestamp >= ?
            ''', (start_date,)).fetchone()[0]
            
            # 活跃用户数
            active_users = cursor.execute('''
                SELECT COUNT(DISTINCT user_id) FROM audit_logs 
                WHERE timestamp >= ? AND user_id IS NOT NULL
            ''', (start_date,)).fetchone()[0]
            
            # 医疗查询次数
            medical_queries = cursor.execute('''
                SELECT COUNT(*) FROM audit_logs 
                WHERE timestamp >= ? AND action = '医疗知识查询'
            ''', (start_date,)).fetchone()[0]
            
            # 登录次数
            login_attempts = cursor.execute('''
                SELECT COUNT(*) FROM audit_logs 
                WHERE timestamp >= ? AND action = '用户登录'
            ''', (start_date,)).fetchone()[0]
            
            # 失败操作次数
            failed_operations = cursor.execute('''
                SELECT COUNT(*) FROM audit_logs 
                WHERE timestamp >= ? AND success = FALSE
            ''', (start_date,)).fetchone()[0]
            
            # 热门查询类型
            popular_actions = cursor.execute('''
                SELECT action, COUNT(*) as count FROM audit_logs 
                WHERE timestamp >= ?
                GROUP BY action 
                ORDER BY count DESC LIMIT 10
            ''', (start_date,)).fetchall()
            
            conn.close()
            
            return {
                "period_days": days,
                "total_operations": total_operations,
                "active_users": active_users,
                "medical_queries": medical_queries,
                "login_attempts": login_attempts,
                "failed_operations": failed_operations,
                "success_rate": (total_operations - failed_operations) / total_operations * 100 if total_operations > 0 else 0,
                "popular_actions": [{"action": row[0], "count": row[1]} for row in popular_actions]
            }
            
        except Exception as e:
            print(f"获取系统统计失败: {str(e)}")
            return {}
    
    def export_logs(self, output_file: str, 
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> bool:
        """导出审计日志"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM audit_logs 
                WHERE 1=1
            '''
            params = []
            
            if start_date:
                query += ' AND timestamp >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND timestamp <= ?'
                params.append(end_date)
            
            query += ' ORDER BY timestamp DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # 导出为JSON格式
            logs = []
            for row in rows:
                log_entry = {
                    "id": row[0],
                    "user_id": row[1],
                    "username": row[2],
                    "action": row[3],
                    "resource_type": row[4],
                    "resource_id": row[5],
                    "details": json.loads(row[6]) if row[6] else None,
                    "ip_address": row[7],
                    "user_agent": row[8],
                    "timestamp": row[9],
                    "success": bool(row[10]),
                    "error_message": row[11]
                }
                logs.append(log_entry)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"导出日志失败: {str(e)}")
            return False

# Flask集成辅助函数
def get_client_ip(request):
    """获取客户端IP地址"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

def get_user_agent(request):
    """获取用户代理信息"""
    return request.headers.get('User-Agent', '')
