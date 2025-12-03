# 登录系统设置完成

## 已完成的功能

✅ **登录页面** (`/src/views/Login.vue`)
- 用户登录表单
- 用户注册功能
- 密码显示/隐藏切换
- 错误提示和加载状态
- 响应式设计

✅ **用户认证状态管理** (`/src/stores/auth.js`)
- Pinia状态管理
- JWT token处理
- 登录/注册/登出功能
- 认证API请求封装
- 本地存储持久化

✅ **路由守卫** (`/src/router/index.js`)
- 保护需要认证的页面
- 自动跳转到登录页
- 登录后重定向到原页面
- Token有效性检查

✅ **导航栏用户菜单** (`/src/components/Layout.vue`)
- 显示当前用户信息
- 用户角色标识
- 登出功能
- 下拉菜单

✅ **聊天组件更新** (`/src/components/ChatBox.vue`)
- 使用认证的API请求
- 错误处理和用户反馈
- 敏感信息提示
- 个性化欢迎消息

## 默认账号

**管理员账号：**
- 用户名: `admin`
- 密码: `medical_admin_2024`

## 启动步骤

1. **启动后端服务**
   ```bash
   cd QASystemOnMedicalKG-master
   python app.py
   ```

2. **启动前端服务**
   ```bash
   cd kg-frontend
   npm run dev
   ```

3. **访问系统**
   - 打开浏览器访问 `http://localhost:5173`
   - 系统会自动跳转到登录页面
   - 使用默认账号或注册新账号登录

## 功能说明

### 认证流程
1. 用户访问任何页面时，系统检查登录状态
2. 未登录用户自动跳转到 `/login` 页面
3. 登录成功后跳转到原访问页面或首页
4. 所有API请求自动携带认证token

### 安全特性
- JWT token认证
- 密码哈希存储
- 敏感信息检测和脱敏
- 审计日志记录
- 路由级别的访问控制

### 用户体验
- 响应式设计，支持移动端
- 实时错误提示
- 加载状态指示
- 记住登录状态
- 优雅的错误处理

## API端点

- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册  
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/profile` - 获取用户信息
- `POST /ask` - 问答接口（需要认证）

## 注意事项

1. 确保后端服务在 `http://localhost:5000` 运行
2. 如需修改API地址，请更新 `src/stores/auth.js` 中的 `API_BASE_URL`
3. 首次使用建议先用管理员账号登录测试系统功能
4. 生产环境请修改默认管理员密码和JWT密钥






