import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useAuthStore } from './auth'

export const useConfigStore = defineStore('config', () => {
  // 状态
  const configs = ref({})
  const loading = ref(false)
  const error = ref(null)

  // 计算属性
  const hasConfigs = computed(() => Object.keys(configs.value).length > 0)

  // 获取配置
  const getConfig = async (configType) => {
    const authStore = useAuthStore()
    
    loading.value = true
    error.value = null
    
    try {
      const response = await authStore.authenticatedRequest(`/api/admin/config/${configType}`, {
        method: 'GET'
      })
      
      configs.value[configType] = response.config
      return response.config
    } catch (err) {
      error.value = err.message || '获取配置失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新配置
  const updateConfig = async (configType, updates) => {
    const authStore = useAuthStore()
    
    loading.value = true
    error.value = null
    
    try {
      const response = await authStore.authenticatedRequest(`/api/admin/config/${configType}`, {
        method: 'PUT',
        body: JSON.stringify({ updates })
      })
      
      // 更新本地缓存
      configs.value[configType] = { ...configs.value[configType], ...updates }
      
      return response
    } catch (err) {
      error.value = err.message || '更新配置失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 验证配置
  const validateConfig = async (configType, configData) => {
    const authStore = useAuthStore()
    
    try {
      const response = await authStore.authenticatedRequest('/api/admin/validate-config', {
        method: 'POST',
        body: JSON.stringify({ 
          config_type: configType,
          config_data: configData 
        })
      })
      
      return response.validation_result
    } catch (err) {
      console.error('验证配置失败:', err)
      return {
        valid: false,
        errors: ['验证请求失败'],
        warnings: []
      }
    }
  }

  // 创建备份
  const createBackup = async (configType) => {
    const authStore = useAuthStore()
    
    try {
      const response = await authStore.authenticatedRequest('/api/admin/backup-config', {
        method: 'POST',
        body: JSON.stringify({ config_type: configType })
      })
      
      return response
    } catch (err) {
      error.value = err.message || '创建备份失败'
      throw err
    }
  }

  // 恢复备份
  const restoreBackup = async (configType, backupFilename) => {
    const authStore = useAuthStore()
    
    loading.value = true
    error.value = null
    
    try {
      const response = await authStore.authenticatedRequest('/api/admin/restore-config', {
        method: 'POST',
        body: JSON.stringify({ 
          config_type: configType,
          backup_filename: backupFilename 
        })
      })
      
      // 清除本地缓存，强制重新加载
      delete configs.value[configType]
      
      return response
    } catch (err) {
      error.value = err.message || '恢复备份失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 列出备份
  const listBackups = async (configType = null) => {
    const authStore = useAuthStore()
    
    try {
      const url = configType 
        ? `/api/admin/list-backups?config_type=${configType}`
        : '/api/admin/list-backups'
        
      const response = await authStore.authenticatedRequest(url, {
        method: 'GET'
      })
      
      return response.backups || []
    } catch (err) {
      console.error('获取备份列表失败:', err)
      return []
    }
  }

  // 导出配置
  const exportConfig = async (configTypes = null) => {
    const authStore = useAuthStore()
    
    try {
      const body = configTypes ? { config_types: configTypes } : {}
      
      const response = await fetch('/api/admin/export-config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authStore.token}`
        },
        body: JSON.stringify(body)
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      // 下载文件
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `config_export_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      return true
    } catch (err) {
      error.value = err.message || '导出配置失败'
      throw err
    }
  }

  // 导入配置
  const importConfig = async (file, configTypes = null) => {
    const authStore = useAuthStore()
    
    loading.value = true
    error.value = null
    
    try {
      const formData = new FormData()
      formData.append('config_file', file)
      
      if (configTypes) {
        formData.append('config_types', JSON.stringify(configTypes))
      }
      
      const response = await fetch('/api/admin/import-config', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authStore.token}`
        },
        body: formData
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`)
      }
      
      // 清除本地缓存
      configs.value = {}
      
      return data
    } catch (err) {
      error.value = err.message || '导入配置失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 重置为默认配置
  const resetToDefault = async (configType) => {
    const authStore = useAuthStore()
    
    loading.value = true
    error.value = null
    
    try {
      const response = await authStore.authenticatedRequest('/api/admin/reset-config', {
        method: 'POST',
        body: JSON.stringify({ config_type: configType })
      })
      
      // 清除本地缓存
      delete configs.value[configType]
      
      return response
    } catch (err) {
      error.value = err.message || '重置配置失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取配置哈希值（用于检测变化）
  const getConfigHash = async (configType) => {
    const authStore = useAuthStore()
    
    try {
      const response = await authStore.authenticatedRequest(`/api/admin/config-hash/${configType}`, {
        method: 'GET'
      })
      
      return response.hash
    } catch (err) {
      console.error('获取配置哈希失败:', err)
      return null
    }
  }

  // 批量获取所有配置
  const getAllConfigs = async () => {
    const configTypes = ['main', 'api', 'security', 'database']
    const results = {}
    
    loading.value = true
    error.value = null
    
    try {
      const promises = configTypes.map(async (type) => {
        try {
          const config = await getConfig(type)
          results[type] = config
        } catch (err) {
          console.error(`获取${type}配置失败:`, err)
          results[type] = null
        }
      })
      
      await Promise.all(promises)
      return results
    } finally {
      loading.value = false
    }
  }

  // 监控配置变化
  const watchConfigChanges = async (configType, callback, interval = 30000) => {
    let lastHash = await getConfigHash(configType)
    
    const checkChanges = async () => {
      try {
        const currentHash = await getConfigHash(configType)
        if (currentHash && currentHash !== lastHash) {
          lastHash = currentHash
          const newConfig = await getConfig(configType)
          callback(newConfig, configType)
        }
      } catch (err) {
        console.error('检查配置变化失败:', err)
      }
    }
    
    const intervalId = setInterval(checkChanges, interval)
    
    // 返回清理函数
    return () => clearInterval(intervalId)
  }

  // 清除错误
  const clearError = () => {
    error.value = null
  }

  // 清除缓存
  const clearCache = () => {
    configs.value = {}
  }

  return {
    // 状态
    configs,
    loading,
    error,
    
    // 计算属性
    hasConfigs,
    
    // 方法
    getConfig,
    updateConfig,
    validateConfig,
    createBackup,
    restoreBackup,
    listBackups,
    exportConfig,
    importConfig,
    resetToDefault,
    getConfigHash,
    getAllConfigs,
    watchConfigChanges,
    clearError,
    clearCache
  }
})






