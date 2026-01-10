<template>
  <div class="w-full bg-white rounded-2xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-xl border border-gray-100">
    <!-- 对话历史区域 -->
    <div class="p-6 max-h-[500px] overflow-y-auto space-y-6" id="chatHistory">
      <!-- 空状态提示 -->
      <div v-if="messages.length === 0" class="text-center text-gray-400 py-12 bg-gradient-to-b from-gray-50 to-transparent rounded-xl mx-4">
        <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-blue-600">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
          </svg>
        </div>
        <p class="font-medium">请输入您的医疗健康相关问题</p>
        <p class="text-sm mt-2">我将为您提供专业的医疗知识问答服务</p>
      </div>

      <!-- 消息列表 -->
      <div v-for="(msg, index) in messages" :key="index" class="animate-fadeIn mx-4">
        <!-- 小智头像 -->
        <div v-if="!msg.isUser" class="flex items-start gap-3">
          <div class="w-9 h-9 rounded-full bg-gradient-to-r from-gray-200 to-gray-100 flex items-center justify-center text-gray-700 text-sm shadow-sm">
            小智
          </div>
          <div class="ml-2" style="max-width: 100%">
            <div class="flex-1 max-w-[100%]">
              <div :class="[
                'rounded-2xl px-4 py-3 shadow-sm inline-block',
                msg.isError ? 'bg-red-50 border border-red-200' :
                msg.isWarning ? 'bg-yellow-50 border border-yellow-200' :
                msg.isInfo ? 'bg-blue-50 border border-blue-200' :
                msg.isLocal ? 'bg-green-50 border border-green-200' :
                msg.isGeneral ? 'bg-purple-50 border border-purple-200' :
                'bg-gray-100'
              ]">
                <div :class="[
                  'whitespace-pre-wrap break-words leading-relaxed',
                  msg.isError ? 'text-red-800' :
                  msg.isWarning ? 'text-yellow-800' :
                  msg.isInfo ? 'text-blue-800' :
                  msg.isLocal ? 'text-green-800' :
                  msg.isGeneral ? 'text-purple-800' :
                  'text-gray-800'
                ]">{{ msg.content }}</div>
                <div :class="[
                  'text-xs mt-2 flex items-center gap-1',
                  msg.isError ? 'text-red-500' :
                  msg.isWarning ? 'text-yellow-500' :
                  msg.isInfo ? 'text-blue-500' :
                  msg.isLocal ? 'text-green-500' :
                  msg.isGeneral ? 'text-purple-500' :
                  'text-gray-500'
                ]">
                  <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"></path>
                  </svg>
                  {{ formatTime(msg.timestamp) }}
                  <span v-if="msg.isInfo" class="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">提示</span>
                  <span v-if="msg.isWarning" class="ml-2 text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">警告</span>
                  <span v-if="msg.isError" class="ml-2 text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">错误</span>
                </div>
              </div>
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

        <!-- 用户消息（无头像） -->
        <div v-else class="flex justify-end">
          <div class="text-right" style="max-width: 100%">
            <div class="inline-block max-w-[100%]">
              <div class="rounded-2xl px-4 py-3 shadow-sm bg-blue-600 text-white">
                <div class="whitespace-pre-wrap break-words leading-relaxed text-white">{{ msg.content }}</div>
                <div class="text-xs mt-2 flex items-center gap-1 justify-end text-blue-100">
                  <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"></path>
                  </svg>
                  {{ formatTime(msg.timestamp) }}
                </div>
              </div>
            </div>
            <div class="text-xs text-gray-400 mt-1 mr-2">
              <span>{{ new Date(msg.timestamp).toLocaleTimeString() }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="border-t border-gray-100 p-4 bg-gray-50">
      <div class="flex gap-2 max-w-full">
        <input
            v-model="question"
            @keyup.enter="handleAskQuestion"
            class="flex-1 border border-gray-200 rounded-xl p-3 focus:ring-2 focus:ring-blue-400 focus:border-transparent outline-none transition-all shadow-sm hover:border-gray-300"
            type="text"
            placeholder="请输入您的问题..."
            :disabled="loading"
        />
        <button
            @click="handleAskQuestion"
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

// 本地问答数据库
const localQA = []


// 本地问答匹配函数
const findLocalAnswer = (userQuestion) => {
  const questionLower = userQuestion.toLowerCase()
  
  // 精确匹配预设问题
  const exactMatch = localQA.find(qa => qa.question === userQuestion)
  if (exactMatch) return exactMatch.answer
  
  // 关键词匹配
  const keywordMatch = localQA.find(qa => 
    qa.keywords.some(keyword => questionLower.includes(keyword.toLowerCase()))
  )
  if (keywordMatch) return keywordMatch.answer
  
  return null
}

// 初始化欢迎消息
const initializeChat = () => {
  messages.value.push({
    content: `欢迎使用智慧医疗知识服务平台！\n\n您好，${authStore.user?.username}，我是您的智能医疗助手。请输入您的问题，我将为您提供专业的医疗知识问答服务。`,
    isUser: false,
    timestamp: new Date()
  })
}

// 处理提问按钮点击
const handleAskQuestion = () => {
  console.log('按钮被点击了！')
  console.log('当前问题内容:', question.value)
  console.log('问题长度:', question.value.length)
  console.log('trim后长度:', question.value.trim().length)
  console.log('loading状态:', loading.value)
  console.log('按钮是否被禁用:', loading.value || !question.value.trim())
  
  // 如果按钮被禁用，给用户提示
  if (loading.value) {
    console.log('正在处理中，请稍候...')
    return
  }
  
  if (!question.value.trim()) {
    console.log('请输入问题内容')
    // 可以在这里添加用户提示
    return
  }
  
  askQuestion()
}

// 发送问题
const askQuestion = async () => {
  const q = question.value.trim()
  console.log('提问函数被调用，问题内容:', q)
  console.log('loading状态:', loading.value)
  
  if (!q || loading.value) {
    console.log('提问被阻止：', !q ? '问题为空' : '正在加载中')
    return
  }

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
    // 首先尝试本地问答匹配
    const localAnswer = findLocalAnswer(q)
    
    if (localAnswer) {
      // 模拟加载延迟，提供更真实的体验
      await new Promise(resolve => setTimeout(resolve, 800))
      
      // 添加本地答案到聊天记录
      messages.value.push({
        content: localAnswer,
        isUser: false,
        timestamp: new Date(),
        isLocal: true
      })
      
      // 添加提示信息
      messages.value.push({
        content: '💡 以上信息仅供参考。如有严重症状，请及时就医。',
        isUser: false,
        timestamp: new Date(),
        isInfo: true
      })
      
    } else {
      // 本地找不到答案，尝试后端API
      try {
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
        
      } catch (backendError) {
        console.log('后端API不可用，提供通用回答:', backendError)
        
        // 后端不可用时的通用回答
        messages.value.push({
          content: `很抱歉，我暂时无法为您提供关于"${q}"的详细信息。\n\n建议您：\n\n1. **咨询专业医生**：获得最准确的诊断和建议\n2. **查阅权威医疗资料**：如医学教科书、权威医疗网站\n3. **寻求第二意见**：重要健康问题可咨询多位专家\n\n如果是紧急情况，请立即就医或拨打急救电话。`,
          isUser: false,
          timestamp: new Date(),
          isGeneral: true
        })
      }
    }

  } catch (error) {
    console.error('问答处理失败:', error)
    
    messages.value.push({
      content: '抱歉，系统暂时出现问题，请稍后重试。如有紧急情况，请及时就医。',
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


// 格式化时间显示
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
  })
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