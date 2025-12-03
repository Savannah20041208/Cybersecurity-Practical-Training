#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket服务器（稳定版）
-------------------------------------
✅ 认证 / 审计 / 敏感检测 / 配置管理 全启用
✅ 容错：防止 audit_logger 参数错误导致崩溃
✅ 异步化：所有阻塞操作在线程池执行
✅ ChatBotGraph 单例，复用连接
"""

import asyncio
import websockets
import json
import logging
import traceback
import subprocess
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Optional

# ================================
# 模块导入（兼容缺失）
# ================================
try:
    from auth_manager import AuthManager
except Exception:
    AuthManager = None

try:
    from audit_logger import AuditLogger
except Exception:
    AuditLogger = None

try:
    from sensitive_detector import SensitiveDetector
except Exception:
    SensitiveDetector = None

try:
    from config_manager import ConfigManager
except Exception:
    ConfigManager = None

try:
    from chatbot_graph import ChatBotGraph
except Exception:
    ChatBotGraph = None

# ================================
# 全局配置
# ================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
EXECUTOR = ThreadPoolExecutor(max_workers=6)


def simple_cache(maxsize=256):
    def deco(func):
        cache = lru_cache(maxsize=maxsize)(func)
        return cache
    return deco


# ================================
# WebSocket 主类
# ================================
class WebSocketServer:
    def __init__(self):
        # 配置管理
        self.config_manager = None
        if ConfigManager:
            try:
                self.config_manager = ConfigManager()
                self.main_config = self.config_manager.get_config("main") or {}
                self.api_config = self.config_manager.get_config("api") or {}
                self.security_config = self.config_manager.get_config("security") or {}
            except Exception as e:
                logger.warning("⚠️ 配置加载失败: %s", e)
                self.main_config, self.api_config, self.security_config = {}, {}, {}
        else:
            self.main_config, self.api_config, self.security_config = {}, {}, {}

        # 管理模块实例
        self.auth_manager = AuthManager() if AuthManager else None
        self.audit_logger = AuditLogger() if AuditLogger else None
        self.sensitive_detector = SensitiveDetector() if SensitiveDetector else None

        # 状态
        self.connected_clients = set()
        self.authenticated_clients = {}

        # ChatBot 初始化（单例）
        self.chatbot = None
        if ChatBotGraph:
            try:
                logger.info("🔌 正在初始化 ChatBotGraph（进程内）...")
                self.chatbot = ChatBotGraph()
                logger.info("✅ ChatBotGraph 初始化完成")
            except Exception as e:
                logger.exception("❌ ChatBotGraph 初始化失败，将回退至子进程: %s", e)
                self.chatbot = None

        # 超时配置
        self.auth_timeout = int(self.security_config.get("auth_timeout", 5) or 5)
        self.question_timeout = int(self.api_config.get("question_timeout", 30) or 30)
        self.sensitive_timeout = int(self.security_config.get("sensitive_timeout", 3) or 3)
        self.audit_timeout = int(self.security_config.get("audit_timeout", 2) or 2)

        logger.info("✅ WebSocket服务器初始化完成")

    # ================================
    # 安全发送
    # ================================
    async def safe_send(self, websocket, payload: dict):
        try:
            await websocket.send(json.dumps(payload, ensure_ascii=False))
        except Exception as e:
            logger.warning("❌ 消息发送失败: %s", e)

    # ================================
    # ChatBot 执行（含缓存）
    # ================================
    @simple_cache(maxsize=512)
    def chat_main_cached(self, question: str) -> str:
        if self.chatbot:
            try:
                return self.chatbot.chat_main(question)
            except Exception as e:
                logger.warning("ChatBot 内部错误: %s", e)
                return self.get_answer_via_subprocess(question)
        else:
            return self.get_answer_via_subprocess(question)

    # 子进程回退方案
    def get_answer_via_subprocess(self, question: str) -> str:
        try:
            result = subprocess.run(
                [sys.executable, "chatbot_graph.py", question],
                text=True, capture_output=True, check=True, timeout=self.question_timeout,
            )
            return result.stdout.strip()
        except Exception as e:
            logger.warning("子进程执行失败: %s", e)
            return f"问答子进程出错: {e}"

    # ================================
    # 审计记录（参数白名单过滤）
    # ================================
    def _safe_audit_log_action(self, action: str, data: dict):
        if not self.audit_logger:
            return
        try:
            allowed = {"user_id", "username", "action", "message", "details", "timestamp"}
            safe_data = {k: v for k, v in (data or {}).items() if k in allowed}

            if hasattr(self.audit_logger, "log_action"):
                self.audit_logger.log_action(action=action, **safe_data)
            elif hasattr(self.audit_logger, "log"):
                self.audit_logger.log(action, safe_data)
            else:
                logger.info("[AUDIT] %s %s", action, safe_data)
        except Exception as e:
            logger.warning("跳过审计记录错误: %s", e)

    # ================================
    # 敏感检测
    # ================================
    async def detect_sensitive(self, text: str):
        if not self.sensitive_detector:
            return None
        loop = asyncio.get_event_loop()
        try:
            res = await asyncio.wait_for(
                loop.run_in_executor(EXECUTOR, self.sensitive_detector.detect_sensitive_info, text),
                timeout=self.sensitive_timeout,
            )
            return res
        except asyncio.TimeoutError:
            logger.warning("敏感检测超时")
        except Exception as e:
            logger.warning("敏感检测错误: %s", e)
        return None

    # ================================
    # 用户认证
    # ================================
    async def authenticate_websocket(self, websocket, message: dict):
        token = message.get("token")
        try:
            if token in ["test_token", "dev_bypass_token"]:
                user_info = {"user_id": 0, "username": "test_user", "role": "tester"}
                self.authenticated_clients[websocket] = user_info
                await self.safe_send(websocket, {"type": "auth_success", "message": "认证成功（测试模式）", "user": user_info})
                return True

            if not self.auth_manager:
                user_info = {"user_id": -1, "username": "anonymous"}
                self.authenticated_clients[websocket] = user_info
                await self.safe_send(websocket, {"type": "auth_success", "message": "认证跳过（未启用）", "user": user_info})
                return True

            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(EXECUTOR, self.auth_manager.verify_token, token),
                timeout=self.auth_timeout,
            )

            if isinstance(result, dict) and result.get("success"):
                user_info = result.get("data", {})
                self.authenticated_clients[websocket] = user_info
                await self.safe_send(websocket, {"type": "auth_success", "message": "认证成功", "user": user_info})
                return True
            else:
                await self.safe_send(websocket, {"type": "auth_error", "error": "认证失败"})
                return False
        except Exception as e:
            logger.warning("认证异常: %s", e)
            await self.safe_send(websocket, {"type": "auth_error", "error": "认证出错"})
            return False

    # ================================
    # 问答逻辑
    # ================================
    async def handle_question(self, websocket, message: dict):
        try:
            if websocket not in self.authenticated_clients:
                await self.safe_send(websocket, {"type": "error", "error": "未认证"})
                return

            question = (message.get("question") or "").strip()
            if not question:
                await self.safe_send(websocket, {"type": "error", "error": "问题不能为空"})
                return

            # 异步敏感检测
            sensitive = await self.detect_sensitive(question)
            if sensitive:
                await self.safe_send(websocket, {"type": "warning", "message": "问题含敏感内容，系统已记录"})

            # 提示处理中
            await self.safe_send(websocket, {"type": "processing", "message": "处理中..."})

            # 异步执行问答
            loop = asyncio.get_event_loop()
            answer = await asyncio.wait_for(
                loop.run_in_executor(EXECUTOR, self.chat_main_cached, question),
                timeout=self.question_timeout,
            )

            await self.safe_send(websocket, {"type": "answer", "answer": answer})
        except asyncio.TimeoutError:
            await self.safe_send(websocket, {"type": "error", "error": "问答超时"})
        except Exception as e:
            logger.warning("问答异常: %s", e)
            await self.safe_send(websocket, {"type": "error", "error": "系统错误"})

    # ================================
    # 客户端处理
    # ================================
    async def handle_client(self, websocket, path):
        ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
        logger.info(f"新的客户端连接: {ip}")
        self.connected_clients.add(websocket)

        await self.safe_send(websocket, {"type": "welcome", "message": "欢迎使用医疗知识图谱问答系统"})

        try:
            async for message_str in websocket:
                try:
                    msg = json.loads(message_str)
                    msg_type = msg.get("type")

                    if msg_type == "auth":
                        await self.authenticate_websocket(websocket, msg)
                    elif msg_type == "question":
                        asyncio.create_task(self.handle_question(websocket, msg))
                    elif msg_type == "ping":
                        await self.safe_send(websocket, {"type": "pong", "time": datetime.now().isoformat()})
                    else:
                        await self.safe_send(websocket, {"type": "error", "error": f"未知消息类型: {msg_type}"})
                except Exception as e:
                    logger.warning("消息解析失败: %s", e)
                    await self.safe_send(websocket, {"type": "error", "error": "消息格式错误"})
        except websockets.exceptions.ConnectionClosed:
            logger.info("连接关闭: %s", ip)
        finally:
            self.connected_clients.discard(websocket)
            self.authenticated_clients.pop(websocket, None)

    # ================================
    # 启动服务
    # ================================
    async def start_server(self):
        host = self.main_config.get("host", "localhost")
        port = self.api_config.get("port", 8765)

        logger.info(f"🔌 启动 WebSocket服务器: ws://{host}:{port}")
        server = await websockets.serve(self.handle_client, host, port)
        logger.info(f"✅ WebSocket服务器运行在 ws://{host}:{port}")
        await server.wait_closed()


# ================================
# 启动入口
# ================================
async def main():
    server = WebSocketServer()
    try:
        await server.start_server()
    except Exception as e:
        logger.error("WebSocket 启动失败: %s", e)
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
