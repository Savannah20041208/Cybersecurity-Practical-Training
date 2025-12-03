import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

// API基础URL - 根据实际后端地址调整
const API_BASE_URL = 'http://localhost:5000'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('auth_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('auth_user') || 'null'))
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // API请求封装
  const apiRequest = async (url, options = {}) => {
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    }

    // 如果有token，添加到请求头
    if (token.value) {
      config.headers.Authorization = `Bearer ${token.value}`
    }

    try {
      const response = await fetch(`${API_BASE_URL}${url}`, config)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`)
      }

      return data
    } catch (error) {
      console.error('API请求失败:', error)
      throw error
    }
  }

  // 登录
  const login = async (username, password) => {
    loading.value = true
    
    try {
      const data = await apiRequest('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
      })

      // 保存token和用户信息
      token.value = data.token
      user.value = data.user
      
      // 持久化存储
      localStorage.setItem('auth_token', data.token)
      localStorage.setItem('auth_user', JSON.stringify(data.user))

      return data
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (username, password) => {
    loading.value = true
    
    try {
      const data = await apiRequest('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify({ username, password })
      })

      return data
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      // 如果有token，通知后端登出
      if (token.value) {
        await apiRequest('/api/auth/logout', {
          method: 'POST'
        })
      }
    } catch (error) {
      console.error('登出请求失败:', error)
      // 即使后端请求失败，也要清除本地数据
    } finally {
      // 清除本地存储
      token.value = null
      user.value = null
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
    }
  }

  // 获取用户信息
  const fetchProfile = async () => {
    if (!token.value) return null

    try {
      const data = await apiRequest('/api/auth/profile')
      user.value = data.user
      localStorage.setItem('auth_user', JSON.stringify(data.user))
      return data.user
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果token无效，清除登录状态
      if (error.message.includes('401') || error.message.includes('未授权')) {
        await logout()
      }
      throw error
    }
  }

  // 检查token有效性
  const checkAuth = async () => {
    if (!token.value) return false

    try {
      await fetchProfile()
      return true
    } catch (error) {
      console.error('认证检查失败:', error)
      await logout()
      return false
    }
  }

  // 发送认证请求（用于其他API调用）
  const authenticatedRequest = async (url, options = {}) => {
    if (!isAuthenticated.value) {
      throw new Error('用户未登录')
    }

    return apiRequest(url, options)
  }

  return {
    // 状态
    token,
    user,
    loading,
    
    // 计算属性
    isAuthenticated,
    
    // 方法
    login,
    register,
    logout,
    fetchProfile,
    checkAuth,
    authenticatedRequest
  }
})

