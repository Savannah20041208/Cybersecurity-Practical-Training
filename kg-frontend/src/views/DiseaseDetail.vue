<template>
  <div class="p-6 md:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- 返回按钮 -->
      <div class="mb-6">
        <button @click="$router.go(-1)" class="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          返回
        </button>
      </div>

      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p class="text-gray-600">正在加载疾病信息...</p>
        </div>
      </div>

      <div v-else-if="disease" class="space-y-8">
        <!-- 疾病基本信息 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="bg-gradient-to-r from-red-600 to-pink-600 px-6 py-8 text-white">
            <div class="flex items-center gap-4">
              <div class="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
                <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                </svg>
              </div>
              <div>
                <h1 class="text-3xl font-bold mb-2">{{ disease.name }}</h1>
                <p class="text-red-100">{{ disease.englishName }}</p>
                <div class="flex gap-2 mt-3">
                  <span class="bg-white/20 px-3 py-1 rounded-full text-sm">{{ disease.category }}</span>
                  <span class="bg-white/20 px-3 py-1 rounded-full text-sm">{{ disease.severity }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="p-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h3 class="font-semibold text-gray-800 mb-2">基本信息</h3>
                <div class="space-y-2 text-sm">
                  <div><span class="text-gray-500">疾病ID:</span> {{ disease.id }}</div>
                  <div><span class="text-gray-500">ICD-10编码:</span> {{ disease.icd10 }}</div>
                  <div><span class="text-gray-500">患病率:</span> {{ disease.prevalence }}</div>
                  <div><span class="text-gray-500">发病年龄:</span> {{ disease.onsetAge }}</div>
                </div>
              </div>
              
              <div>
                <h3 class="font-semibold text-gray-800 mb-2">临床特征</h3>
                <div class="space-y-2 text-sm">
                  <div><span class="text-gray-500">主要症状:</span> {{ disease.mainSymptoms }}</div>
                  <div><span class="text-gray-500">病程:</span> {{ disease.progression }}</div>
                  <div><span class="text-gray-500">预后:</span> {{ disease.prognosis }}</div>
                  <div><span class="text-gray-500">并发症:</span> {{ disease.complications }}</div>
                </div>
              </div>
              
              <div>
                <h3 class="font-semibold text-gray-800 mb-2">统计信息</h3>
                <div class="space-y-2 text-sm">
                  <div><span class="text-gray-500">相关药物:</span> {{ disease.relatedDrugs }}种</div>
                  <div><span class="text-gray-500">相关基因:</span> {{ disease.relatedGenes }}个</div>
                  <div><span class="text-gray-500">研究文献:</span> {{ disease.researchPapers }}篇</div>
                  <div><span class="text-gray-500">临床试验:</span> {{ disease.clinicalTrials }}项</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 疾病描述 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">疾病概述</h2>
          <div class="prose max-w-none">
            <p class="text-gray-700 leading-relaxed mb-4">{{ disease.description }}</p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <div>
                <h3 class="font-semibold text-gray-800 mb-3">病因</h3>
                <ul class="space-y-2">
                  <li v-for="cause in disease.causes" :key="cause" class="flex items-start gap-2">
                    <div class="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span class="text-sm text-gray-700">{{ cause }}</span>
                  </li>
                </ul>
              </div>
              <div>
                <h3 class="font-semibold text-gray-800 mb-3">风险因素</h3>
                <ul class="space-y-2">
                  <li v-for="factor in disease.riskFactors" :key="factor" class="flex items-start gap-2">
                    <div class="w-2 h-2 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span class="text-sm text-gray-700">{{ factor }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 症状和诊断 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">症状与诊断</h2>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 class="font-semibold text-gray-800 mb-3">临床症状</h3>
              <div class="space-y-3">
                <div v-for="symptom in disease.symptoms" :key="symptom.name" 
                     class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div class="font-medium text-gray-800">{{ symptom.name }}</div>
                    <div class="text-sm text-gray-600">{{ symptom.description }}</div>
                  </div>
                  <div class="text-right">
                    <div class="text-sm font-medium" :class="[
                      symptom.frequency === 'High' ? 'text-red-600' :
                      symptom.frequency === 'Medium' ? 'text-orange-600' :
                      'text-yellow-600'
                    ]">{{ symptom.frequency }}</div>
                    <div class="text-xs text-gray-500">{{ symptom.stage }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="font-semibold text-gray-800 mb-3">诊断方法</h3>
              <div class="space-y-3">
                <div v-for="diagnostic in disease.diagnostics" :key="diagnostic.method" 
                     class="p-3 border border-gray-200 rounded-lg">
                  <div class="flex items-start justify-between mb-2">
                    <h4 class="font-medium text-gray-800">{{ diagnostic.method }}</h4>
                    <span class="text-xs px-2 py-1 rounded-full" :class="[
                      diagnostic.accuracy === 'High' ? 'bg-green-100 text-green-800' :
                      diagnostic.accuracy === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    ]">{{ diagnostic.accuracy }}</span>
                  </div>
                  <p class="text-sm text-gray-600">{{ diagnostic.description }}</p>
                  <div class="mt-2 text-xs text-gray-500">
                    <span>敏感性: {{ diagnostic.sensitivity }}%</span> |
                    <span>特异性: {{ diagnostic.specificity }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 治疗药物 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">治疗药物</h2>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 class="font-semibold text-gray-800 mb-3">一线治疗药物</h3>
              <div class="space-y-3">
                <div v-for="drug in disease.firstLineDrugs" :key="drug.id" 
                     class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <div class="font-medium text-green-800">{{ drug.name }}</div>
                    <div class="text-sm text-green-600">{{ drug.mechanism }}</div>
                  </div>
                  <div class="text-right">
                    <router-link :to="`/drug/${drug.id}`" 
                                 class="text-green-600 hover:text-green-800 text-sm">
                      查看详情
                    </router-link>
                    <div class="text-xs text-green-600 mt-1">有效率: {{ drug.efficacy }}%</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="font-semibold text-gray-800 mb-3">潜在重定位药物</h3>
              <div class="space-y-3">
                <div v-for="drug in disease.repositioningDrugs" :key="drug.id" 
                     class="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <div>
                    <div class="font-medium text-blue-800">{{ drug.name }}</div>
                    <div class="text-sm text-blue-600">{{ drug.originalIndication }}</div>
                  </div>
                  <div class="text-right">
                    <div class="text-sm font-medium text-blue-800">{{ drug.confidence }}%</div>
                    <div class="text-xs text-blue-600">{{ drug.evidence }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 相关基因和靶点 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">相关基因与靶点</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">基因/靶点</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">功能</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">关联性</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">证据水平</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="target in disease.relatedTargets" :key="target.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{{ target.name }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ target.type }}</td>
                  <td class="px-6 py-4 text-sm text-gray-600">{{ target.function }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ target.association }}</td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="[
                      target.evidenceLevel === 'High' ? 'bg-green-100 text-green-800' :
                      target.evidenceLevel === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800',
                      'inline-flex px-2 py-1 text-xs font-semibold rounded-full'
                    ]">
                      {{ target.evidenceLevel }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 疾病进展和分期 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">疾病进展与分期</h2>
          <div class="relative">
            <div class="flex items-center justify-between mb-6">
              <div v-for="(stage, index) in disease.stages" :key="stage.name" 
                   class="flex flex-col items-center relative" 
                   :class="index < disease.stages.length - 1 ? 'flex-1' : ''">
                <div class="w-12 h-12 rounded-full flex items-center justify-center mb-2" 
                     :class="[
                       stage.severity === 'Mild' ? 'bg-green-500 text-white' :
                       stage.severity === 'Moderate' ? 'bg-yellow-500 text-white' :
                       stage.severity === 'Severe' ? 'bg-red-500 text-white' :
                       'bg-purple-500 text-white'
                     ]">
                  {{ index + 1 }}
                </div>
                <h3 class="font-semibold text-center mb-1">{{ stage.name }}</h3>
                <p class="text-sm text-gray-600 text-center max-w-32">{{ stage.description }}</p>
                
                <!-- 连接线 -->
                <div v-if="index < disease.stages.length - 1" 
                     class="absolute top-6 left-full w-full h-0.5 bg-gray-300 transform -translate-y-1/2 z-0"></div>
              </div>
            </div>
            
            <!-- 详细信息 -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
              <div v-for="stage in disease.stages" :key="stage.name" 
                   class="p-4 border border-gray-200 rounded-lg">
                <h4 class="font-semibold text-gray-800 mb-2">{{ stage.name }}</h4>
                <div class="space-y-2 text-sm">
                  <div><span class="text-gray-500">持续时间:</span> {{ stage.duration }}</div>
                  <div><span class="text-gray-500">主要特征:</span> {{ stage.features }}</div>
                  <div><span class="text-gray-500">治疗重点:</span> {{ stage.treatment }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 相关研究 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">最新研究进展</h2>
          <div class="space-y-4">
            <div v-for="research in disease.recentResearch" :key="research.id" 
                 class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div class="flex justify-between items-start mb-2">
                <h3 class="font-semibold text-gray-900">{{ research.title }}</h3>
                <span class="text-sm text-gray-500">{{ research.year }}</span>
              </div>
              <p class="text-sm text-gray-600 mb-2">{{ research.authors }}</p>
              <p class="text-sm text-gray-700 mb-3">{{ research.findings }}</p>
              <div class="flex justify-between items-center">
                <div class="flex gap-2">
                  <span v-for="keyword in research.keywords" :key="keyword"
                        class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                    {{ keyword }}
                  </span>
                </div>
                <div class="flex gap-2">
                  <span class="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800">
                    {{ research.type }}
                  </span>
                  <a :href="research.url" target="_blank" class="text-blue-600 hover:text-blue-900 text-sm">查看详情</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-20">
        <div class="text-gray-400 mb-4">
          <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0118 12a8 8 0 00-8-8 8 8 0 00-8 8c0 2.485.953 4.743 2.51 6.42l1.49 2.08L12 22l6-1.5 1.49-2.08A7.962 7.962 0 0021 12a8 8 0 00-8-8z"></path>
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-gray-800 mb-2">未找到疾病信息</h2>
        <p class="text-gray-600">请检查疾病ID是否正确，或返回重新搜索。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const loading = ref(true)
const disease = ref(null)

// 模拟疾病数据
const mockDisease = {
  id: 'DIS001',
  name: '肝纤维化',
  englishName: 'Hepatic Fibrosis',
  category: '肝脏疾病',
  severity: '慢性进展性',
  icd10: 'K74.0',
  prevalence: '全球约2-3%',
  onsetAge: '40-60岁',
  mainSymptoms: '肝功能异常、腹胀',
  progression: '慢性进展',
  prognosis: '早期可逆，晚期不可逆',
  complications: '肝硬化、肝癌',
  relatedDrugs: 15,
  relatedGenes: 23,
  researchPapers: 1247,
  clinicalTrials: 89,
  description: '肝纤维化是由各种致病因子所致肝内结缔组织异常增生，导致肝内弥漫性细胞外基质过度沉淀的病理过程。它不是一个独立的疾病，而是许多慢性肝病的共同病理基础。',
  causes: [
    '病毒性肝炎（乙肝、丙肝）',
    '酒精性肝病',
    '非酒精性脂肪性肝病',
    '自身免疫性肝病',
    '药物性肝损伤'
  ],
  riskFactors: [
    '长期饮酒',
    '肥胖和糖尿病',
    '病毒感染',
    '遗传因素',
    '环境毒素暴露'
  ],
  symptoms: [
    {
      name: '乏力',
      description: '持续性疲劳感',
      frequency: 'High',
      stage: '早期'
    },
    {
      name: '腹胀',
      description: '餐后腹部胀满感',
      frequency: 'Medium',
      stage: '中期'
    },
    {
      name: '肝区疼痛',
      description: '右上腹隐痛',
      frequency: 'Medium',
      stage: '中期'
    },
    {
      name: '黄疸',
      description: '皮肤和巩膜黄染',
      frequency: 'Low',
      stage: '晚期'
    }
  ],
  diagnostics: [
    {
      method: '肝脏弹性成像',
      description: '无创评估肝脏硬度',
      accuracy: 'High',
      sensitivity: 85,
      specificity: 92
    },
    {
      method: '血清纤维化标志物',
      description: '检测透明质酸、层粘连蛋白等',
      accuracy: 'Medium',
      sensitivity: 75,
      specificity: 80
    },
    {
      method: '肝脏活检',
      description: '组织学检查金标准',
      accuracy: 'High',
      sensitivity: 95,
      specificity: 98
    }
  ],
  firstLineDrugs: [
    {
      id: 'DRUG003',
      name: '恩替卡韦',
      mechanism: '核苷类似物',
      efficacy: 85
    },
    {
      id: 'DRUG004',
      name: '熊去氧胆酸',
      mechanism: '胆汁酸',
      efficacy: 70
    }
  ],
  repositioningDrugs: [
    {
      id: 'DRUG001',
      name: '阿司匹林',
      originalIndication: '心血管疾病',
      confidence: 78,
      evidence: '抗炎作用'
    },
    {
      id: 'DRUG005',
      name: '二甲双胍',
      originalIndication: '糖尿病',
      confidence: 65,
      evidence: '代谢调节'
    }
  ],
  relatedTargets: [
    {
      id: 1,
      name: 'TGF-β1',
      type: '细胞因子',
      function: '促进纤维化',
      association: '上调表达',
      evidenceLevel: 'High'
    },
    {
      id: 2,
      name: 'PDGF',
      type: '生长因子',
      function: '肝星状细胞激活',
      association: '信号通路激活',
      evidenceLevel: 'High'
    },
    {
      id: 3,
      name: 'MMP-2',
      type: '基质金属蛋白酶',
      function: '细胞外基质重塑',
      association: '活性增加',
      evidenceLevel: 'Medium'
    }
  ],
  stages: [
    {
      name: '早期纤维化',
      severity: 'Mild',
      description: '轻微纤维增生',
      duration: '1-3年',
      features: '肝功能基本正常',
      treatment: '病因治疗'
    },
    {
      name: '中度纤维化',
      severity: 'Moderate',
      description: '明显纤维增生',
      duration: '3-5年',
      features: '肝功能轻度异常',
      treatment: '抗纤维化治疗'
    },
    {
      name: '重度纤维化',
      severity: 'Severe',
      description: '广泛纤维增生',
      duration: '5-10年',
      features: '肝功能明显异常',
      treatment: '综合治疗'
    },
    {
      name: '肝硬化',
      severity: 'Critical',
      description: '假小叶形成',
      duration: '10年以上',
      features: '肝功能失代偿',
      treatment: '肝移植考虑'
    }
  ],
  recentResearch: [
    {
      id: 1,
      title: '基于机器学习的肝纤维化药物重定位研究',
      authors: '王教授团队',
      year: 2024,
      findings: '发现了5种具有抗纤维化潜力的已上市药物',
      keywords: ['机器学习', '药物重定位', '肝纤维化'],
      type: '计算研究',
      url: 'https://example.com/research1'
    },
    {
      id: 2,
      title: '肝星状细胞激活机制的新发现',
      authors: '李研究员等',
      year: 2024,
      findings: '揭示了新的信号通路在肝纤维化中的作用',
      keywords: ['肝星状细胞', '信号通路', '纤维化机制'],
      type: '基础研究',
      url: 'https://example.com/research2'
    }
  ]
}

onMounted(() => {
  // 模拟API调用
  setTimeout(() => {
    const diseaseId = route.params.id
    if (diseaseId === 'DIS001' || !diseaseId) {
      disease.value = mockDisease
    }
    loading.value = false
  }, 1000)
})
</script>
