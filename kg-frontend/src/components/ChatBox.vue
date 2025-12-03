<template>
  <div class="w-full bg-white rounded-2xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-xl border border-gray-100">
    <!-- 对话历史区域 -->
    <div class="p-6 max-h-[600px] overflow-y-auto space-y-6" id="chatHistory">
      <!-- 示例问题提示 -->
      <div v-if="messages.length === 0" class="text-center text-gray-400 py-12 bg-gradient-to-b from-gray-50 to-transparent rounded-xl mx-4">
        <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-blue-600">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
          </svg>
        </div>
        <p class="font-medium">请输入您的问题，例如：</p>
        <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-3 px-4">
          <button
              @click="useExample('哪种药物适用于肝纤维化的治疗？')"
              class="bg-blue-50 hover:bg-blue-100 text-blue-700 px-4 py-3 rounded-lg text-sm transition-all hover:shadow-md transform hover:-translate-y-1"
          >
            哪种药物适用于肝纤维化的治疗？
          </button>
          <button
              @click="useExample('药物A对肝硬化有治疗效果吗？')"
              class="bg-blue-50 hover:bg-blue-100 text-blue-700 px-4 py-3 rounded-lg text-sm transition-all hover:shadow-md transform hover:-translate-y-1"
          >
            药物A对肝硬化有治疗效果吗？
          </button>
          <button
              @click="useExample('治疗肝癌的药物有哪些副作用？')"
              class="bg-blue-50 hover:bg-blue-100 text-blue-700 px-4 py-3 rounded-lg text-sm transition-all hover:shadow-md transform hover:-translate-y-1"
          >
            治疗肝癌的药物有哪些副作用？
          </button>
          <button
              @click="useExample('药物B和药物C能同时用于肝病治疗吗？')"
              class="bg-blue-50 hover:bg-blue-100 text-blue-700 px-4 py-3 rounded-lg text-sm transition-all hover:shadow-md transform hover:-translate-y-1"
          >
            药物B和药物C能同时用于肝病治疗吗？
          </button>
        </div>
      </div>

      <!-- 消息列表 -->
      <div v-for="(msg, index) in messages" :key="index" class="animate-fadeIn">
        <div class="flex items-start gap-3">
          <!-- 用户头像 -->
          <div v-if="msg.isUser" class="ml-auto">
            <div>
              
            </div>
            <div class="w-9 h-9 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 flex items-center justify-center text-white text-sm shadow-sm">
              用户
            </div>
          </div>

          <!-- 小肝脏 -->
          <div v-else>
            <div class="w-9 h-9 rounded-full bg-gradient-to-r from-gray-200 to-gray-100 flex items-center justify-center text-gray-700 text-sm shadow-sm">
              小肝脏
            </div>
          </div>

          <!-- 消息内容 -->
          <div :class="msg.isUser ? 'ml-2 ml-auto' : 'ml-2'" style="max-width: 80%">
            <div :class="{
              'bg-gradient-to-r from-blue-600 to-indigo-600 text-white': msg.isUser,
              'bg-gray-50 text-gray-800 border border-gray-100': !msg.isUser && !msg.isError && !msg.isWarning,
              'bg-red-50 text-red-800 border border-red-200': msg.isError,
              'bg-yellow-50 text-yellow-800 border border-yellow-200': msg.isWarning
            }"
                 class="p-4 rounded-2xl rounded-tl-none shadow-sm relative">
              <p class="whitespace-pre-line">{{ msg.content }}</p>

              <!-- 敏感信息标识 -->
              <div v-if="msg.hasSensitiveInfo" class="mt-2 text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded">
                🔒 已脱敏处理
              </div>

              <!-- 消息装饰 -->
              <span v-if="msg.isUser" class="absolute -left-1 top-0 w-2 h-4 bg-blue-600 rounded-tr-full"></span>
              <span v-else-if="msg.isError" class="absolute -right-1 top-0 w-2 h-4 bg-red-50 border-r border-t border-red-200 rounded-tl-full"></span>
              <span v-else-if="msg.isWarning" class="absolute -right-1 top-0 w-2 h-4 bg-yellow-50 border-r border-t border-yellow-200 rounded-tl-full"></span>
              <span v-else class="absolute -right-1 top-0 w-2 h-4 bg-gray-50 border-r border-t border-gray-100 rounded-tl-full"></span>
            </div>
            <div class="text-xs text-gray-400 mt-1 ml-2 flex items-center gap-1">
              <span>{{ new Date(msg.timestamp).toLocaleTimeString() }}</span>
              <span v-if="!msg.isUser && !msg.isError" class="inline-block w-1.5 h-1.5 rounded-full bg-green-500"></span>
              <span v-if="!msg.isUser && !msg.isError" class="text-[10px]">已读</span>
              <span v-if="msg.isError" class="inline-block w-1.5 h-1.5 rounded-full bg-red-500"></span>
              <span v-if="msg.isWarning" class="inline-block w-1.5 h-1.5 rounded-full bg-yellow-500"></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="border-t border-gray-100 p-4 bg-gray-50">
      <div class="flex gap-2">
        <input
            v-model="question"
            @keyup.enter="askQuestion"
            class="flex-1 border border-gray-200 rounded-xl p-3 focus:ring-2 focus:ring-blue-400 focus:border-transparent outline-none transition-all shadow-sm hover:border-gray-300"
            type="text"
            placeholder="请输入您的问题..."
            :disabled="loading"
        />
        <button
            @click="askQuestion"
            class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-5 py-3 rounded-xl hover:opacity-95 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all disabled:opacity-70 disabled:cursor-not-allowed shadow-sm hover:shadow"
            :disabled="loading || !question.trim()"
        >
          <span v-if="loading" class="flex items-center">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            处理中...
          </span>
          <span v-else class="flex items-center gap-1">
            提问
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12z" />
            </svg>
          </span>
        </button>
      </div>

      <!-- 辅助功能区 -->
      <div class="flex items-center gap-4 mt-3 text-gray-500 text-sm">
        <button class="hover:text-blue-600 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
        </button>
        <span class="text-xs text-gray-400">支持药物、疾病名称查询，最多显示5条相关结果</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const question = ref('')
const messages = ref([])
const loading = ref(false)
const chatHistory = ref(null)

// 使用示例问题
const useExample = (text) => {
  question.value = text
}

// 初始化欢迎消息
const initializeChat = () => {
  messages.value.push({
    content: `欢迎使用肝脏疾病药物重定位知识图谱问答系统！\n\n您好，${authStore.user?.username}，我是您的智能助手。请输入您的问题，我将为您提供专业的药物重定位相关信息。`,
    isUser: false,
    timestamp: new Date()
  })
}

// 发送问题
const askQuestion = async () => {
  const q = question.value.trim()
  if (!q || loading.value) return

  // 添加用户消息到聊天记录
  messages.value.push({
    content: q,
    isUser: true,
    timestamp: new Date()
  })

  // 清空输入框并设置加载状态
  question.value = ''
  loading.value = true

  try {
    // 使用认证的API请求
    const response = await authStore.authenticatedRequest('/ask', {
      method: 'POST',
      body: JSON.stringify({ question: q })
    })

    // 添加回答到聊天记录
    messages.value.push({
      content: response.answer || '未能获取到回答，请稍后重试。',
      isUser: false,
      timestamp: new Date(),
      hasSensitiveInfo: response.has_sensitive_info
    })

    // 如果包含敏感信息，显示提示
    if (response.has_sensitive_info) {
      messages.value.push({
        content: '⚠️ 注意：回答中可能包含敏感信息，已进行脱敏处理。',
        isUser: false,
        timestamp: new Date(),
        isWarning: true
      })
    }

  } catch (error) {
    console.error('提问失败:', error)
    
    let errorMessage = '抱歉，处理您的问题时出现了错误。'
    
    if (error.message.includes('401') || error.message.includes('未授权')) {
      errorMessage = '登录已过期，请重新登录。'
    } else if (error.message.includes('403')) {
      errorMessage = '您的查询包含敏感信息，已被系统拒绝。'
    } else if (error.message.includes('400')) {
      errorMessage = '问题格式不正确，请重新输入。'
    }
    
    messages.value.push({
      content: errorMessage,
      isUser: false,
      timestamp: new Date(),
      isError: true
    })
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}


// 滚动到最新消息
const scrollToBottom = () => {
  nextTick(() => {
    const el = document.getElementById('chatHistory')
    if (el) {
      el.scrollTop = el.scrollHeight
    }
  })
}

// 页面加载时初始化
onMounted(() => {
  initializeChat()
})
</script>

<style>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease forwards;
}

#chatHistory::-webkit-scrollbar {
  width: 6px;
}

#chatHistory::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

#chatHistory::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
}

#chatHistory::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>