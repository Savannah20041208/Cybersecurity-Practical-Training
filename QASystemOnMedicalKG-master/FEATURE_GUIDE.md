# 医疗知识图谱问答系统 - 新功能使用指南

## 🎯 功能概述

本系统在原有医疗知识图谱问答功能基础上，融合了PHP代码中的优秀设计理念，新增了以下核心功能模块：

### 🔐 用户认证授权系统
- 用户注册/登录/登出
- JWT令牌认证
- 角色权限管理
- 密码强度策略

### 📊 审计日志系统
- 全面记录用户操作
- 医疗查询审计
- 敏感信息访问追踪
- 系统统计分析
- 日志导出功能

### 🛡️ 敏感信息检测
- 身份证号、手机号检测
- 患者姓名识别
- 医疗记录脱敏
- 风险等级评估
- 自动脱敏处理

### ⚙️ 配置管理系统
- 统一配置管理
- 配置备份恢复
- 动态配置更新
- 配置验证检查

### 🔌 WebSocket实时通信
- 实时问答交互
- 连接状态管理
- 认证集成
- 消息广播

---

## 🚀 快速启动

### 1. 安装依赖
```bash
pip install flask flask-cors pyjwt websockets neo4j
```

### 2. 启动系统
```bash
# 方式1: 使用启动脚本（推荐）
python start_system.py

# 方式2: 分别启动
python app.py          # Flask API服务器
python websocket_server.py  # WebSocket服务器
```

### 3. 访问系统
- **API服务**: http://localhost:5000
- **测试页面**: http://localhost:5000/test
- **WebSocket**: ws://localhost:8765

---

## 🔐 用户认证

### 注册新用户
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "doctor01",
    "password": "StrongPass123!"
  }'
```

### 用户登录
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "doctor01", 
    "password": "StrongPass123!"
  }'
```

**返回示例**:
```json
{
  "message": "登录成功",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 2,
    "username": "doctor01",
    "role": "user"
  }
}
```

### 认证问答请求
```bash
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "question": "什么是高血压？"
  }'
```

---

## 🔌 WebSocket使用

### 前端连接示例
```javascript
const ws = new WebSocket('ws://localhost:8765');

// 1. 连接后发送认证
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'YOUR_JWT_TOKEN'
  }));
};

// 2. 处理消息
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'auth_success':
      console.log('认证成功:', data.user);
      // 可以开始发送问题
      break;
      
    case 'answer':
      console.log('收到答案:', data.answer);
      break;
      
    case 'error':
      console.error('错误:', data.error);
      break;
  }
};

// 3. 发送问题
const askQuestion = (question) => {
  ws.send(JSON.stringify({
    type: 'question',
    question: question
  }));
};

// 使用示例
askQuestion("阿司匹林的副作用有哪些？");
```

---

## 📊 管理员功能

### 默认管理员账户
- **用户名**: `admin`
- **密码**: `medical_admin_2024`

### 获取系统统计
```bash
curl -X GET "http://localhost:5000/api/admin/stats?days=7" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

### 查看用户活动
```bash
curl -X GET "http://localhost:5000/api/admin/user-activity/2?limit=50" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

### 导出审计日志
```bash
curl -X POST http://localhost:5000/api/admin/export-logs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -d '{
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

### 敏感信息检测
```bash
curl -X POST http://localhost:5000/api/admin/check-sensitive \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -d '{
    "text": "患者王小明，身份证号：110101199001011234，手机：13812345678"
  }'
```

**返回示例**:
```json
{
  "detections": [
    {
      "type": "中文姓名",
      "category": "patient_name",
      "risk_level": "critical",
      "matched_text": "王小明",
      "confidence": 0.8
    }
  ],
  "risk_summary": {
    "total_count": 3,
    "risk_level": "critical",
    "recommendation": "检测到极高风险敏感信息，建议立即处理"
  },
  "masked_text": "患者***，身份证号：***********1234，手机：138****5678"
}
```

---

## ⚙️ 配置管理

### 查看配置
```bash
# 查看主配置
curl -X GET http://localhost:5000/api/admin/config/main \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"

# 查看数据库配置
curl -X GET http://localhost:5000/api/admin/config/database \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

### 更新配置
```bash
curl -X PUT http://localhost:5000/api/admin/config/main \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -d '{
    "updates": {
      "max_query_length": 1000,
      "debug": false
    }
  }'
```

---

## 🛡️ 安全特性

### 1. 敏感信息自动检测与脱敏
- 系统自动检测查询和回答中的敏感信息
- 根据风险等级进行不同程度的脱敏处理
- 极高风险内容会被系统拒绝处理

### 2. 全面审计日志
- 记录所有用户操作和系统事件
- 敏感信息访问特别标记
- 支持按时间范围和用户筛选

### 3. 密码策略
```json
{
  "min_length": 8,
  "require_uppercase": true,
  "require_lowercase": true, 
  "require_numbers": true,
  "require_special_chars": true
}
```

### 4. JWT令牌安全
- 24小时过期时间
- 安全密钥加密
- 自动过期检测

---

## 📁 文件结构

```
QASystemOnMedicalKG-master/
├── app.py                 # Flask API服务器
├── websocket_server.py    # WebSocket服务器
├── start_system.py        # 系统启动脚本
├── auth_manager.py        # 用户认证管理
├── audit_logger.py        # 审计日志系统
├── sensitive_detector.py  # 敏感信息检测
├── config_manager.py      # 配置管理系统
├── chatbot_graph.py       # 原有问答逻辑
├── config/                # 配置目录
│   ├── main_config.json
│   ├── database_config.json
│   ├── api_config.json
│   └── security_config.json
└── FEATURE_GUIDE.md       # 本文档
```

---

## 🔧 开发者说明

### 数据库文件
- `medical_users.db`: 用户认证数据
- `medical_audit.db`: 审计日志数据
- `medical_cache.db`: 缓存数据（可选）

### 配置文件位置
- 配置文件存储在 `config/` 目录
- 备份文件存储在 `config/backups/` 目录

### 扩展开发
1. **添加新的敏感信息模式**: 修改 `sensitive_detector.py` 中的 `_init_patterns()` 方法
2. **新增API接口**: 在 `app.py` 中添加路由和认证装饰器
3. **自定义配置**: 修改 `config_manager.py` 中的默认配置

---

## ❓ 常见问题

### Q: 忘记管理员密码怎么办？
A: 删除 `medical_users.db` 文件，重启系统会自动创建默认管理员账户。

### Q: 如何修改WebSocket端口？
A: 修改 `config/api_config.json` 中的 `websocket.port` 配置。

### Q: 敏感信息检测太严格怎么办？
A: 可以在 `sensitive_detector.py` 中调整检测规则或添加白名单词汇。

### Q: 如何查看详细日志？
A: 检查控制台输出，或使用管理员API导出审计日志进行分析。

---

## 🎉 总结

通过融合PHP代码中的优秀功能模块，本系统现在具备了：

✅ **企业级安全**: 完整的认证授权体系  
✅ **合规审计**: 医疗级别的操作记录  
✅ **隐私保护**: 自动敏感信息检测与脱敏  
✅ **运维友好**: 统一配置管理和监控  
✅ **现代化通信**: WebSocket实时交互  

这些功能使得医疗知识图谱系统更加适合在实际医疗环境中部署和使用。
