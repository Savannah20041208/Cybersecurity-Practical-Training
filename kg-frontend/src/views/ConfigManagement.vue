<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">系统配置管理</h1>
        <p class="text-gray-600">管理系统配置、备份恢复和安全设置</p>
      </div>

      <!-- 配置类型选择 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 mb-6">
        <div class="p-6 border-b border-gray-200">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">配置类型</h2>
          <div class="flex flex-wrap gap-3">
            <button
              v-for="type in configTypes"
              :key="type.key"
              @click="selectConfigType(type.key)"
              :class="[
                'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-2',
                selectedConfigType === type.key
                  ? 'bg-blue-100 text-blue-700 border-2 border-blue-300'
                  : 'bg-gray-100 text-gray-700 border-2 border-transparent hover:bg-gray-200'
              ]"
            >
              <component :is="type.icon" class="w-4 h-4" />
              {{ type.name }}
            </button>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <!-- 配置编辑区域 -->
        <div class="xl:col-span-2">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200">
            <div class="p-6 border-b border-gray-200 flex justify-between items-center">
              <h3 class="text-lg font-semibold text-gray-900">
                {{ getCurrentConfigType()?.name || '配置编辑' }}
              </h3>
              <div class="flex gap-2">
                <button
                  @click="validateConfig"
                  :disabled="loading"
                  class="px-3 py-2 text-sm bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  <CheckCircleIcon class="w-4 h-4" />
                  验证配置
                </button>
                <button
                  @click="saveConfig"
                  :disabled="loading || !hasChanges"
                  class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  <SaveIcon class="w-4 h-4" />
                  {{ loading ? '保存中...' : '保存配置' }}
                </button>
              </div>
            </div>

            <div class="p-6">
              <!-- 配置编辑器 -->
              <div v-if="selectedConfigType && currentConfig">
                <!-- 主配置 -->
                <div v-if="selectedConfigType === 'main'" class="space-y-6">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">应用名称</label>
                      <input
                        v-model="currentConfig.app_name"
                        type="text"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">版本</label>
                      <input
                        v-model="currentConfig.version"
                        type="text"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">主机地址</label>
                      <input
                        v-model="currentConfig.host"
                        type="text"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">端口</label>
                      <input
                        v-model.number="currentConfig.port"
                        type="number"
                        min="1"
                        max="65535"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">最大查询长度</label>
                      <input
                        v-model.number="currentConfig.max_query_length"
                        type="number"
                        min="100"
                        max="2000"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">会话超时(秒)</label>
                      <input
                        v-model.number="currentConfig.session_timeout"
                        type="number"
                        min="300"
                        max="86400"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div class="flex items-center">
                    <input
                      v-model="currentConfig.debug"
                      type="checkbox"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label class="ml-2 block text-sm text-gray-700">启用调试模式</label>
                  </div>
                </div>

                <!-- API配置 -->
                <div v-else-if="selectedConfigType === 'api'" class="space-y-6">
                  <!-- CORS配置 -->
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-md font-medium text-gray-900 mb-3">CORS设置</h4>
                    <div class="space-y-3">
                      <div class="flex items-center">
                        <input
                          v-model="currentConfig.cors.enabled"
                          type="checkbox"
                          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label class="ml-2 block text-sm text-gray-700">启用CORS</label>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">允许的源</label>
                        <div class="space-y-2">
                          <div v-for="(origin, index) in currentConfig.cors.origins" :key="index" class="flex gap-2">
                            <input
                              v-model="currentConfig.cors.origins[index]"
                              type="text"
                              class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              placeholder="http://localhost:3000"
                            />
                            <button
                              @click="removeOrigin(index)"
                              class="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            >
                              <XMarkIcon class="w-4 h-4" />
                            </button>
                          </div>
                          <button
                            @click="addOrigin"
                            class="px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors text-sm"
                          >
                            + 添加源
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 限流配置 -->
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-md font-medium text-gray-900 mb-3">限流设置</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div class="flex items-center">
                        <input
                          v-model="currentConfig.rate_limiting.enabled"
                          type="checkbox"
                          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label class="ml-2 block text-sm text-gray-700">启用限流</label>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">每分钟请求数</label>
                        <input
                          v-model.number="currentConfig.rate_limiting.requests_per_minute"
                          type="number"
                          min="1"
                          max="1000"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 安全配置 -->
                <div v-else-if="selectedConfigType === 'security'" class="space-y-6">
                  <!-- JWT配置 -->
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-md font-medium text-gray-900 mb-3">JWT设置</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">过期时间(小时)</label>
                        <input
                          v-model.number="currentConfig.jwt.expiration_hours"
                          type="number"
                          min="1"
                          max="168"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">算法</label>
                        <select
                          v-model="currentConfig.jwt.algorithm"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="HS256">HS256</option>
                          <option value="HS384">HS384</option>
                          <option value="HS512">HS512</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  <!-- 密码策略 -->
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-md font-medium text-gray-900 mb-3">密码策略</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">最小长度</label>
                        <input
                          v-model.number="currentConfig.password_policy.min_length"
                          type="number"
                          min="6"
                          max="32"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">密码有效期(天)</label>
                        <input
                          v-model.number="currentConfig.password_policy.max_age_days"
                          type="number"
                          min="30"
                          max="365"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                    <div class="mt-4 space-y-2">
                      <div class="flex items-center">
                        <input
                          v-model="currentConfig.password_policy.require_uppercase"
                          type="checkbox"
                          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label class="ml-2 block text-sm text-gray-700">要求大写字母</label>
                      </div>
                      <div class="flex items-center">
                        <input
                          v-model="currentConfig.password_policy.require_numbers"
                          type="checkbox"
                          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label class="ml-2 block text-sm text-gray-700">要求数字</label>
                      </div>
                      <div class="flex items-center">
                        <input
                          v-model="currentConfig.password_policy.require_special_chars"
                          type="checkbox"
                          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label class="ml-2 block text-sm text-gray-700">要求特殊字符</label>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 数据库配置 -->
                <div v-else-if="selectedConfigType === 'database'" class="space-y-6">
                  <!-- Neo4j配置 -->
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-md font-medium text-gray-900 mb-3">Neo4j数据库</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">URI</label>
                        <input
                          v-model="currentConfig.neo4j.uri"
                          type="text"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="bolt://localhost:7687"
                        />
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">用户名</label>
                        <input
                          v-model="currentConfig.neo4j.username"
                          type="text"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">密码</label>
                        <input
                          v-model="currentConfig.neo4j.password"
                          type="password"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">数据库名</label>
                        <input
                          v-model="currentConfig.neo4j.database"
                          type="text"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <!-- JSON编辑器 (高级模式) -->
                <div v-else class="space-y-4">
                  <div class="flex items-center justify-between">
                    <span class="text-sm text-gray-600">高级JSON编辑模式</span>
                    <button
                      @click="formatJson"
                      class="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    >
                      格式化
                    </button>
                  </div>
                  <textarea
                    v-model="configJsonString"
                    class="w-full h-96 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                    placeholder="JSON配置内容..."
                  ></textarea>
                </div>
              </div>

              <!-- 空状态 -->
              <div v-else class="text-center py-12">
                <CogIcon class="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p class="text-gray-500">请选择要编辑的配置类型</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 侧边栏 -->
        <div class="space-y-6">
          <!-- 配置状态 -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">配置状态</h3>
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">配置有效性</span>
                <span :class="[
                  'px-2 py-1 text-xs rounded-full',
                  validationResult?.valid 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-red-100 text-red-700'
                ]">
                  {{ validationResult?.valid ? '有效' : '无效' }}
                </span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">未保存更改</span>
                <span :class="[
                  'px-2 py-1 text-xs rounded-full',
                  hasChanges 
                    ? 'bg-yellow-100 text-yellow-700' 
                    : 'bg-gray-100 text-gray-700'
                ]">
                  {{ hasChanges ? '有' : '无' }}
                </span>
              </div>
            </div>

            <!-- 验证错误 -->
            <div v-if="validationResult && !validationResult.valid" class="mt-4">
              <h4 class="text-sm font-medium text-red-700 mb-2">验证错误</h4>
              <ul class="text-xs text-red-600 space-y-1">
                <li v-for="error in validationResult.errors" :key="error">• {{ error }}</li>
              </ul>
            </div>

            <!-- 验证警告 -->
            <div v-if="validationResult && validationResult.warnings?.length" class="mt-4">
              <h4 class="text-sm font-medium text-yellow-700 mb-2">警告</h4>
              <ul class="text-xs text-yellow-600 space-y-1">
                <li v-for="warning in validationResult.warnings" :key="warning">• {{ warning }}</li>
              </ul>
            </div>
          </div>

          <!-- 备份管理 -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">备份管理</h3>
              <button
                @click="createBackup"
                :disabled="!selectedConfigType || loading"
                class="px-3 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                创建备份
              </button>
            </div>

            <div class="space-y-2 max-h-64 overflow-y-auto">
              <div
                v-for="backup in backups"
                :key="backup.filename"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <div class="text-sm font-medium text-gray-900">{{ backup.config_type }}</div>
                  <div class="text-xs text-gray-500">{{ formatDate(backup.created_at) }}</div>
                </div>
                <button
                  @click="restoreBackup(backup)"
                  class="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                >
                  恢复
                </button>
              </div>
              
              <div v-if="!backups.length" class="text-center py-4 text-gray-500 text-sm">
                暂无备份
              </div>
            </div>
          </div>

          <!-- 快速操作 -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">快速操作</h3>
            <div class="space-y-3">
              <button
                @click="exportConfig"
                class="w-full px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
              >
                <DownloadIcon class="w-4 h-4" />
                导出配置
              </button>
              <button
                @click="importConfig"
                class="w-full px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
              >
                <UploadIcon class="w-4 h-4" />
                导入配置
              </button>
              <button
                @click="resetToDefault"
                class="w-full px-4 py-2 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors flex items-center justify-center gap-2"
              >
                <ArrowPathIcon class="w-4 h-4" />
                重置为默认
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 导入文件输入 -->
    <input
      ref="fileInput"
      type="file"
      accept=".json"
      @change="handleFileImport"
      class="hidden"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useConfigStore } from '../stores/config'
import { useAuthStore } from '../stores/auth'

const configStore = useConfigStore()
const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const selectedConfigType = ref('main')
const currentConfig = ref(null)
const originalConfig = ref(null)
const configJsonString = ref('')
const validationResult = ref(null)
const backups = ref([])
const fileInput = ref(null)

// 配置类型定义
const configTypes = [
  { key: 'main', name: '主配置', icon: 'CogIcon' },
  { key: 'api', name: 'API配置', icon: 'CloudIcon' },
  { key: 'security', name: '安全配置', icon: 'ShieldCheckIcon' },
  { key: 'database', name: '数据库配置', icon: 'CircleStackIcon' }
]

// 计算属性
const hasChanges = computed(() => {
  if (!currentConfig.value || !originalConfig.value) return false
  return JSON.stringify(currentConfig.value) !== JSON.stringify(originalConfig.value)
})

const getCurrentConfigType = () => {
  return configTypes.find(type => type.key === selectedConfigType.value)
}

// 方法
const selectConfigType = async (type) => {
  if (hasChanges.value) {
    if (!confirm('有未保存的更改，确定要切换配置类型吗？')) {
      return
    }
  }
  
  selectedConfigType.value = type
  await loadConfig()
}

const loadConfig = async () => {
  if (!selectedConfigType.value) return
  
  loading.value = true
  try {
    const config = await configStore.getConfig(selectedConfigType.value)
    currentConfig.value = JSON.parse(JSON.stringify(config))
    originalConfig.value = JSON.parse(JSON.stringify(config))
    configJsonString.value = JSON.stringify(config, null, 2)
    validationResult.value = null
  } catch (error) {
    console.error('加载配置失败:', error)
  } finally {
    loading.value = false
  }
}

const saveConfig = async () => {
  if (!selectedConfigType.value || !currentConfig.value) return
  
  loading.value = true
  try {
    await configStore.updateConfig(selectedConfigType.value, currentConfig.value)
    originalConfig.value = JSON.parse(JSON.stringify(currentConfig.value))
    await loadBackups()
  } catch (error) {
    console.error('保存配置失败:', error)
  } finally {
    loading.value = false
  }
}

const validateConfig = async () => {
  if (!selectedConfigType.value) return
  
  try {
    validationResult.value = await configStore.validateConfig(selectedConfigType.value, currentConfig.value)
  } catch (error) {
    console.error('验证配置失败:', error)
  }
}

const createBackup = async () => {
  if (!selectedConfigType.value) return
  
  loading.value = true
  try {
    await configStore.createBackup(selectedConfigType.value)
    await loadBackups()
  } catch (error) {
    console.error('创建备份失败:', error)
  } finally {
    loading.value = false
  }
}

const restoreBackup = async (backup) => {
  if (!confirm(`确定要恢复到备份 ${backup.filename} 吗？这将覆盖当前配置。`)) {
    return
  }
  
  loading.value = true
  try {
    await configStore.restoreBackup(backup.config_type, backup.filename)
    await loadConfig()
  } catch (error) {
    console.error('恢复备份失败:', error)
  } finally {
    loading.value = false
  }
}

const loadBackups = async () => {
  try {
    backups.value = await configStore.listBackups(selectedConfigType.value)
  } catch (error) {
    console.error('加载备份列表失败:', error)
  }
}

const exportConfig = async () => {
  try {
    await configStore.exportConfig([selectedConfigType.value])
  } catch (error) {
    console.error('导出配置失败:', error)
  }
}

const importConfig = () => {
  fileInput.value?.click()
}

const handleFileImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  try {
    await configStore.importConfig(file, [selectedConfigType.value])
    await loadConfig()
    event.target.value = '' // 清空文件输入
  } catch (error) {
    console.error('导入配置失败:', error)
  }
}

const resetToDefault = async () => {
  if (!confirm('确定要重置为默认配置吗？这将丢失所有自定义设置。')) {
    return
  }
  
  try {
    await configStore.resetToDefault(selectedConfigType.value)
    await loadConfig()
  } catch (error) {
    console.error('重置配置失败:', error)
  }
}

const formatJson = () => {
  try {
    const parsed = JSON.parse(configJsonString.value)
    configJsonString.value = JSON.stringify(parsed, null, 2)
    currentConfig.value = parsed
  } catch (error) {
    alert('JSON格式错误，请检查语法')
  }
}

const addOrigin = () => {
  if (!currentConfig.value.cors) {
    currentConfig.value.cors = { origins: [] }
  }
  currentConfig.value.cors.origins.push('')
}

const removeOrigin = (index) => {
  currentConfig.value.cors.origins.splice(index, 1)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 监听配置变化
watch(currentConfig, (newConfig) => {
  if (newConfig) {
    configJsonString.value = JSON.stringify(newConfig, null, 2)
  }
}, { deep: true })

watch(configJsonString, (newValue) => {
  try {
    const parsed = JSON.parse(newValue)
    currentConfig.value = parsed
  } catch (error) {
    // JSON格式错误，不更新currentConfig
  }
})

// 生命周期
onMounted(async () => {
  // 检查管理员权限
  if (authStore.user?.role !== 'admin') {
    alert('只有管理员可以访问配置管理')
    return
  }
  
  await loadConfig()
  await loadBackups()
})
</script>

<script>
// 图标组件
const CogIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0Z" /></svg>`
}

const CloudIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15a4.5 4.5 0 004.5 4.5H18a3.75 3.75 0 001.332-7.257 3 3 0 00-3.758-3.848 5.25 5.25 0 00-10.233 2.33A4.502 4.502 0 002.25 15z" /></svg>`
}

const ShieldCheckIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" /></svg>`
}

const CircleStackIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" /></svg>`
}

const CheckCircleIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`
}

const SaveIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0z" /></svg>`
}

const XMarkIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>`
}

const DownloadIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" /></svg>`
}

const UploadIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" /></svg>`
}

const ArrowPathIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" /></svg>`
}

export default {
  components: {
    CogIcon,
    CloudIcon,
    ShieldCheckIcon,
    CircleStackIcon,
    CheckCircleIcon,
    SaveIcon,
    XMarkIcon,
    DownloadIcon,
    UploadIcon,
    ArrowPathIcon
  }
}
</script>






