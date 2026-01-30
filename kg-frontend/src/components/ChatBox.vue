<template>
  <div class="w-full bg-white rounded-2xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-xl border border-gray-100">
    <!-- 对话历史区域 -->
    <div class="p-6 max-h-[500px] overflow-y-auto space-y-6" id="chatHistory">
      <!-- 示例问题提示 -->
      <div v-if="messages.length === 0" class="text-center text-gray-400 py-12 bg-gradient-to-b from-gray-50 to-transparent rounded-xl mx-4">
        <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-blue-600">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
          </svg>
        </div>
        <p class="font-medium">请输入您的问题，例如：</p>
        <div class="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 px-4">
          <button
              @click="useExample('我有头痛和发热症状，可能是什么疾病？')"
              class="bg-blue-50 hover:bg-blue-100 text-blue-700 px-4 py-3 rounded-lg text-sm transition-all hover:shadow-md transform hover:-translate-y-1"
          >
            我有头痛和发热症状，可能是什么疾病？
          </button>
          <button
              @click="useExample('高血压患者应该注意什么？')"
              class="bg-blue-50 hover:bg-blue-100 text-blue-700 px-4 py-3 rounded-lg text-sm transition-all hover:shadow-md transform hover:-translate-y-1"
          >
            高血压患者应该注意什么？
          </button>
          <button
              @click="useExample('阿司匹林有哪些副作用？')"
              class="bg-blue-50 hover:bg-blue-100 text-blue-700 px-4 py-3 rounded-lg text-sm transition-all hover:shadow-md transform hover:-translate-y-1"
          >
            阿司匹林有哪些副作用？
          </button>
          <button
              @click="useExample('糖尿病患者的饮食建议有哪些？')"
              class="bg-blue-50 hover:bg-blue-100 text-blue-700 px-4 py-3 rounded-lg text-sm transition-all hover:shadow-md transform hover:-translate-y-1"
          >
            糖尿病患者的饮食建议有哪些？
          </button>
        </div>
      </div>

      <!-- 消息列表 -->
      <div v-for="(msg, index) in messages" :key="index" class="animate-fadeIn mx-4">
        <!-- 小智头像 -->
        <div v-if="!msg.isUser" class="flex items-start gap-3">
          <div class="w-9 h-9 rounded-full bg-gradient-to-r from-gray-200 to-gray-100 flex items-center justify-center text-gray-700 text-sm shadow-sm">
            小兔智
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
const localQA = [
  {
    keywords: ['头痛', '发热', '症状', '疾病'],
    question: '我有头痛和发热症状，可能是什么疾病？',
    answer: '头痛和发热是常见的症状组合，可能的疾病包括：\n\n1. 感冒或流感：最常见的原因，通常伴有鼻塞、咳嗽等症状\n2. 细菌感染：如扁桃体炎、肺炎等\n3. 病毒感染：如病毒性脑炎（较严重）\n4. 偏头痛：可能伴有轻微发热\n\n建议：\n多休息，多喝水\n如果发热超过38.5°C或症状持续加重，请及时就医\n如出现剧烈头痛、颈部僵硬等症状，应立即就医'
  },
  {
    keywords: ['高血压', '注意', '患者'],
    question: '高血压患者应该注意什么？',
    answer: '高血压患者需要注意以下几个方面：\n\n饮食管理：\n低盐饮食（每日盐摄入量<6g）\n多吃新鲜蔬菜水果\n控制饱和脂肪摄入\n限制酒精摄入\n\n生活方式：\n规律运动（每周至少150分钟中等强度运动）\n控制体重\n戒烟\n保证充足睡眠\n学会压力管理\n\n药物治疗：\n按医嘱规律服药\n不可随意停药或减量\n定期监测血压\n\n定期检查：\n每月测量血压\n定期检查心、脑、肾功能'
  },
  {
    keywords: ['阿司匹林', '副作用'],
    question: '阿司匹林有哪些副作用？',
    answer: '阿司匹林的主要副作用包括：\n\n消化系统：\n胃肠道刺激、胃痛\n消化性溃疡\n胃肠道出血\n恶心、呕吐\n\n血液系统：\n出血倾向增加\n血小板功能异常\n凝血时间延长\n\n过敏反应：\n皮疹、荨麻疹\n哮喘发作（阿司匹林哮喘）\n严重过敏反应\n\n其他：\n耳鸣、听力下降\n头晕、头痛\n肝功能异常（大剂量时）\n\n注意事项：\n有胃溃疡史者慎用\n孕妇、哺乳期妇女慎用\n与其他抗凝药物联用需谨慎'
  },
  {
    keywords: ['糖尿病', '饮食', '建议'],
    question: '糖尿病患者的饮食建议有哪些？',
    answer: '糖尿病患者的饮食建议：\n\n主食选择：\n选择低升糖指数食物\n粗粮代替精米白面\n控制总量，少食多餐\n\n蛋白质：\n优质蛋白：鱼类、瘦肉、蛋类、豆制品\n每日蛋白质占总热量15-20%\n\n脂肪：\n选择不饱和脂肪酸\n限制饱和脂肪和反式脂肪\n每日脂肪占总热量<30%\n\n蔬菜水果：\n多吃绿叶蔬菜\n水果选择低糖品种，控制量\n避免果汁\n\n饮食原则：\n定时定量\n少食多餐\n控制总热量\n监测血糖变化\n\n禁忌食物：\n含糖饮料、糖果\n油炸食品\n高盐高脂食物'
  },
  {
    keywords: ['感冒', '治疗', '药物'],
    question: '感冒了应该怎么治疗？',
    answer: '感冒的治疗建议：\n\n一般治疗：\n多休息，保证充足睡眠\n多喝温开水\n保持室内空气流通\n清淡饮食\n\n症状缓解：\n发热：物理降温，必要时服用退热药\n鼻塞：生理盐水冲洗鼻腔\n咳嗽：蜂蜜水、梨汤等\n咽痛：温盐水漱口\n\n药物治疗：\n对症治疗为主\n退热药：对乙酰氨基酚、布洛芬\n抗病毒药：奥司他韦（流感）\n避免滥用抗生素\n\n就医指征：\n发热超过3天\n出现呼吸困难\n剧烈头痛、颈部僵硬\n症状持续加重\n\n预防措施：\n勤洗手\n避免接触患者\n增强体质'
  },
  {
    keywords: ['咳嗽', '原因', '治疗'],
    question: '咳嗽的原因有哪些？',
    answer: '咳嗽的常见原因：\n\n感染性原因：\n病毒感染：感冒、流感\n细菌感染：肺炎、支气管炎\n支原体、衣原体感染\n\n非感染性原因：\n过敏性咳嗽\n哮喘\n胃食管反流\n药物性咳嗽（如ACEI类降压药）\n慢性阻塞性肺疾病\n\n环境因素：\n空气污染\n吸烟\n粉尘刺激\n温度变化\n\n治疗原则：\n针对病因治疗\n干咳：可用镇咳药\n有痰咳嗽：用祛痰药\n避免刺激因素\n\n就医指征：\n咳嗽超过2周\n咳血\n伴有发热、胸痛\n呼吸困难'
  },
  {
    keywords: ['失眠', '睡眠', '改善'],
    question: '失眠怎么办？',
    answer: '改善失眠的方法：\n\n睡眠卫生：\n规律作息，固定睡眠时间\n睡前2小时避免大量进食\n避免睡前饮用咖啡、茶、酒精\n创造舒适的睡眠环境\n\n放松技巧：\n深呼吸练习\n渐进性肌肉放松\n冥想、瑜伽\n听轻柔音乐\n\n生活方式调整：\n规律运动（但避免睡前剧烈运动）\n控制白天小睡时间\n减少电子设备使用\n管理压力和焦虑\n\n药物治疗：\n短期使用安眠药\n需在医生指导下使用\n避免长期依赖\n\n就医指征：\n失眠持续超过1个月\n严重影响日常生活\n伴有抑郁、焦虑症状'
  },
  {
    keywords: ['腹痛', '肚子疼', '原因'],
    question: '腹痛的常见原因有哪些？',
    answer: '腹痛的常见原因：\n\n消化系统疾病：\n胃炎、胃溃疡\n肠炎、肠易激综合征\n胆囊炎、胆石症\n胰腺炎\n阑尾炎\n\n妇科疾病（女性）：\n痛经\n卵巢囊肿\n盆腔炎\n异位妊娠\n\n泌尿系统：\n肾结石\n尿路感染\n膀胱炎\n\n其他原因：\n肠梗阻\n腹主动脉瘤\n心肌梗死（上腹痛）\n\n紧急就医指征：\n剧烈腹痛\n伴有发热、呕吐\n腹部僵硬\n便血、黑便\n休克症状\n\n一般处理：\n轻微腹痛可观察\n避免盲目使用止痛药\n清淡饮食\n注意休息'
  }
]

// 使用示例问题
const useExample = (text) => {
  question.value = text
}

const findSmallTalkAnswer = (userQuestion) => {
  const trimmed = userQuestion.trim()
  const lower = trimmed.toLowerCase()
  if (trimmed === '你好' || trimmed === '您好' || trimmed === '在吗' || lower === 'hello' || lower === 'hi') {
    return '你好！我是智慧医疗知识助手。\n\n你可以这样问我：\n1. 疾病相关："糖尿病有什么症状？"\n2. 症状分析："头痛发热可能是什么？"\n3. 药物咨询："阿司匹林有哪些副作用？"\n4. 健康建议："高血压患者要注意什么？"'
  }

  if (trimmed === '谢谢' || trimmed === '感谢' || trimmed === '多谢') {
    return '不客气！你可以继续描述：症状出现多久、是否发热、年龄/既往病史等，我会结合知识图谱给你更完整的结果。'
  }

  return null
}

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
  
  // 模糊匹配常见问题
  if (questionLower.includes('头痛') || questionLower.includes('头疼')) {
    return '头痛的常见原因包括：\n\n1. 紧张性头痛：最常见，由压力、疲劳引起\n2. 偏头痛：一侧搏动性疼痛，可能伴有恶心\n3. 颈椎病：颈部僵硬引起的头痛\n4. 高血压：血压升高时的头痛\n5. 感冒发热：病毒感染引起\n\n缓解方法：\n充分休息\n按摩太阳穴\n热敷或冷敷\n如持续严重，请就医检查'
  }
  
  if (questionLower.includes('发烧') || questionLower.includes('发热')) {
    return '发热的处理建议：\n\n物理降温：\n温水擦浴\n多喝水\n适当减少衣物\n保持室内通风\n\n药物降温：\n体温>38.5°C时可服用退热药\n成人：对乙酰氨基酚、布洛芬\n儿童：避免使用阿司匹林\n\n就医指征：\n体温>39°C\n发热超过3天\n伴有剧烈头痛、呼吸困难\n婴幼儿发热\n\n注意事项：\n监测体温变化\n观察其他症状\n充分休息'
  }
  
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
    const smallTalkAnswer = findSmallTalkAnswer(q)
    if (smallTalkAnswer) {
      // 模拟加载延迟，提供更真实的体验
      await new Promise(resolve => setTimeout(resolve, 800))
      
      // 添加本地答案到聊天记录
      messages.value.push({
        content: smallTalkAnswer,
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
      const allowLocalMedical = authStore.isDemoMode
      const localAnswer = allowLocalMedical ? findLocalAnswer(q) : null

      if (localAnswer) {
        await new Promise(resolve => setTimeout(resolve, 800))

        messages.value.push({
          content: localAnswer,
          isUser: false,
          timestamp: new Date(),
          isLocal: true
        })

        messages.value.push({
          content: '💡 以上信息仅供参考。如有严重症状，请及时就医。',
          isUser: false,
          timestamp: new Date(),
          isInfo: true
        })
      } else {
        // 走后端API（真实知识图谱问答）
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
          console.log('后端API不可用:', backendError)

          const msg = (backendError && backendError.message) ? backendError.message : ''
          if (msg.includes('用户未登录') || msg.includes('缺少认证令牌') || msg.includes('未授权')) {
            messages.value.push({
              content: '请先登录后再提问（系统会从知识图谱中查询并返回结果）。',
              isUser: false,
              timestamp: new Date(),
              isWarning: true
            })
          } else {
            messages.value.push({
              content: '后端知识图谱问答服务暂时不可用，请确认后端(5000)与Neo4j(7687)正常运行后重试。',
              isUser: false,
              timestamp: new Date(),
              isError: true
            })
          }
        }
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