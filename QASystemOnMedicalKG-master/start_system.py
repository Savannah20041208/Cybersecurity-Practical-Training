#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
医疗知识图谱问答系统 - 启动脚本
同时启动Flask API服务器和WebSocket服务器
"""

import asyncio
import subprocess
import sys
import time
import threading
import signal
import os
from config_manager import ConfigManager

class SystemLauncher:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_manager = ConfigManager()
        self.main_config = self.config_manager.get_config("main")
        self.api_config = self.config_manager.get_config("api")
        
        self.flask_process = None
        self.websocket_process = None
        self.running = True
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """信号处理函数"""
        print(f"\n收到信号 {signum}，正在优雅关闭系统...")
        self.running = False
        self.stop_services()
    
    def start_flask_server(self):
        """启动Flask API服务器"""
        try:
            print("🚀 启动Flask API服务器...")
            self.flask_process = subprocess.Popen([
                sys.executable, os.path.join(self.base_dir, 'app.py')
            ], cwd=self.base_dir)
            
            print("✅ Flask API服务器已启动")
            return True
        except Exception as e:
            print(f"❌ Flask服务器启动失败: {str(e)}")
            return False
    
    def start_websocket_server(self):
        """启动WebSocket服务器"""
        try:
            print("🔌 启动WebSocket服务器...")
            self.websocket_process = subprocess.Popen([
                sys.executable, os.path.join(self.base_dir, 'websocket_server.py')
            ], cwd=self.base_dir)
            
            print("✅ WebSocket服务器已启动")
            return True
        except Exception as e:
            print(f"❌ WebSocket服务器启动失败: {str(e)}")
            return False
    
    def check_dependencies(self):
        """检查依赖"""
        required_modules = [
            'flask', 'flask_cors', 'jwt', 'websockets', 'neo4j'
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module if module != 'flask_cors' else 'flask_cors')
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            print("❌ 缺少以下依赖模块:")
            for module in missing_modules:
                print(f"   - {module}")
            print("\n请运行以下命令安装:")
            print(f"pip install {' '.join(missing_modules)}")
            return False
        
        print("✅ 依赖检查通过")
        return True
    
    def check_files(self):
        """检查必要文件"""
        required_files = [
            'app.py', 'websocket_server.py', 'chatbot_graph.py',
            'auth_manager.py', 'audit_logger.py', 
            'sensitive_detector.py', 'config_manager.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(os.path.join(self.base_dir, file)):
                missing_files.append(file)
        
        if missing_files:
            print("❌ 缺少以下文件:")
            for file in missing_files:
                print(f"   - {file}")
            return False
        
        print("✅ 文件检查通过")
        return True
    
    def show_system_info(self):
        """显示系统信息"""
        print("\n" + "="*60)
        print("🏥 医疗知识图谱问答系统")
        print("="*60)
        
        # API服务信息
        host = self.main_config.get('host', 'localhost')
        port = self.main_config.get('port', 5000)
        print(f"📡 API服务器: http://{host}:{port}")
        print(f"   - 问答接口: POST http://{host}:{port}/ask")
        print(f"   - 测试页面: http://{host}:{port}/test")
        print(f"   - 用户注册: POST http://{host}:{port}/api/auth/register")
        print(f"   - 用户登录: POST http://{host}:{port}/api/auth/login")
        
        # WebSocket服务信息
        ws_config = self.api_config.get('websocket', {})
        ws_port = ws_config.get('port', 8765)
        print(f"🔌 WebSocket服务器: ws://{host}:{ws_port}")
        
        # 默认管理员账户信息
        print(f"\n🔐 默认管理员账户:")
        print(f"   - 用户名: admin")
        print(f"   - 密码: medical_admin_2024")
        
        # 功能模块状态
        print(f"\n🛡️ 安全功能:")
        print(f"   - 用户认证: ✅ 已启用")
        print(f"   - 权限管理: ✅ 已启用")
        print(f"   - 审计日志: ✅ 已启用")
        print(f"   - 敏感信息检测: ✅ 已启用")
        print(f"   - 配置管理: ✅ 已启用")
        
        print("\n" + "="*60)
        print("系统启动完成! 按 Ctrl+C 停止服务")
        print("="*60)
    
    def monitor_processes(self):
        """监控子进程状态"""
        while self.running:
            try:
                # 检查Flask进程
                if self.flask_process and self.flask_process.poll() is not None:
                    print("⚠️ Flask服务器意外退出，正在重启...")
                    self.start_flask_server()
                
                # 检查WebSocket进程
                if self.websocket_process and self.websocket_process.poll() is not None:
                    print("⚠️ WebSocket服务器意外退出，正在重启...")
                    self.start_websocket_server()
                
                time.sleep(5)  # 每5秒检查一次
                
            except Exception as e:
                print(f"监控进程异常: {str(e)}")
                time.sleep(5)
    
    def stop_services(self):
        """停止所有服务"""
        print("\n🛑 正在停止服务...")
        
        if self.flask_process:
            try:
                self.flask_process.terminate()
                self.flask_process.wait(timeout=5)
                print("✅ Flask服务器已停止")
            except subprocess.TimeoutExpired:
                self.flask_process.kill()
                print("⚠️ 强制终止Flask服务器")
            except Exception as e:
                print(f"⚠️ 停止Flask服务器异常: {str(e)}")
        
        if self.websocket_process:
            try:
                self.websocket_process.terminate()
                self.websocket_process.wait(timeout=5)
                print("✅ WebSocket服务器已停止")
            except subprocess.TimeoutExpired:
                self.websocket_process.kill()
                print("⚠️ 强制终止WebSocket服务器")
            except Exception as e:
                print(f"⚠️ 停止WebSocket服务器异常: {str(e)}")
    
    def start(self):
        """启动系统"""
        print("🔍 检查系统环境...")
        
        # 检查依赖和文件
        if not self.check_dependencies() or not self.check_files():
            print("❌ 系统环境检查失败，无法启动")
            return False
        
        # 启动服务
        flask_started = self.start_flask_server()
        websocket_started = self.start_websocket_server()
        
        if not (flask_started and websocket_started):
            print("❌ 服务启动失败")
            self.stop_services()
            return False
        
        # 等待服务启动
        print("⏳ 等待服务初始化...")
        time.sleep(3)
        
        # 显示系统信息
        self.show_system_info()
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        monitor_thread.start()
        
        # 保持主进程运行
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        # 清理资源
        self.stop_services()
        print("👋 系统已完全关闭")
        return True

def main():
    """主函数"""
    launcher = SystemLauncher()
    success = launcher.start()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
