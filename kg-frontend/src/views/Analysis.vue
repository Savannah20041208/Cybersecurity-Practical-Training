<template>
  <div class="p-6 md:p-8 bg-gray-50 min-h-screen">
    <div class="max-w-7xl mx-auto">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">我的健康分析</h1>
        <p class="text-gray-600">个人健康信息记录、分析与管理平台</p>
      </div>

      <!-- 健康概览卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- 症状记录 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"></path>
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-gray-900">症状记录</h3>
                <p class="text-sm text-gray-500">本周记录</p>
              </div>
            </div>
          </div>
          <div class="text-2xl font-bold text-gray-900 mb-1">{{ symptomRecords.length }}</div>
          <p class="text-sm text-gray-500">条症状记录</p>
        </div>

        <!-- 用药提醒 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 7.172V5L8 4z"></path>
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-gray-900">用药提醒</h3>
                <p class="text-sm text-gray-500">今日待服用</p>
              </div>
            </div>
          </div>
          <div class="text-2xl font-bold text-gray-900 mb-1">{{ todayMedications.length }}</div>
          <p class="text-sm text-gray-500">种药物</p>
        </div>

        <!-- 就医提醒 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3a2 2 0 012-2h4a2 2 0 012 2v4m-6 4v10m6-10v10m-6 0h6"></path>
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-gray-900">就医提醒</h3>
                <p class="text-sm text-gray-500">近期安排</p>
              </div>
            </div>
          </div>
          <div class="text-2xl font-bold text-gray-900 mb-1">{{ upcomingAppointments.length }}</div>
          <p class="text-sm text-gray-500">个预约</p>
        </div>

        <!-- 健康评分 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-gray-900">健康评分</h3>
                <p class="text-sm text-gray-500">综合评估</p>
              </div>
            </div>
          </div>
          <div class="text-2xl font-bold text-gray-900 mb-1">{{ healthScore }}/100</div>
          <p class="text-sm" :class="healthScore >= 80 ? 'text-green-500' : healthScore >= 60 ? 'text-yellow-500' : 'text-red-500'">
            {{ healthScore >= 80 ? '良好' : healthScore >= 60 ? '一般' : '需要关注' }}
          </p>
        </div>
      </div>

      <!-- 主要功能区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <!-- 症状记录 -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-semibold text-gray-800">症状记录</h3>
              <button @click="showAddSymptom = true" class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors">
                记录症状
              </button>
            </div>
            
            <!-- 症状记录列表 -->
            <div class="space-y-4">
              <div v-for="symptom in symptomRecords" :key="symptom.id" class="border border-gray-200 rounded-lg p-4">
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <h4 class="font-medium text-gray-900">{{ symptom.name }}</h4>
                    <p class="text-sm text-gray-600 mt-1">{{ symptom.description }}</p>
                    <div class="flex items-center gap-4 mt-2">
                      <span class="text-xs text-gray-500">{{ symptom.date }}</span>
                      <span class="text-xs px-2 py-1 rounded-full" :class="getSeverityClass(symptom.severity)">
                        {{ symptom.severity }}
                      </span>
                    </div>
                  </div>
                  <div class="flex gap-2">
                    <button @click="editSymptom(symptom)" class="text-blue-600 hover:text-blue-800">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                      </svg>
                    </button>
                    <button @click="deleteSymptom(symptom.id)" class="text-red-600 hover:text-red-800">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
              
              <div v-if="symptomRecords.length === 0" class="text-center py-8 text-gray-500">
                <svg class="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <p>暂无症状记录</p>
                <p class="text-sm mt-1">点击"记录症状"开始记录您的健康状况</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 侧边栏 -->
        <div class="space-y-6">
          <!-- 今日提醒 -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">今日提醒</h3>
            
            <!-- 用药提醒 -->
            <div class="mb-4">
              <h4 class="font-medium text-gray-700 mb-2">用药提醒</h4>
              <div class="space-y-2">
                <div v-for="med in todayMedications" :key="med.id" class="flex items-center justify-between p-2 bg-blue-50 rounded-lg">
                  <div>
                    <span class="text-sm font-medium text-blue-900">{{ med.name }}</span>
                    <span class="text-xs text-blue-600 block">{{ med.time }}</span>
                  </div>
                  <button @click="markMedicationTaken(med.id)" class="text-blue-600 hover:text-blue-800">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                  </button>
                </div>
                <div v-if="todayMedications.length === 0" class="text-sm text-gray-500 text-center py-2">
                  今日无用药安排
                </div>
              </div>
            </div>
            
            <!-- 就医提醒 -->
            <div>
              <h4 class="font-medium text-gray-700 mb-2">就医提醒</h4>
              <div class="space-y-2">
                <div v-for="appointment in upcomingAppointments" :key="appointment.id" class="p-2 bg-green-50 rounded-lg">
                  <div class="text-sm font-medium text-green-900">{{ appointment.doctor }}</div>
                  <div class="text-xs text-green-600">{{ appointment.date }} {{ appointment.time }}</div>
                  <div class="text-xs text-green-600">{{ appointment.department }}</div>
                </div>
                <div v-if="upcomingAppointments.length === 0" class="text-sm text-gray-500 text-center py-2">
                  近期无就医安排
                </div>
              </div>
            </div>
          </div>
          
          <!-- 健康建议 -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">健康建议</h3>
            <div class="space-y-3">
              <div v-for="suggestion in healthSuggestions" :key="suggestion.id" class="p-3 bg-yellow-50 rounded-lg">
                <div class="flex items-start gap-2">
                  <svg class="w-4 h-4 text-yellow-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <div>
                    <p class="text-sm font-medium text-yellow-900">{{ suggestion.title }}</p>
                    <p class="text-xs text-yellow-700 mt-1">{{ suggestion.content }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 健康统计图表 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- 症状趋势图 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-semibold text-gray-800">症状趋势</h3>
            <select v-model="chartTimeRange" class="px-3 py-1 text-sm border border-gray-300 rounded-lg">
              <option value="week">最近一周</option>
              <option value="month">最近一月</option>
              <option value="quarter">最近三月</option>
            </select>
          </div>
          <div class="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <div class="text-center text-gray-500">
              <svg class="w-16 h-16 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              <p>症状趋势图表</p>
              <p class="text-sm mt-1">记录更多症状后显示趋势</p>
            </div>
          </div>
        </div>

        <!-- 用药统计 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-semibold text-gray-800">用药统计</h3>
            <button @click="showAddMedication = true" class="px-3 py-1 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600">
              添加用药
            </button>
          </div>
          <div class="space-y-4">
            <div v-for="med in medications" :key="med.id" class="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <div>
                <h4 class="font-medium text-blue-900">{{ med.name }}</h4>
                <p class="text-sm text-blue-600">{{ med.dosage }} - {{ med.frequency }}</p>
              </div>
              <div class="text-right">
                <div class="text-sm font-medium text-blue-900">{{ med.adherence }}%</div>
                <div class="text-xs text-blue-600">依从性</div>
              </div>
            </div>
            <div v-if="medications.length === 0" class="text-center py-8 text-gray-500">
              <svg class="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 7.172V5L8 4z"></path>
              </svg>
              <p>暂无用药记录</p>
              <p class="text-sm mt-1">点击"添加用药"开始管理您的用药</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 快速操作 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <button @click="showAddAppointment = true" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 text-left hover:shadow-md transition-shadow">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3a2 2 0 012-2h4a2 2 0 012 2v4m-6 4v10m6-10v10m-6 0h6"></path>
              </svg>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900">预约就医</h3>
              <p class="text-sm text-gray-600">安排医生预约</p>
            </div>
          </div>
        </button>

        <button @click="exportHealthData" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 text-left hover:shadow-md transition-shadow">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900">导出数据</h3>
              <p class="text-sm text-gray-600">下载健康报告</p>
            </div>
          </div>
        </button>

        <button @click="showHealthInsights = true" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 text-left hover:shadow-md transition-shadow">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
              </svg>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900">健康洞察</h3>
              <p class="text-sm text-gray-600">AI分析建议</p>
            </div>
          </div>
        </button>
      </div>
      
      <!-- 模态框 -->
      <!-- 添加症状模态框 -->
      <div v-if="showAddSymptom" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-xl shadow-xl max-w-md w-full mx-4">
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">记录症状</h3>
              <button @click="showAddSymptom = false" class="text-gray-400 hover:text-gray-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <form @submit.prevent="addSymptom">
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">症状名称</label>
                  <input v-model="newSymptom.name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent" placeholder="例如：头痛">
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">症状描述</label>
                  <textarea v-model="newSymptom.description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent" placeholder="详细描述症状情况..."></textarea>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">严重程度</label>
                  <select v-model="newSymptom.severity" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent">
                    <option value="">请选择</option>
                    <option value="轻微">轻微</option>
                    <option value="中等">中等</option>
                    <option value="严重">严重</option>
                  </select>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">发生时间</label>
                  <input v-model="newSymptom.date" type="datetime-local" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent">
                </div>
              </div>
              
              <div class="flex gap-3 mt-6">
                <button type="button" @click="showAddSymptom = false" class="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
                  取消
                </button>
                <button type="submit" class="flex-1 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors">
                  保存
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- 添加用药模态框 -->
      <div v-if="showAddMedication" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-xl shadow-xl max-w-md w-full mx-4">
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">添加用药</h3>
              <button @click="showAddMedication = false" class="text-gray-400 hover:text-gray-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <form @submit.prevent="addMedication">
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">药物名称</label>
                  <input v-model="newMedication.name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="例如：阿司匹林">
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">剂量</label>
                  <input v-model="newMedication.dosage" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="例如：100mg">
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">服用频率</label>
                  <select v-model="newMedication.frequency" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    <option value="">请选择</option>
                    <option value="每日一次">每日一次</option>
                    <option value="每日两次">每日两次</option>
                    <option value="每日三次">每日三次</option>
                    <option value="按需服用">按需服用</option>
                  </select>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">服用时间</label>
                  <input v-model="newMedication.time" type="time" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                </div>
              </div>
              
              <div class="flex gap-3 mt-6">
                <button type="button" @click="showAddMedication = false" class="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
                  取消
                </button>
                <button type="submit" class="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                  保存
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- 添加预约模态框 -->
      <div v-if="showAddAppointment" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-xl shadow-xl max-w-md w-full mx-4">
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">预约就医</h3>
              <button @click="showAddAppointment = false" class="text-gray-400 hover:text-gray-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <form @submit.prevent="addAppointment">
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">医生姓名</label>
                  <input v-model="newAppointment.doctor" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent" placeholder="例如：张医生">
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">科室</label>
                  <input v-model="newAppointment.department" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent" placeholder="例如：内科">
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">预约日期</label>
                  <input v-model="newAppointment.date" type="date" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent">
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">预约时间</label>
                  <input v-model="newAppointment.time" type="time" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent">
                </div>
              </div>
              
              <div class="flex gap-3 mt-6">
                <button type="button" @click="showAddAppointment = false" class="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
                  取消
                </button>
                <button type="submit" class="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors">
                  保存
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 响应式数据
const showAddSymptom = ref(false)
const showAddMedication = ref(false)
const showAddAppointment = ref(false)
const showHealthInsights = ref(false)
const chartTimeRange = ref('week')

// 症状记录相关
const symptomRecords = ref([
  {
    id: 1,
    name: '头痛',
    description: '持续性头痛，主要在太阳穴附近',
    severity: '中等',
    date: '2024-01-09 14:30',
    timestamp: new Date('2024-01-09 14:30')
  },
  {
    id: 2,
    name: '失眠',
    description: '难以入睡，夜间易醒',
    severity: '轻微',
    date: '2024-01-08 23:00',
    timestamp: new Date('2024-01-08 23:00')
  }
])

const newSymptom = ref({
  name: '',
  description: '',
  severity: '',
  date: ''
})

// 用药管理相关
const medications = ref([
  {
    id: 1,
    name: '阿司匹林',
    dosage: '100mg',
    frequency: '每日一次',
    time: '08:00',
    adherence: 95
  },
  {
    id: 2,
    name: '维生素D',
    dosage: '1000IU',
    frequency: '每日一次',
    time: '09:00',
    adherence: 88
  }
])

const newMedication = ref({
  name: '',
  dosage: '',
  frequency: '',
  time: ''
})

// 今日用药提醒
const todayMedications = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return medications.value.map(med => ({
    ...med,
    taken: false
  }))
})

// 预约管理相关
const upcomingAppointments = ref([
  {
    id: 1,
    doctor: '张医生',
    department: '心内科',
    date: '2024-01-15',
    time: '09:30'
  }
])

const newAppointment = ref({
  doctor: '',
  department: '',
  date: '',
  time: ''
})

// 健康建议
const healthSuggestions = ref([
  {
    id: 1,
    title: '规律作息',
    content: '建议每天保持7-8小时的睡眠，有助于缓解头痛症状'
  },
  {
    id: 2,
    title: '适量运动',
    content: '每周进行3-4次中等强度运动，有助于改善整体健康状况'
  },
  {
    id: 3,
    title: '定期复查',
    content: '建议每3个月进行一次健康检查，监测各项指标'
  }
])

// 健康评分
const healthScore = computed(() => {
  let score = 80
  
  // 根据症状记录调整评分
  const recentSymptoms = symptomRecords.value.filter(symptom => {
    const daysDiff = (new Date() - symptom.timestamp) / (1000 * 60 * 60 * 24)
    return daysDiff <= 7
  })
  
  score -= recentSymptoms.length * 5
  
  // 根据用药依从性调整评分
  const avgAdherence = medications.value.reduce((sum, med) => sum + med.adherence, 0) / medications.value.length
  score = score * (avgAdherence / 100)
  
  return Math.max(0, Math.min(100, Math.round(score)))
})

// 方法
const getSeverityClass = (severity) => {
  switch (severity) {
    case '轻微':
      return 'bg-green-100 text-green-800'
    case '中等':
      return 'bg-yellow-100 text-yellow-800'
    case '严重':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const addSymptom = () => {
  const newId = Math.max(...symptomRecords.value.map(s => s.id), 0) + 1
  symptomRecords.value.unshift({
    id: newId,
    name: newSymptom.value.name,
    description: newSymptom.value.description,
    severity: newSymptom.value.severity,
    date: new Date(newSymptom.value.date).toLocaleString('zh-CN'),
    timestamp: new Date(newSymptom.value.date)
  })
  
  // 重置表单
  newSymptom.value = {
    name: '',
    description: '',
    severity: '',
    date: ''
  }
  
  showAddSymptom.value = false
}

const editSymptom = (symptom) => {
  // 实现编辑功能
  console.log('编辑症状:', symptom)
}

const deleteSymptom = (id) => {
  symptomRecords.value = symptomRecords.value.filter(s => s.id !== id)
}

const addMedication = () => {
  const newId = Math.max(...medications.value.map(m => m.id), 0) + 1
  medications.value.push({
    id: newId,
    name: newMedication.value.name,
    dosage: newMedication.value.dosage,
    frequency: newMedication.value.frequency,
    time: newMedication.value.time,
    adherence: 100
  })
  
  // 重置表单
  newMedication.value = {
    name: '',
    dosage: '',
    frequency: '',
    time: ''
  }
  
  showAddMedication.value = false
}

const markMedicationTaken = (id) => {
  console.log('标记用药完成:', id)
  // 实现标记用药完成的逻辑
}

const addAppointment = () => {
  const newId = Math.max(...upcomingAppointments.value.map(a => a.id), 0) + 1
  upcomingAppointments.value.push({
    id: newId,
    doctor: newAppointment.value.doctor,
    department: newAppointment.value.department,
    date: newAppointment.value.date,
    time: newAppointment.value.time
  })
  
  // 重置表单
  newAppointment.value = {
    doctor: '',
    department: '',
    date: '',
    time: ''
  }
  
  showAddAppointment.value = false
}

const exportHealthData = () => {
  // 实现导出健康数据功能
  const data = {
    symptoms: symptomRecords.value,
    medications: medications.value,
    appointments: upcomingAppointments.value,
    healthScore: healthScore.value,
    exportDate: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `health-data-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  // 设置默认的症状记录时间
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  newSymptom.value.date = now.toISOString().slice(0, 16)
})
</script>

<style scoped>
.transition-all {
  transition: all 0.2s ease-in-out;
}
</style>
