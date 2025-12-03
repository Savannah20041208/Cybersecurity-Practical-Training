<template>
  <div class="p-6 md:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">分析页面</h1>
        <p class="text-gray-600">可视化展示药物-疾病重定位结果分析、统计图表</p>
      </div>

      <!-- 控制面板 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <div class="flex flex-wrap gap-4 items-center">
          <div class="flex gap-2">
            <select v-model="selectedAnalysisType" @change="updateAnalysis" class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
              <option value="repositioning">药物重定位分析</option>
              <option value="network">网络分析</option>
              <option value="pathway">通路分析</option>
              <option value="statistics">统计分析</option>
            </select>
            
            <select v-model="selectedTimeRange" @change="updateAnalysis" class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
              <option value="all">全部时间</option>
              <option value="recent">最近一年</option>
              <option value="2024">2024年</option>
              <option value="2023">2023年</option>
            </select>
          </div>
          
          <div class="flex gap-2 ml-auto">
            <button
              @click="exportAnalysis"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              导出报告
            </button>
            
            <button
              @click="refreshData"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              刷新数据
            </button>
          </div>
        </div>
      </div>

      <!-- 概览统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">总药物数量</p>
              <p class="text-2xl font-bold text-gray-900">{{ statistics.totalDrugs }}</p>
              <p class="text-xs text-green-600 mt-1">↑ 12% 较上月</p>
            </div>
            <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">疾病数量</p>
              <p class="text-2xl font-bold text-gray-900">{{ statistics.totalDiseases }}</p>
              <p class="text-xs text-green-600 mt-1">↑ 8% 较上月</p>
            </div>
            <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">重定位机会</p>
              <p class="text-2xl font-bold text-gray-900">{{ statistics.repositioningOpportunities }}</p>
              <p class="text-xs text-blue-600 mt-1">↑ 25% 较上月</p>
            </div>
            <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">成功率</p>
              <p class="text-2xl font-bold text-gray-900">{{ statistics.successRate }}%</p>
              <p class="text-xs text-green-600 mt-1">↑ 3% 较上月</p>
            </div>
            <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z"></path>
                <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- 主要分析图表 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- 药物重定位成功率趋势 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-800">重定位成功率趋势</h3>
            <div class="flex gap-2">
              <button class="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">月度</button>
              <button class="text-xs px-2 py-1 text-gray-600 hover:bg-gray-100 rounded">季度</button>
            </div>
          </div>
          <div class="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
            <!-- 模拟折线图 -->
            <svg width="100%" height="100%" viewBox="0 0 400 200" class="text-blue-600">
              <polyline
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                points="20,160 60,140 100,120 140,100 180,90 220,85 260,80 300,75 340,70 380,65"
              />
              <circle cx="20" cy="160" r="3" fill="currentColor" />
              <circle cx="60" cy="140" r="3" fill="currentColor" />
              <circle cx="100" cy="120" r="3" fill="currentColor" />
              <circle cx="140" cy="100" r="3" fill="currentColor" />
              <circle cx="180" cy="90" r="3" fill="currentColor" />
              <circle cx="220" cy="85" r="3" fill="currentColor" />
              <circle cx="260" cy="80" r="3" fill="currentColor" />
              <circle cx="300" cy="75" r="3" fill="currentColor" />
              <circle cx="340" cy="70" r="3" fill="currentColor" />
              <circle cx="380" cy="65" r="3" fill="currentColor" />
            </svg>
          </div>
          <div class="mt-4 flex justify-between text-xs text-gray-500">
            <span>1月</span>
            <span>6月</span>
            <span>12月</span>
          </div>
        </div>

        <!-- 疾病类别分布 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-800">疾病类别分布</h3>
            <button class="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">查看详情</button>
          </div>
          <div class="h-64 flex items-center justify-center">
            <!-- 模拟饼图 -->
            <div class="relative w-48 h-48">
              <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#e5e7eb" stroke-width="10"/>
                <circle cx="50" cy="50" r="40" fill="none" stroke="#3b82f6" stroke-width="10" 
                        stroke-dasharray="75 25" stroke-dashoffset="0"/>
                <circle cx="50" cy="50" r="40" fill="none" stroke="#ef4444" stroke-width="10" 
                        stroke-dasharray="50 50" stroke-dashoffset="-75"/>
                <circle cx="50" cy="50" r="40" fill="none" stroke="#22c55e" stroke-width="10" 
                        stroke-dasharray="25 75" stroke-dashoffset="-125"/>
              </svg>
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="text-center">
                  <div class="text-2xl font-bold text-gray-900">{{ statistics.totalDiseases }}</div>
                  <div class="text-xs text-gray-500">总疾病数</div>
                </div>
              </div>
            </div>
          </div>
          <div class="mt-4 space-y-2">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span class="text-sm text-gray-600">肝脏疾病</span>
              </div>
              <span class="text-sm font-medium">45%</span>
            </div>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 bg-red-500 rounded-full"></div>
                <span class="text-sm text-gray-600">心血管疾病</span>
              </div>
              <span class="text-sm font-medium">30%</span>
            </div>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 bg-green-500 rounded-full"></div>
                <span class="text-sm text-gray-600">神经系统疾病</span>
              </div>
              <span class="text-sm font-medium">25%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 详细分析表格 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mb-8">
        <div class="p-6 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-semibold text-gray-800">重定位分析结果</h3>
            <div class="flex gap-2">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索药物或疾病..."
                class="px-3 py-1 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
              <select v-model="confidenceFilter" class="px-3 py-1 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                <option value="all">全部置信度</option>
                <option value="high">高置信度 (>80%)</option>
                <option value="medium">中等置信度 (60-80%)</option>
                <option value="low">低置信度 (<60%)</option>
              </select>
            </div>
          </div>
        </div>
        
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">药物</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">原适应症</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">新适应症</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">置信度</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">证据类型</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="result in filteredResults" :key="result.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                      <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                    </div>
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ result.drug }}</div>
                      <div class="text-sm text-gray-500">{{ result.drugId }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ result.originalIndication }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ result.newIndication }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div class="h-2 rounded-full" :class="[
                        result.confidence >= 80 ? 'bg-green-500' :
                        result.confidence >= 60 ? 'bg-yellow-500' :
                        'bg-red-500'
                      ]" :style="{ width: result.confidence + '%' }"></div>
                    </div>
                    <span class="text-sm font-medium">{{ result.confidence }}%</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full" :class="[
                    result.evidenceType === '临床试验' ? 'bg-green-100 text-green-800' :
                    result.evidenceType === '文献挖掘' ? 'bg-blue-100 text-blue-800' :
                    result.evidenceType === '网络分析' ? 'bg-purple-100 text-purple-800' :
                    'bg-gray-100 text-gray-800'
                  ]">
                    {{ result.evidenceType }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full" :class="[
                    result.status === '已验证' ? 'bg-green-100 text-green-800' :
                    result.status === '验证中' ? 'bg-yellow-100 text-yellow-800' :
                    result.status === '待验证' ? 'bg-gray-100 text-gray-800' :
                    'bg-red-100 text-red-800'
                  ]">
                    {{ result.status }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button @click="viewDetails(result)" class="text-blue-600 hover:text-blue-900 mr-3">查看详情</button>
                  <button @click="addToWatchlist(result)" class="text-green-600 hover:text-green-900">关注</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 网络分析和通路分析 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- 药物-疾病网络 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-800">药物-疾病关联网络</h3>
            <div class="flex gap-2">
              <select v-model="selectedNetworkType" @change="updateNetwork" class="px-2 py-1 text-xs border border-gray-300 rounded">
                <option value="liver">肝脏疾病</option>
                <option value="cardiovascular">心血管疾病</option>
                <option value="cancer">肿瘤疾病</option>
                <option value="all">全部</option>
              </select>
              <button @click="rearrangeNetwork" class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded hover:bg-blue-200">
                重新布局
              </button>
            </div>
          </div>
          <div class="h-80 bg-gray-50 rounded-lg flex items-center justify-center relative overflow-hidden">
            <!-- 增强的网络图 -->
            <svg width="100%" height="100%" viewBox="0 0 400 280" class="cursor-move" @mousedown="startDrag" @mousemove="drag" @mouseup="endDrag">
              <!-- 定义渐变和阴影 -->
              <defs>
                <radialGradient id="drugGradient" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" style="stop-color:#60a5fa;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:1" />
                </radialGradient>
                <radialGradient id="diseaseGradient" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" style="stop-color:#f87171;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#ef4444;stop-opacity:1" />
                </radialGradient>
                <radialGradient id="targetGradient" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" style="stop-color:#4ade80;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#22c55e;stop-opacity:1" />
                </radialGradient>
                <radialGradient id="geneGradient" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" style="stop-color:#a78bfa;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" />
                </radialGradient>
                <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                  <feDropShadow dx="1" dy="1" stdDeviation="2" flood-color="#000" flood-opacity="0.3"/>
                </filter>
              </defs>
              
              <!-- 连接线 - 更多真实的药物-疾病关联 -->
              <g stroke="#d1d5db" stroke-width="1.5" opacity="0.7">
                <!-- 恩替卡韦相关 -->
                <line x1="80" y1="60" x2="150" y2="80" stroke-width="3" stroke="#22c55e" opacity="0.8" />
                <line x1="80" y1="60" x2="180" y2="120" stroke-width="2" stroke="#3b82f6" />
                <line x1="80" y1="60" x2="220" y2="160" stroke-width="2" stroke="#f59e0b" />
                
                <!-- 索拉非尼相关 -->
                <line x1="120" y1="200" x2="200" y2="180" stroke-width="3" stroke="#22c55e" opacity="0.8" />
                <line x1="120" y1="200" x2="280" y2="140" stroke-width="2" stroke="#3b82f6" />
                <line x1="120" y1="200" x2="320" y2="100" stroke-width="2" stroke="#f59e0b" />
                
                <!-- 熊去氧胆酸相关 -->
                <line x1="300" y1="60" x2="250" y2="100" stroke-width="3" stroke="#22c55e" opacity="0.8" />
                <line x1="300" y1="60" x2="180" y2="120" stroke-width="2" stroke="#3b82f6" />
                <line x1="300" y1="60" x2="150" y2="80" stroke-width="2" stroke="#f59e0b" />
                
                <!-- 二甲双胍相关 -->
                <line x1="60" y1="140" x2="150" y2="80" stroke-width="2" stroke="#8b5cf6" />
                <line x1="60" y1="140" x2="200" y2="180" stroke-width="2" stroke="#3b82f6" />
                <line x1="60" y1="140" x2="280" y2="140" stroke-width="2" stroke="#f59e0b" />
                
                <!-- 阿司匹林相关 -->
                <line x1="340" y1="200" x2="280" y2="140" stroke-width="2" stroke="#22c55e" />
                <line x1="340" y1="200" x2="220" y2="160" stroke-width="2" stroke="#3b82f6" />
                <line x1="340" y1="200" x2="200" y2="180" stroke-width="2" stroke="#f59e0b" />
                
                <!-- 靶点和基因连接 -->
                <line x1="150" y1="80" x2="100" y2="100" stroke-width="1" stroke="#8b5cf6" stroke-dasharray="3,3" />
                <line x1="200" y1="180" x2="160" y2="160" stroke-width="1" stroke="#8b5cf6" stroke-dasharray="3,3" />
                <line x1="280" y1="140" x2="240" y2="120" stroke-width="1" stroke="#8b5cf6" stroke-dasharray="3,3" />
                <line x1="220" y1="160" x2="190" y2="140" stroke-width="1" stroke="#8b5cf6" stroke-dasharray="3,3" />
                
                <!-- 基因-疾病关联 -->
                <line x1="100" y1="100" x2="150" y2="80" stroke-width="1" stroke="#a78bfa" />
                <line x1="160" y1="160" x2="200" y2="180" stroke-width="1" stroke="#a78bfa" />
                <line x1="240" y1="120" x2="280" y2="140" stroke-width="1" stroke="#a78bfa" />
                <line x1="190" y1="140" x2="220" y2="160" stroke-width="1" stroke="#a78bfa" />
              </g>
              
              <!-- 节点 - 药物 (蓝色) -->
              <g>
                <circle cx="80" cy="60" r="12" fill="url(#drugGradient)" filter="url(#shadow)" class="hover:r-14 transition-all cursor-pointer" />
                <circle cx="120" cy="200" r="12" fill="url(#drugGradient)" filter="url(#shadow)" class="hover:r-14 transition-all cursor-pointer" />
                <circle cx="300" cy="60" r="12" fill="url(#drugGradient)" filter="url(#shadow)" class="hover:r-14 transition-all cursor-pointer" />
                <circle cx="60" cy="140" r="12" fill="url(#drugGradient)" filter="url(#shadow)" class="hover:r-14 transition-all cursor-pointer" />
                <circle cx="340" cy="200" r="12" fill="url(#drugGradient)" filter="url(#shadow)" class="hover:r-14 transition-all cursor-pointer" />
              </g>
              
              <!-- 节点 - 疾病 (红色) -->
              <g>
                <circle cx="150" cy="80" r="10" fill="url(#diseaseGradient)" filter="url(#shadow)" class="hover:r-12 transition-all cursor-pointer" />
                <circle cx="200" cy="180" r="10" fill="url(#diseaseGradient)" filter="url(#shadow)" class="hover:r-12 transition-all cursor-pointer" />
                <circle cx="280" cy="140" r="10" fill="url(#diseaseGradient)" filter="url(#shadow)" class="hover:r-12 transition-all cursor-pointer" />
                <circle cx="220" cy="160" r="10" fill="url(#diseaseGradient)" filter="url(#shadow)" class="hover:r-12 transition-all cursor-pointer" />
                <circle cx="180" cy="120" r="10" fill="url(#diseaseGradient)" filter="url(#shadow)" class="hover:r-12 transition-all cursor-pointer" />
                <circle cx="250" cy="100" r="10" fill="url(#diseaseGradient)" filter="url(#shadow)" class="hover:r-12 transition-all cursor-pointer" />
                <circle cx="320" cy="100" r="10" fill="url(#diseaseGradient)" filter="url(#shadow)" class="hover:r-12 transition-all cursor-pointer" />
              </g>
              
              <!-- 节点 - 靶点 (绿色) -->
              <g>
                <circle cx="100" cy="100" r="8" fill="url(#targetGradient)" filter="url(#shadow)" class="hover:r-10 transition-all cursor-pointer" />
                <circle cx="160" cy="160" r="8" fill="url(#targetGradient)" filter="url(#shadow)" class="hover:r-10 transition-all cursor-pointer" />
                <circle cx="240" cy="120" r="8" fill="url(#targetGradient)" filter="url(#shadow)" class="hover:r-10 transition-all cursor-pointer" />
                <circle cx="190" cy="140" r="8" fill="url(#targetGradient)" filter="url(#shadow)" class="hover:r-10 transition-all cursor-pointer" />
              </g>
              
              <!-- 节点 - 基因 (紫色) -->
              <g>
                <circle cx="130" cy="120" r="6" fill="url(#geneGradient)" filter="url(#shadow)" class="hover:r-8 transition-all cursor-pointer" />
                <circle cx="170" cy="100" r="6" fill="url(#geneGradient)" filter="url(#shadow)" class="hover:r-8 transition-all cursor-pointer" />
                <circle cx="260" cy="120" r="6" fill="url(#geneGradient)" filter="url(#shadow)" class="hover:r-8 transition-all cursor-pointer" />
                <circle cx="210" cy="140" r="6" fill="url(#geneGradient)" filter="url(#shadow)" class="hover:r-8 transition-all cursor-pointer" />
                <circle cx="140" cy="160" r="6" fill="url(#geneGradient)" filter="url(#shadow)" class="hover:r-8 transition-all cursor-pointer" />
              </g>
              
              <!-- 标签 -->
              <g class="text-xs fill-gray-700 font-medium">
                <!-- 药物标签 -->
                <text x="80" y="45" text-anchor="middle">恩替卡韦</text>
                <text x="120" y="220" text-anchor="middle">索拉非尼</text>
                <text x="300" y="45" text-anchor="middle">熊去氧胆酸</text>
                <text x="60" y="125" text-anchor="middle">二甲双胍</text>
                <text x="340" y="185" text-anchor="middle">阿司匹林</text>
                
                <!-- 疾病标签 -->
                <text x="150" y="95" text-anchor="middle" class="text-xs">乙肝</text>
                <text x="200" y="195" text-anchor="middle" class="text-xs">肝癌</text>
                <text x="280" y="155" text-anchor="middle" class="text-xs">肝硬化</text>
                <text x="220" y="175" text-anchor="middle" class="text-xs">肝纤维化</text>
                <text x="180" y="135" text-anchor="middle" class="text-xs">脂肪肝</text>
                <text x="250" y="115" text-anchor="middle" class="text-xs">胆汁淤积</text>
                <text x="320" y="115" text-anchor="middle" class="text-xs">肝炎</text>
                
                <!-- 靶点标签 -->
                <text x="100" y="90" text-anchor="middle" class="text-xs">HBV-POL</text>
                <text x="160" y="150" text-anchor="middle" class="text-xs">VEGFR</text>
                <text x="240" y="110" text-anchor="middle" class="text-xs">FXR</text>
                <text x="190" y="130" text-anchor="middle" class="text-xs">PDGFR</text>
                
                <!-- 基因标签 -->
                <text x="130" y="110" text-anchor="middle" class="text-xs">TP53</text>
                <text x="170" y="90" text-anchor="middle" class="text-xs">CTNNB1</text>
                <text x="260" y="110" text-anchor="middle" class="text-xs">TGFB1</text>
                <text x="210" y="130" text-anchor="middle" class="text-xs">VEGFA</text>
                <text x="140" y="150" text-anchor="middle" class="text-xs">MYC</text>
              </g>
            </svg>
          </div>
          <div class="mt-4">
            <div class="flex justify-between items-center mb-2">
              <div class="flex gap-4 text-xs">
                <div class="flex items-center gap-1">
                  <div class="w-3 h-3 bg-gradient-to-r from-blue-400 to-blue-600 rounded-full"></div>
                  <span>药物 ({{ networkStats.drugs }})</span>
                </div>
                <div class="flex items-center gap-1">
                  <div class="w-3 h-3 bg-gradient-to-r from-red-400 to-red-600 rounded-full"></div>
                  <span>疾病 ({{ networkStats.diseases }})</span>
                </div>
                <div class="flex items-center gap-1">
                  <div class="w-3 h-3 bg-gradient-to-r from-green-400 to-green-600 rounded-full"></div>
                  <span>靶点 ({{ networkStats.targets }})</span>
                </div>
                <div class="flex items-center gap-1">
                  <div class="w-3 h-3 bg-gradient-to-r from-purple-400 to-purple-600 rounded-full"></div>
                  <span>基因 ({{ networkStats.genes }})</span>
                </div>
              </div>
              <div class="flex gap-2">
                <span class="text-xs text-gray-500">关联: {{ networkStats.connections }}</span>
                <button @click="expandNetwork" class="text-blue-600 hover:text-blue-800 text-sm">查看完整网络</button>
              </div>
            </div>
            <div class="text-xs text-gray-500">
              <div class="flex gap-4">
                <span>强关联 (绿线): 临床验证</span>
                <span>中关联 (蓝线): 文献支持</span>
                <span>弱关联 (黄线): 计算预测</span>
                <span>基因关联 (紫线): 分子机制</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 通路富集分析 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">通路富集分析</h3>
          <div class="space-y-3">
            <div v-for="pathway in pathwayAnalysis" :key="pathway.name" 
                 class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div class="flex-1">
                <div class="font-medium text-gray-800">{{ pathway.name }}</div>
                <div class="text-sm text-gray-600">{{ pathway.description }}</div>
              </div>
              <div class="text-right ml-4">
                <div class="text-sm font-medium" :class="[
                  pathway.pValue < 0.01 ? 'text-red-600' :
                  pathway.pValue < 0.05 ? 'text-orange-600' :
                  'text-gray-600'
                ]">
                  p={{ pathway.pValue }}
                </div>
                <div class="text-xs text-gray-500">{{ pathway.geneCount }}个基因</div>
              </div>
            </div>
          </div>
          <div class="mt-4 text-center">
            <button class="text-blue-600 hover:text-blue-800 text-sm">查看完整通路分析</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const selectedAnalysisType = ref('repositioning')
const selectedTimeRange = ref('all')
const searchQuery = ref('')
const confidenceFilter = ref('all')
const selectedNetworkType = ref('liver')

// 网络交互状态
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })

// 统计数据
const statistics = ref({
  totalDrugs: 1547,
  totalDiseases: 1156,
  repositioningOpportunities: 489,
  successRate: 76
})

// 网络统计数据
const networkStats = ref({
  drugs: 5,
  diseases: 7,
  targets: 4,
  genes: 5,
  connections: 28
})

// 重定位分析结果 - 扩展更多真实数据
const repositioningResults = ref([
  {
    id: 1,
    drug: '恩替卡韦',
    drugId: 'DRUG001',
    originalIndication: '慢性乙型肝炎',
    newIndication: '肝纤维化',
    confidence: 92,
    evidenceType: '临床试验',
    status: '已验证'
  },
  {
    id: 2,
    drug: '索拉非尼',
    drugId: 'DRUG002',
    originalIndication: '肾细胞癌',
    newIndication: '肝细胞癌',
    confidence: 89,
    evidenceType: '临床试验',
    status: '已验证'
  },
  {
    id: 3,
    drug: '熊去氧胆酸',
    drugId: 'DRUG003',
    originalIndication: '胆汁淤积',
    newIndication: '原发性胆汁性肝硬化',
    confidence: 87,
    evidenceType: '临床试验',
    status: '已验证'
  },
  {
    id: 4,
    drug: '二甲双胍',
    drugId: 'DRUG004',
    originalIndication: '2型糖尿病',
    newIndication: '非酒精性脂肪肝',
    confidence: 78,
    evidenceType: '文献挖掘',
    status: '验证中'
  },
  {
    id: 5,
    drug: '阿司匹林',
    drugId: 'DRUG005',
    originalIndication: '心血管疾病',
    newIndication: '肝癌预防',
    confidence: 74,
    evidenceType: '队列研究',
    status: '验证中'
  },
  {
    id: 6,
    drug: '利伐沙班',
    drugId: 'DRUG006',
    originalIndication: '血栓栓塞',
    newIndication: '肝纤维化',
    confidence: 69,
    evidenceType: '网络分析',
    status: '待验证'
  },
  {
    id: 7,
    drug: '西罗莫司',
    drugId: 'DRUG007',
    originalIndication: '器官移植排斥',
    newIndication: '肝血管瘤',
    confidence: 82,
    evidenceType: '病例报告',
    status: '验证中'
  },
  {
    id: 8,
    drug: '奥美拉唑',
    drugId: 'DRUG008',
    originalIndication: '胃食管反流',
    newIndication: '肝性脑病',
    confidence: 65,
    evidenceType: '文献挖掘',
    status: '待验证'
  },
  {
    id: 9,
    drug: '维生素E',
    drugId: 'DRUG009',
    originalIndication: '抗氧化',
    newIndication: '非酒精性脂肪性肝炎',
    confidence: 76,
    evidenceType: '随机对照试验',
    status: '验证中'
  },
  {
    id: 10,
    drug: '吡格列酮',
    drugId: 'DRUG010',
    originalIndication: '2型糖尿病',
    newIndication: '非酒精性脂肪肝',
    confidence: 81,
    evidenceType: '临床试验',
    status: '验证中'
  },
  {
    id: 11,
    drug: '利福昔明',
    drugId: 'DRUG011',
    originalIndication: '肠道感染',
    newIndication: '肝性脑病',
    confidence: 88,
    evidenceType: '临床试验',
    status: '已验证'
  },
  {
    id: 12,
    drug: '普罗布考',
    drugId: 'DRUG012',
    originalIndication: '高胆固醇血症',
    newIndication: '肝纤维化',
    confidence: 71,
    evidenceType: '动物实验',
    status: '待验证'
  }
])

// 通路分析数据 - 扩展更多肝脏相关通路
const pathwayAnalysis = ref([
  {
    name: 'TGF-β信号通路',
    description: '肝纤维化关键调节通路',
    pValue: 0.001,
    geneCount: 28
  },
  {
    name: 'MAPK信号通路',
    description: '肝细胞应激和凋亡反应',
    pValue: 0.003,
    geneCount: 24
  },
  {
    name: 'PI3K-Akt通路',
    description: '肝细胞存活和糖脂代谢',
    pValue: 0.008,
    geneCount: 21
  },
  {
    name: 'NF-κB通路',
    description: '肝脏炎症反应调节',
    pValue: 0.015,
    geneCount: 19
  },
  {
    name: 'Wnt/β-catenin通路',
    description: '肝细胞再生和肝癌发生',
    pValue: 0.022,
    geneCount: 16
  },
  {
    name: 'p53信号通路',
    description: '肝细胞DNA损伤应答',
    pValue: 0.031,
    geneCount: 14
  },
  {
    name: 'PPAR信号通路',
    description: '肝脏脂质代谢调节',
    pValue: 0.045,
    geneCount: 12
  },
  {
    name: 'JAK-STAT通路',
    description: '肝脏免疫和再生信号',
    pValue: 0.058,
    geneCount: 11
  }
])

// 过滤后的结果
const filteredResults = computed(() => {
  let filtered = repositioningResults.value

  // 搜索过滤
  if (searchQuery.value) {
    filtered = filtered.filter(result => 
      result.drug.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      result.newIndication.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  // 置信度过滤
  if (confidenceFilter.value !== 'all') {
    filtered = filtered.filter(result => {
      if (confidenceFilter.value === 'high') return result.confidence > 80
      if (confidenceFilter.value === 'medium') return result.confidence >= 60 && result.confidence <= 80
      if (confidenceFilter.value === 'low') return result.confidence < 60
      return true
    })
  }

  return filtered
})

// 方法
const updateAnalysis = () => {
  console.log('更新分析:', selectedAnalysisType.value, selectedTimeRange.value)
}

const exportAnalysis = () => {
  console.log('导出分析报告')
}

const refreshData = () => {
  console.log('刷新数据')
}

const viewDetails = (result) => {
  console.log('查看详情:', result)
}

const addToWatchlist = (result) => {
  console.log('添加到关注列表:', result)
}

// 网络交互方法
const updateNetwork = () => {
  console.log('更新网络类型:', selectedNetworkType.value)
  // 根据选择的网络类型更新统计数据
  switch (selectedNetworkType.value) {
    case 'liver':
      networkStats.value = { drugs: 5, diseases: 7, targets: 4, genes: 5, connections: 28 }
      break
    case 'cardiovascular':
      networkStats.value = { drugs: 8, diseases: 6, targets: 6, genes: 7, connections: 35 }
      break
    case 'cancer':
      networkStats.value = { drugs: 12, diseases: 9, targets: 8, genes: 11, connections: 52 }
      break
    case 'all':
      networkStats.value = { drugs: 25, diseases: 22, targets: 18, genes: 23, connections: 115 }
      break
  }
}

const rearrangeNetwork = () => {
  console.log('重新布局网络')
  // 这里可以添加网络重新布局的逻辑
}

const expandNetwork = () => {
  console.log('查看完整网络')
  // 这里可以添加跳转到完整网络页面的逻辑
}

const startDrag = (event) => {
  isDragging.value = true
  dragStart.value = { x: event.clientX, y: event.clientY }
}

const drag = (event) => {
  if (!isDragging.value) return
  // 这里可以添加拖拽网络的逻辑
}

const endDrag = () => {
  isDragging.value = false
}

onMounted(() => {
  // 初始化数据
  updateAnalysis()
  updateNetwork()
})
</script>
