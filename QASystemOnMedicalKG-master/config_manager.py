#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
医疗知识图谱 - 配置管理系统
管理系统配置、数据库连接、API配置等
"""

import json
import os
import shutil
import datetime
import hashlib
from typing import Dict, Any, Optional, List
from pathlib import Path

class ConfigManager:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # 配置文件路径
        self.main_config_file = self.config_dir / "main_config.json"
        self.db_config_file = self.config_dir / "database_config.json"
        self.api_config_file = self.config_dir / "api_config.json"
        self.security_config_file = self.config_dir / "security_config.json"
        
        self._init_default_configs()
    
    def _init_default_configs(self):
        """初始化默认配置"""
        # 主配置
        if not self.main_config_file.exists():
            main_config = {
                "app_name": "医疗知识图谱问答系统",
                "version": "1.0.0",
                "debug": False,
                "host": "localhost",
                "port": 5000,
                "timezone": "Asia/Shanghai",
                "log_level": "INFO",
                "max_query_length": 500,
                "session_timeout": 3600,
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat()
            }
            self._save_config(self.main_config_file, main_config)
        
        # 数据库配置
        if not self.db_config_file.exists():
            db_config = {
                "neo4j": {
                    "uri": "bolt://localhost:7687",
                    "username": "neo4j",
                    "password": "password",
                    "database": "medical_kg",
                    "max_connection_pool_size": 50,
                    "connection_timeout": 30,
                    "max_transaction_retry_time": 30
                },
                "sqlite": {
                    "auth_db": "medical_users.db",
                    "audit_db": "medical_audit.db",
                    "cache_db": "medical_cache.db"
                },
                "redis": {
                    "host": "localhost",
                    "port": 6379,
                    "db": 0,
                    "password": None,
                    "socket_timeout": 5,
                    "connection_pool_max_connections": 10
                }
            }
            self._save_config(self.db_config_file, db_config)
        
        # API配置
        if not self.api_config_file.exists():
            api_config = {
                "rate_limiting": {
                    "enabled": True,
                    "requests_per_minute": 60,
                    "burst_limit": 10
                },
                "cors": {
                    "enabled": True,
                    "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
                    "methods": ["GET", "POST", "PUT", "DELETE"],
                    "allow_headers": ["Content-Type", "Authorization"]
                },
                "websocket": {
                    "enabled": True,
                    "port": 8765,
                    "max_connections": 100,
                    "ping_interval": 20,
                    "ping_timeout": 10
                },
                "external_apis": {
                    "drug_database": {
                        "url": "https://api.drugbank.com",
                        "api_key": "",
                        "timeout": 30,
                        "retry_attempts": 3
                    },
                    "medical_dictionary": {
                        "url": "https://api.medlineplus.gov",
                        "timeout": 15,
                        "retry_attempts": 2
                    }
                }
            }
            self._save_config(self.api_config_file, api_config)
        
        # 安全配置
        if not self.security_config_file.exists():
            security_config = {
                "jwt": {
                    "secret_key": self._generate_secret_key(),
                    "algorithm": "HS256",
                    "expiration_hours": 24,
                    "refresh_token_expiration_days": 7
                },
                "encryption": {
                    "algorithm": "AES-256-CBC",
                    "key_derivation": "PBKDF2",
                    "iterations": 100000,
                    "salt_length": 32
                },
                "password_policy": {
                    "min_length": 8,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_numbers": True,
                    "require_special_chars": True,
                    "max_age_days": 90
                },
                "audit": {
                    "log_all_queries": True,
                    "log_sensitive_access": True,
                    "log_failed_attempts": True,
                    "retention_days": 365
                },
                "sensitive_detection": {
                    "enabled": True,
                    "mask_in_logs": True,
                    "alert_on_critical": True
                }
            }
            self._save_config(self.security_config_file, security_config)
    
    def _generate_secret_key(self) -> str:
        """生成安全密钥"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _save_config(self, file_path: Path, config: Dict[str, Any]):
        """保存配置到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败 {file_path}: {str(e)}")
            return False
    
    def _load_config(self, file_path: Path) -> Dict[str, Any]:
        """从文件加载配置"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"加载配置失败 {file_path}: {str(e)}")
            return {}
    
    def get_config(self, config_type: str) -> Dict[str, Any]:
        """获取指定类型的配置"""
        config_files = {
            "main": self.main_config_file,
            "database": self.db_config_file,
            "api": self.api_config_file,
            "security": self.security_config_file
        }
        
        if config_type in config_files:
            return self._load_config(config_files[config_type])
        else:
            raise ValueError(f"未知的配置类型: {config_type}")
    
    def update_config(self, config_type: str, updates: Dict[str, Any]) -> bool:
        """更新配置"""
        try:
            # 创建备份
            self.backup_config(config_type)
            
            current_config = self.get_config(config_type)
            
            # 深度合并配置
            merged_config = self._deep_merge(current_config, updates)
            merged_config["updated_at"] = datetime.datetime.now().isoformat()
            
            config_files = {
                "main": self.main_config_file,
                "database": self.db_config_file,
                "api": self.api_config_file,
                "security": self.security_config_file
            }
            
            return self._save_config(config_files[config_type], merged_config)
            
        except Exception as e:
            print(f"更新配置失败: {str(e)}")
            return False
    
    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并字典"""
        result = base.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def backup_config(self, config_type: str) -> str:
        """备份配置文件"""
        try:
            config_files = {
                "main": self.main_config_file,
                "database": self.db_config_file,
                "api": self.api_config_file,
                "security": self.security_config_file
            }
            
            if config_type in config_files:
                source_file = config_files[config_type]
                if source_file.exists():
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_file = self.backup_dir / f"{config_type}_config_{timestamp}.json"
                    shutil.copy2(source_file, backup_file)
                    return str(backup_file)
            
            return ""
            
        except Exception as e:
            print(f"备份配置失败: {str(e)}")
            return ""
    
    def restore_config(self, config_type: str, backup_file: str) -> bool:
        """从备份恢复配置"""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                return False
            
            config_files = {
                "main": self.main_config_file,
                "database": self.db_config_file,
                "api": self.api_config_file,
                "security": self.security_config_file
            }
            
            if config_type in config_files:
                target_file = config_files[config_type]
                shutil.copy2(backup_path, target_file)
                return True
            
            return False
            
        except Exception as e:
            print(f"恢复配置失败: {str(e)}")
            return False
    
    def list_backups(self, config_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出备份文件"""
        backups = []
        
        try:
            pattern = f"{config_type}_config_*.json" if config_type else "*_config_*.json"
            backup_files = list(self.backup_dir.glob(pattern))
            
            for backup_file in backup_files:
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "full_path": str(backup_file),
                    "config_type": backup_file.name.split('_config_')[0],
                    "timestamp": backup_file.name.split('_config_')[1].replace('.json', ''),
                    "size": stat.st_size,
                    "created_at": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
            
            # 按创建时间排序
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            print(f"列出备份失败: {str(e)}")
        
        return backups
    
    def validate_config(self, config_type: str) -> Dict[str, Any]:
        """验证配置有效性"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            config = self.get_config(config_type)
            
            if config_type == "main":
                # 验证主配置
                required_fields = ["app_name", "version", "host", "port"]
                for field in required_fields:
                    if field not in config:
                        validation_result["errors"].append(f"缺少必需字段: {field}")
                
                if "port" in config and not (1 <= config["port"] <= 65535):
                    validation_result["errors"].append("端口号必须在1-65535范围内")
            
            elif config_type == "database":
                # 验证数据库配置
                if "neo4j" in config:
                    neo4j_config = config["neo4j"]
                    if not neo4j_config.get("uri"):
                        validation_result["errors"].append("Neo4j URI不能为空")
                    if not neo4j_config.get("username"):
                        validation_result["errors"].append("Neo4j用户名不能为空")
            
            elif config_type == "security":
                # 验证安全配置
                if "jwt" in config:
                    jwt_config = config["jwt"]
                    if not jwt_config.get("secret_key"):
                        validation_result["errors"].append("JWT密钥不能为空")
                    elif len(jwt_config["secret_key"]) < 32:
                        validation_result["warnings"].append("JWT密钥长度建议至少32字符")
            
            if validation_result["errors"]:
                validation_result["valid"] = False
        
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"配置验证失败: {str(e)}")
        
        return validation_result
    
    def export_config(self, output_file: str, config_types: Optional[List[str]] = None) -> bool:
        """导出配置"""
        try:
            all_configs = {}
            types_to_export = config_types or ["main", "database", "api", "security"]
            
            for config_type in types_to_export:
                all_configs[config_type] = self.get_config(config_type)
            
            export_data = {
                "export_timestamp": datetime.datetime.now().isoformat(),
                "export_version": "1.0",
                "configs": all_configs
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"导出配置失败: {str(e)}")
            return False
    
    def import_config(self, import_file: str, config_types: Optional[List[str]] = None) -> bool:
        """导入配置"""
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if "configs" not in import_data:
                return False
            
            configs = import_data["configs"]
            types_to_import = config_types or list(configs.keys())
            
            for config_type in types_to_import:
                if config_type in configs:
                    self.update_config(config_type, configs[config_type])
            
            return True
            
        except Exception as e:
            print(f"导入配置失败: {str(e)}")
            return False
    
    def get_config_hash(self, config_type: str) -> str:
        """获取配置文件哈希值，用于检测配置变化"""
        try:
            config = self.get_config(config_type)
            config_str = json.dumps(config, sort_keys=True)
            return hashlib.md5(config_str.encode()).hexdigest()
        except Exception:
            return ""

# 使用示例
def demo():
    """演示配置管理功能"""
    config_manager = ConfigManager()
    
    # 获取配置
    main_config = config_manager.get_config("main")
    print("主配置:", json.dumps(main_config, ensure_ascii=False, indent=2))
    
    # 更新配置
    updates = {
        "debug": True,
        "port": 5001,
        "new_feature": {
            "enabled": True,
            "settings": {"option1": "value1"}
        }
    }
    
    if config_manager.update_config("main", updates):
        print("配置更新成功")
    
    # 验证配置
    validation = config_manager.validate_config("main")
    print("配置验证结果:", validation)
    
    # 列出备份
    backups = config_manager.list_backups("main")
    print("备份列表:", backups)

if __name__ == "__main__":
    demo()
