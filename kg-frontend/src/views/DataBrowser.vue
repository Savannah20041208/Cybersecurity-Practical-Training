<template>
  <div class="p-6 md:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">数据浏览</h1>
        <p class="text-gray-600">查看药物、疾病、基因、文献等详细列表</p>
      </div>

      <!-- 标签页导航 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mb-6">
        <div class="border-b border-gray-200">
          <nav class="flex space-x-8 px-6" aria-label="Tabs">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors'
              ]"
            >
              <div class="flex items-center gap-2">
                <component :is="tab.icon" class="w-5 h-5" />
                {{ tab.name }}
                <span class="bg-gray-100 text-gray-600 py-1 px-2 rounded-full text-xs">{{ tab.count }}</span>
              </div>
            </button>
          </nav>
        </div>

        <!-- 搜索和筛选 -->
        <div class="p-6 border-b border-gray-200">
          <div class="flex flex-col md:flex-row gap-4">
            <div class="flex-1">
              <input
                v-model="searchQuery"
                type="text"
                :placeholder="`搜索${getCurrentTab().name}...`"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div class="flex gap-2">
              <select v-model="sortBy" class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                <option value="name">按名称排序</option>
                <option value="date">按日期排序</option>
                <option value="relevance">按相关性排序</option>
              </select>
              <button
                @click="exportData"
                class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                导出
              </button>
            </div>
          </div>
        </div>

        <!-- 数据表格 -->
        <div class="overflow-x-auto">
          <!-- 药物数据 -->
          <div v-if="activeTab === 'drugs'" class="min-w-full">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">药物名称</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">分子式</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">作用机制</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">适应症</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="drug in filteredDrugs" :key="drug.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
                        <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                      </div>
                      <div>
                        <div class="text-sm font-medium text-gray-900">{{ drug.name }}</div>
                        <div class="text-sm text-gray-500">{{ drug.id }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ drug.formula }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ drug.mechanism }}</td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex flex-wrap gap-1">
                      <span v-for="indication in drug.indications" :key="indication" 
                            class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                        {{ indication }}
                      </span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <router-link :to="`/drug/${drug.id}`" class="text-blue-600 hover:text-blue-900 mr-3">查看详情</router-link>
                    <button @click="addToComparison(drug)" class="text-green-600 hover:text-green-900">添加对比</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 疾病数据 -->
          <div v-if="activeTab === 'diseases'" class="min-w-full">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">疾病名称</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">分类</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">症状</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">相关药物数量</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="disease in filteredDiseases" :key="disease.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center mr-3">
                        <svg class="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                        </svg>
                      </div>
                      <div>
                        <div class="text-sm font-medium text-gray-900">{{ disease.name }}</div>
                        <div class="text-sm text-gray-500">{{ disease.id }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ disease.category }}</td>
                  <td class="px-6 py-4 text-sm text-gray-900">{{ disease.symptoms }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                      {{ disease.drugCount }} 种药物
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <router-link :to="`/disease/${disease.id}`" class="text-blue-600 hover:text-blue-900">查看详情</router-link>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 基因数据 -->
          <div v-if="activeTab === 'genes'" class="min-w-full">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">基因名称</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">染色体位置</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">功能</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">相关疾病</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="gene in filteredGenes" :key="gene.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center mr-3">
                        <svg class="w-5 h-5 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"></path>
                          <path fill-rule="evenodd" d="M4 5a2 2 0 012-2v1a1 1 0 102 0V3a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm2.5 5a1.5 1.5 0 100-3 1.5 1.5 0 000 3zm2.45 4a2.5 2.5 0 10-4.9 0h4.9zM12 9a1 1 0 100 2h3a1 1 0 100-2h-3zm-1 4a1 1 0 011-1h2a1 1 0 110 2h-2a1 1 0 01-1-1z" clip-rule="evenodd"></path>
                        </svg>
                      </div>
                      <div>
                        <div class="text-sm font-medium text-gray-900">{{ gene.name }}</div>
                        <div class="text-sm text-gray-500">{{ gene.id }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ gene.chromosome }}</td>
                  <td class="px-6 py-4 text-sm text-gray-900">{{ gene.function }}</td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex flex-wrap gap-1">
                      <span v-for="disease in gene.relatedDiseases" :key="disease" 
                            class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                        {{ disease }}
                      </span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button class="text-blue-600 hover:text-blue-900">查看详情</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 文献数据 -->
          <div v-if="activeTab === 'literature'" class="min-w-full">
            <div class="space-y-4 p-6">
              <div v-for="paper in filteredLiterature" :key="paper.id" 
                   class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-2">
                  <h3 class="text-lg font-semibold text-gray-900">{{ paper.title }}</h3>
                  <span class="text-sm text-gray-500">{{ paper.year }}</span>
                </div>
                <p class="text-sm text-gray-600 mb-2">{{ paper.authors }}</p>
                <p class="text-sm text-gray-700 mb-3">{{ paper.abstract }}</p>
                <div class="flex justify-between items-center">
                  <div class="flex gap-2">
                    <span v-for="keyword in paper.keywords" :key="keyword"
                          class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                      {{ keyword }}
                    </span>
                  </div>
                  <a :href="paper.url" target="_blank" class="text-blue-600 hover:text-blue-900 text-sm">查看原文</a>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
          <div class="flex-1 flex justify-between sm:hidden">
            <button class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
              上一页
            </button>
            <button class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
              下一页
            </button>
          </div>
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                显示 <span class="font-medium">1</span> 到 <span class="font-medium">10</span> 条，共 <span class="font-medium">{{ getCurrentTab().count }}</span> 条记录
              </p>
            </div>
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
                  上一页
                </button>
                <button class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
                  1
                </button>
                <button class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-blue-50 text-sm font-medium text-blue-600">
                  2
                </button>
                <button class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
                  3
                </button>
                <button class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
                  下一页
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const activeTab = ref('drugs')
const searchQuery = ref('')
const sortBy = ref('name')

// 标签页配置
const tabs = [
  { id: 'drugs', name: '药物', count: '12,547', icon: 'PillIcon' },
  { id: 'diseases', name: '疾病', count: '8,923', icon: 'HeartIcon' },
  { id: 'genes', name: '基因', count: '15,672', icon: 'DNAIcon' },
  { id: 'literature', name: '文献', count: '45,891', icon: 'BookIcon' }
]

// 真实的医疗相关药物数据
const drugs = ref([
  {
    id: 'DRUG001',
    name: '恩替卡韦',
    formula: 'C12H15N5O3',
    mechanism: '核苷类逆转录酶抑制剂',
    indications: ['慢性乙型肝炎', '肝纤维化预防']
  },
  {
    id: 'DRUG002',
    name: '索拉非尼',
    formula: 'C21H16ClF3N4O3',
    mechanism: '多激酶抑制剂',
    indications: ['肝细胞癌', '肾细胞癌']
  },
  {
    id: 'DRUG003',
    name: '熊去氧胆酸',
    formula: 'C24H40O4',
    mechanism: '胆汁酸替代疗法',
    indications: ['原发性胆汁性肝硬化', '胆石症']
  },
  {
    id: 'DRUG004',
    name: '吡非尼酮',
    formula: 'C12H11NO',
    mechanism: '抗纤维化剂',
    indications: ['特发性肺纤维化', '肝纤维化']
  },
  {
    id: 'DRUG005',
    name: '秋水仙碱',
    formula: 'C22H25NO6',
    mechanism: '微管蛋白聚合抑制剂',
    indications: ['痛风', '肝纤维化']
  },
  {
    id: 'DRUG006',
    name: '甲氨蝶呤',
    formula: 'C20H22N8O5',
    mechanism: '叶酸拮抗剂',
    indications: ['类风湿关节炎', '肝纤维化治疗']
  },
  {
    id: 'DRUG007',
    name: '利巴韦林',
    formula: 'C8H12N4O5',
    mechanism: '核苷类似物',
    indications: ['丙型肝炎', '呼吸道合胞病毒感染']
  },
  {
    id: 'DRUG008',
    name: '普萘洛尔',
    formula: 'C16H21NO2',
    mechanism: 'β受体阻滞剂',
    indications: ['门脉高压', '食管静脉曲张出血预防']
  },
  {
    id: 'DRUG009',
    name: '拉米夫定',
    formula: 'C8H11N3O3S',
    mechanism: '核苷类逆转录酶抑制剂',
    indications: ['慢性乙型肝炎', 'HIV感染']
  },
  {
    id: 'DRUG010',
    name: '阿德福韦酯',
    formula: 'C20H32N5O8P',
    mechanism: '核苷酸类似物',
    indications: ['慢性乙型肝炎', '肝硬化']
  },
  {
    id: 'DRUG011',
    name: '替诺福韦',
    formula: 'C9H14N5O4P',
    mechanism: '核苷酸逆转录酶抑制剂',
    indications: ['慢性乙型肝炎', 'HIV感染']
  },
  {
    id: 'DRUG012',
    name: '干扰素α-2b',
    formula: 'C860H1353N229O255S9',
    mechanism: '免疫调节剂',
    indications: ['慢性乙型肝炎', '慢性丙型肝炎']
  },
  {
    id: 'DRUG013',
    name: '聚乙二醇干扰素',
    formula: 'C860H1353N229O255S9',
    mechanism: '长效免疫调节剂',
    indications: ['慢性丙型肝炎', '慢性乙型肝炎']
  },
  {
    id: 'DRUG014',
    name: '西美替丁',
    formula: 'C10H16N6S',
    mechanism: 'H2受体拮抗剂',
    indications: ['消化性溃疡', '肝纤维化辅助治疗']
  },
  {
    id: 'DRUG015',
    name: '奥美拉唑',
    formula: 'C17H19N3O3S',
    mechanism: '质子泵抑制剂',
    indications: ['消化性溃疡', '肝硬化并发症']
  },
  {
    id: 'DRUG016',
    name: '螺内酯',
    formula: 'C24H32O4S',
    mechanism: '醛固酮受体拮抗剂',
    indications: ['肝硬化腹水', '心力衰竭']
  },
  {
    id: 'DRUG017',
    name: '呋塞米',
    formula: 'C12H11ClN2O5S',
    mechanism: '袢利尿剂',
    indications: ['肝硬化腹水', '心力衰竭']
  },
  {
    id: 'DRUG018',
    name: '乳果糖',
    formula: 'C12H22O11',
    mechanism: '渗透性泻药',
    indications: ['肝性脑病', '便秘']
  },
  {
    id: 'DRUG019',
    name: '左卡尼汀',
    formula: 'C7H15NO3',
    mechanism: '脂肪酸β氧化促进剂',
    indications: ['脂肪肝', '肝功能不全']
  },
  {
    id: 'DRUG020',
    name: '水飞蓟素',
    formula: 'C25H22O10',
    mechanism: '肝细胞保护剂',
    indications: ['药物性肝损伤', '酒精性肝病']
  },
  {
    id: 'DRUG021',
    name: '多烯磷脂酰胆碱',
    formula: 'C42H80NO8P',
    mechanism: '细胞膜稳定剂',
    indications: ['脂肪肝', '肝细胞损伤']
  },
  {
    id: 'DRUG022',
    name: '甘草酸二铵',
    formula: 'C42H65NO16',
    mechanism: '抗炎保肝剂',
    indications: ['慢性肝炎', '药物性肝损伤']
  },
  {
    id: 'DRUG023',
    name: '还原型谷胱甘肽',
    formula: 'C10H17N3O6S',
    mechanism: '抗氧化剂',
    indications: ['药物性肝损伤', '肝功能不全']
  },
  {
    id: 'DRUG024',
    name: '腺苷蛋氨酸',
    formula: 'C15H22N6O5S',
    mechanism: '甲基供体',
    indications: ['肝内胆汁淤积', '抑郁症']
  },
  {
    id: 'DRUG025',
    name: '门冬氨酸鸟氨酸',
    formula: 'C8H15N3O6',
    mechanism: '氨解毒剂',
    indications: ['肝性脑病', '高氨血症']
  }
])

const diseases = ref([
  {
    id: 'DIS001',
    name: '肝纤维化',
    category: '医疗疾病',
    symptoms: '肝脏硬化、功能减退、门脉高压',
    drugCount: 15
  },
  {
    id: 'DIS002',
    name: '肝硬化',
    category: '医疗疾病',
    symptoms: '腹水、黄疸、肝性脑病、脾肿大',
    drugCount: 23
  },
  {
    id: 'DIS003',
    name: '肝细胞癌',
    category: '恶性肿瘤',
    symptoms: '肝区疼痛、消瘦、腹胀、黄疸',
    drugCount: 12
  },
  {
    id: 'DIS004',
    name: '慢性乙型肝炎',
    category: '病毒性肝炎',
    symptoms: '乏力、食欲不振、肝区不适、黄疸',
    drugCount: 18
  },
  {
    id: 'DIS005',
    name: '慢性丙型肝炎',
    category: '病毒性肝炎',
    symptoms: '疲劳、关节痛、肝功能异常',
    drugCount: 14
  },
  {
    id: 'DIS006',
    name: '脂肪肝',
    category: '代谢性肝病',
    symptoms: '肝肿大、右上腹胀满、乏力',
    drugCount: 16
  },
  {
    id: 'DIS007',
    name: '酒精性肝病',
    category: '中毒性肝病',
    symptoms: '肝肿大、黄疸、腹水、蜘蛛痣',
    drugCount: 11
  },
  {
    id: 'DIS008',
    name: '药物性肝损伤',
    category: '中毒性肝病',
    symptoms: '转氨酶升高、黄疸、皮疹、发热',
    drugCount: 9
  },
  {
    id: 'DIS009',
    name: '原发性胆汁性肝硬化',
    category: '自身免疫性肝病',
    symptoms: '皮肤瘙痒、黄疸、骨痛、疲劳',
    drugCount: 8
  },
  {
    id: 'DIS010',
    name: '自身免疫性肝炎',
    category: '自身免疫性肝病',
    symptoms: '乏力、关节痛、皮疹、肝功能异常',
    drugCount: 13
  },
  {
    id: 'DIS011',
    name: '原发性硬化性胆管炎',
    category: '胆管疾病',
    symptoms: '黄疸、瘙痒、腹痛、体重下降',
    drugCount: 7
  },
  {
    id: 'DIS012',
    name: '肝性脑病',
    category: '肝脏并发症',
    symptoms: '意识障碍、行为异常、震颤、昏迷',
    drugCount: 6
  },
  {
    id: 'DIS013',
    name: '门脉高压症',
    category: '肝脏并发症',
    symptoms: '脾肿大、腹水、食管静脉曲张',
    drugCount: 10
  },
  {
    id: 'DIS014',
    name: '肝内胆汁淤积',
    category: '胆汁淤积性疾病',
    symptoms: '黄疸、皮肤瘙痒、大便颜色变浅',
    drugCount: 8
  },
  {
    id: 'DIS015',
    name: '威尔逊病',
    category: '遗传性肝病',
    symptoms: '肝硬化、神经症状、角膜环',
    drugCount: 5
  },
  {
    id: 'DIS016',
    name: '血色病',
    category: '遗传性肝病',
    symptoms: '肝肿大、皮肤色素沉着、糖尿病',
    drugCount: 4
  },
  {
    id: 'DIS017',
    name: 'α1-抗胰蛋白酶缺乏症',
    category: '遗传性肝病',
    symptoms: '肝硬化、肺气肿、黄疸',
    drugCount: 3
  },
  {
    id: 'DIS018',
    name: '急性肝衰竭',
    category: '急性肝病',
    symptoms: '黄疸、凝血功能障碍、肝性脑病',
    drugCount: 12
  },
  {
    id: 'DIS019',
    name: '肝血管瘤',
    category: '肝脏良性肿瘤',
    symptoms: '多数无症状、偶有腹胀不适',
    drugCount: 2
  },
  {
    id: 'DIS020',
    name: '肝囊肿',
    category: '肝脏良性病变',
    symptoms: '多数无症状、大囊肿可引起压迫症状',
    drugCount: 1
  },
  {
    id: 'DIS021',
    name: '肝腺瘤',
    category: '肝脏良性肿瘤',
    symptoms: '腹痛、肝肿大、出血风险',
    drugCount: 3
  },
  {
    id: 'DIS022',
    name: '胆管细胞癌',
    category: '恶性肿瘤',
    symptoms: '黄疸、腹痛、体重下降、发热',
    drugCount: 8
  },
  {
    id: 'DIS023',
    name: '肝转移癌',
    category: '恶性肿瘤',
    symptoms: '肝肿大、腹痛、黄疸、消瘦',
    drugCount: 15
  },
  {
    id: 'DIS024',
    name: '布加综合征',
    category: '血管性肝病',
    symptoms: '腹水、肝肿大、下肢水肿',
    drugCount: 6
  },
  {
    id: 'DIS025',
    name: '肝窦阻塞综合征',
    category: '血管性肝病',
    symptoms: '肝肿大、腹水、黄疸、体重增加',
    drugCount: 4
  }
])

const genes = ref([
  {
    id: 'GENE001',
    name: 'COL1A1',
    chromosome: '17q21.33',
    function: '编码I型胶原α1链，参与纤维化过程',
    relatedDiseases: ['肝纤维化', '肝硬化']
  },
  {
    id: 'GENE002',
    name: 'ACTA2',
    chromosome: '10q23.31',
    function: '编码α-平滑肌肌动蛋白，肝星状细胞激活标志',
    relatedDiseases: ['肝纤维化', '肝硬化']
  },
  {
    id: 'GENE003',
    name: 'TGFB1',
    chromosome: '19q13.2',
    function: '编码转化生长因子β1，关键纤维化因子',
    relatedDiseases: ['肝纤维化', '肝硬化', '肝细胞癌']
  },
  {
    id: 'GENE004',
    name: 'SMAD3',
    chromosome: '15q22.33',
    function: 'TGF-β信号转导关键转录因子',
    relatedDiseases: ['肝纤维化', '肝硬化']
  },
  {
    id: 'GENE005',
    name: 'TIMP1',
    chromosome: 'Xp11.3-p11.23',
    function: '金属蛋白酶组织抑制因子1，调节ECM降解',
    relatedDiseases: ['肝纤维化', '肝硬化']
  },
  {
    id: 'GENE006',
    name: 'MMP2',
    chromosome: '16q12.2',
    function: '基质金属蛋白酶2，降解胶原',
    relatedDiseases: ['肝纤维化', '肝细胞癌']
  },
  {
    id: 'GENE007',
    name: 'TP53',
    chromosome: '17p13.1',
    function: '肿瘤抑制基因，调节细胞周期和凋亡',
    relatedDiseases: ['肝细胞癌', '肝硬化']
  },
  {
    id: 'GENE008',
    name: 'CTNNB1',
    chromosome: '3p22.1',
    function: '编码β-连环蛋白，Wnt信号通路关键分子',
    relatedDiseases: ['肝细胞癌', '肝纤维化']
  },
  {
    id: 'GENE009',
    name: 'HBV',
    chromosome: '病毒基因组',
    function: '乙型肝炎病毒基因组，引起慢性肝炎',
    relatedDiseases: ['慢性乙型肝炎', '肝硬化', '肝细胞癌']
  },
  {
    id: 'GENE010',
    name: 'HCV',
    chromosome: '病毒基因组',
    function: '丙型肝炎病毒基因组，引起慢性肝炎',
    relatedDiseases: ['慢性丙型肝炎', '肝硬化', '肝细胞癌']
  },
  {
    id: 'GENE011',
    name: 'PNPLA3',
    chromosome: '22q13.31',
    function: '编码脂肪酶，参与脂质代谢',
    relatedDiseases: ['脂肪肝', '肝纤维化', '肝细胞癌']
  },
  {
    id: 'GENE012',
    name: 'TM6SF2',
    chromosome: '19p13.11',
    function: '跨膜蛋白，调节脂质代谢',
    relatedDiseases: ['脂肪肝', '肝纤维化']
  },
  {
    id: 'GENE013',
    name: 'MBOAT7',
    chromosome: '19q13.42',
    function: '膜结合O-酰基转移酶，脂质重塑',
    relatedDiseases: ['脂肪肝', '肝纤维化']
  },
  {
    id: 'GENE014',
    name: 'ATP7B',
    chromosome: '13q14.3',
    function: '铜转运ATP酶，铜代谢关键酶',
    relatedDiseases: ['威尔逊病', '肝硬化']
  },
  {
    id: 'GENE015',
    name: 'HFE',
    chromosome: '6p22.2',
    function: '血色病基因，调节铁吸收',
    relatedDiseases: ['血色病', '肝硬化']
  },
  {
    id: 'GENE016',
    name: 'SERPINA1',
    chromosome: '14q32.13',
    function: '编码α1-抗胰蛋白酶',
    relatedDiseases: ['α1-抗胰蛋白酶缺乏症', '肝硬化']
  },
  {
    id: 'GENE017',
    name: 'CYP2E1',
    chromosome: '10q26.3',
    function: '细胞色素P450酶，酒精代谢',
    relatedDiseases: ['酒精性肝病', '药物性肝损伤']
  },
  {
    id: 'GENE018',
    name: 'ALDH2',
    chromosome: '12q24.12',
    function: '醛脱氢酶2，乙醛代谢',
    relatedDiseases: ['酒精性肝病', '脂肪肝']
  },
  {
    id: 'GENE019',
    name: 'APOE',
    chromosome: '19q13.32',
    function: '载脂蛋白E，脂质转运',
    relatedDiseases: ['脂肪肝', '肝硬化']
  },
  {
    id: 'GENE020',
    name: 'IL6',
    chromosome: '7p15.3',
    function: '白细胞介素6，炎症因子',
    relatedDiseases: ['肝炎', '肝纤维化', '肝细胞癌']
  },
  {
    id: 'GENE021',
    name: 'TNF',
    chromosome: '6p21.33',
    function: '肿瘤坏死因子α，炎症介质',
    relatedDiseases: ['肝炎', '肝纤维化', '酒精性肝病']
  },
  {
    id: 'GENE022',
    name: 'IFNG',
    chromosome: '12q15',
    function: '干扰素γ，免疫调节',
    relatedDiseases: ['病毒性肝炎', '自身免疫性肝炎']
  },
  {
    id: 'GENE023',
    name: 'VEGFA',
    chromosome: '6p21.1',
    function: '血管内皮生长因子A，血管生成',
    relatedDiseases: ['肝细胞癌', '肝纤维化']
  },
  {
    id: 'GENE024',
    name: 'PDGFRB',
    chromosome: '5q32',
    function: '血小板衍生生长因子受体β',
    relatedDiseases: ['肝纤维化', '肝星状细胞激活']
  },
  {
    id: 'GENE025',
    name: 'NF1',
    chromosome: '17q11.2',
    function: '神经纤维瘤病基因1，肿瘤抑制',
    relatedDiseases: ['肝细胞癌', '肝血管瘤']
  }
])

const literature = ref([
  {
    id: 'LIT001',
    title: 'Drug repositioning for liver fibrosis: Computational approaches and therapeutic targets',
    authors: 'Chen L, Wang Y, Zhang H, Liu M',
    year: 2024,
    abstract: '本研究系统性地分析了肝纤维化的分子机制，并通过计算方法识别了多个潜在的药物重定位候选物。研究发现TGF-β信号通路是关键的治疗靶点，多个FDA批准的药物显示出抗纤维化潜力。',
    keywords: ['药物重定位', '肝纤维化', 'TGF-β', '计算药理学'],
    url: 'https://doi.org/10.1016/j.jhep.2024.01.015'
  },
  {
    id: 'LIT002',
    title: 'Sorafenib in hepatocellular carcinoma: A systematic review and meta-analysis',
    authors: 'Rodriguez M, Kim S, Patel A, Johnson R',
    year: 2023,
    abstract: '系统性回顾和荟萃分析了索拉非尼在肝细胞癌治疗中的疗效和安全性。分析了来自15个随机对照试验的数据，证实索拉非尼能显著延长晚期肝癌患者的总生存期。',
    keywords: ['索拉非尼', '肝细胞癌', '荟萃分析', '生存分析'],
    url: 'https://doi.org/10.1002/hep.32876'
  },
  {
    id: 'LIT003',
    title: 'Entecavir versus tenofovir in chronic hepatitis B: Long-term outcomes',
    authors: 'Park JH, Lee KM, Choi SY, Nam HC',
    year: 2023,
    abstract: '比较了恩替卡韦和替诺福韦在慢性乙型肝炎长期治疗中的疗效。10年随访结果显示两药在病毒学应答和肝硬化预防方面疗效相当，但安全性特征略有不同。',
    keywords: ['恩替卡韦', '替诺福韦', '慢性乙型肝炎', '长期随访'],
    url: 'https://doi.org/10.1053/j.gastro.2023.03.028'
  },
  {
    id: 'LIT004',
    title: 'Pirfenidone for liver fibrosis: Mechanisms and clinical evidence',
    authors: 'Thompson K, Garcia E, Brown D, Wilson J',
    year: 2024,
    abstract: '综述了吡非尼酮在肝纤维化治疗中的作用机制和临床证据。该药通过抑制TGF-β1和胶原合成发挥抗纤维化作用，多项临床试验显示其在改善肝纤维化方面的潜力。',
    keywords: ['吡非尼酮', '肝纤维化', '抗纤维化', 'TGF-β1'],
    url: 'https://doi.org/10.1016/j.jhep.2024.02.012'
  },
  {
    id: 'LIT005',
    title: 'PNPLA3 polymorphisms and liver disease susceptibility: A genome-wide association study',
    authors: 'Martinez A, Singh R, Kumar V, Anderson P',
    year: 2023,
    abstract: '大规模全基因组关联研究分析了PNPLA3基因多态性与肝病易感性的关系。发现rs738409变异显著增加脂肪肝、肝纤维化和肝细胞癌的风险。',
    keywords: ['PNPLA3', '基因多态性', '脂肪肝', 'GWAS'],
    url: 'https://doi.org/10.1038/s41588-023-01456-2'
  },
  {
    id: 'LIT006',
    title: 'Colchicine in liver fibrosis: Anti-inflammatory and antifibrotic effects',
    authors: 'Davis M, Liu X, Ahmed S, Taylor R',
    year: 2024,
    abstract: '研究了秋水仙碱在肝纤维化治疗中的抗炎和抗纤维化作用。体外和体内实验证实秋水仙碱能抑制肝星状细胞激活，减少胶原沉积，并改善肝功能。',
    keywords: ['秋水仙碱', '肝纤维化', '抗炎', '肝星状细胞'],
    url: 'https://doi.org/10.1002/hep.32945'
  },
  {
    id: 'LIT007',
    title: 'Ursodeoxycholic acid in primary biliary cholangitis: Updated guidelines',
    authors: 'European Association for Study of Liver',
    year: 2023,
    abstract: '更新了熊去氧胆酸在原发性胆汁性胆管炎治疗中的临床指南。推荐UDCA作为一线治疗药物，详细阐述了用药剂量、监测指标和联合治疗策略。',
    keywords: ['熊去氧胆酸', '原发性胆汁性胆管炎', '临床指南', 'UDCA'],
    url: 'https://doi.org/10.1016/j.jhep.2023.05.015'
  },
  {
    id: 'LIT008',
    title: 'Hepatic stellate cell activation in liver fibrosis: Molecular mechanisms',
    authors: 'Zhang Q, Wang L, Chen M, Li H',
    year: 2024,
    abstract: '深入分析了肝星状细胞激活在肝纤维化中的分子机制。重点阐述了TGF-β、PDGF和Wnt信号通路在HSC激活中的作用，为抗纤维化治疗提供新靶点。',
    keywords: ['肝星状细胞', '肝纤维化', 'TGF-β', 'PDGF'],
    url: 'https://doi.org/10.1053/j.gastro.2024.01.025'
  },
  {
    id: 'LIT009',
    title: 'Propranolol for portal hypertension: Efficacy and safety profile',
    authors: 'Gonzalez F, Smith J, Miller K, Jones B',
    year: 2023,
    abstract: '评估了普萘洛尔在门脉高压治疗中的疗效和安全性。研究显示普萘洛尔能有效降低门脉压力，减少食管静脉曲张出血风险，且耐受性良好。',
    keywords: ['普萘洛尔', '门脉高压', '食管静脉曲张', 'β受体阻滞剂'],
    url: 'https://doi.org/10.1002/hep.32823'
  },
  {
    id: 'LIT010',
    title: 'Machine learning approaches for hepatocellular carcinoma prediction',
    authors: 'AI Research Consortium',
    year: 2024,
    abstract: '开发了基于机器学习的肝细胞癌预测模型。整合了临床、影像学和分子标志物数据，构建了高精度的HCC风险预测算法，为早期诊断提供新工具。',
    keywords: ['机器学习', '肝细胞癌', '预测模型', '早期诊断'],
    url: 'https://doi.org/10.1038/s41591-024-02856-4'
  },
  {
    id: 'LIT011',
    title: 'Silymarin in drug-induced liver injury: Hepatoprotective mechanisms',
    authors: 'Kumar P, Zhao Y, Williams C, Jackson M',
    year: 2023,
    abstract: '研究了水飞蓟素在药物性肝损伤中的肝保护机制。发现水飞蓟素通过抗氧化、抗炎和膜稳定作用保护肝细胞，并能促进肝细胞再生。',
    keywords: ['水飞蓟素', '药物性肝损伤', '肝保护', '抗氧化'],
    url: 'https://doi.org/10.1016/j.jhep.2023.08.019'
  },
  {
    id: 'LIT012',
    title: 'ATP7B mutations in Wilson disease: Genotype-phenotype correlations',
    authors: 'European Wilson Disease Study Group',
    year: 2024,
    abstract: '分析了威尔逊病患者ATP7B基因突变的基因型-表型相关性。识别了超过500种ATP7B突变，建立了突变类型与临床表现的关联模式。',
    keywords: ['ATP7B', '威尔逊病', '基因突变', '基因型-表型'],
    url: 'https://doi.org/10.1002/hep.32967'
  },
  {
    id: 'LIT013',
    title: 'Lactulose in hepatic encephalopathy: Mechanisms and clinical outcomes',
    authors: 'Roberts S, Chang H, Patel N, Kumar A',
    year: 2023,
    abstract: '系统性评价了乳果糖在肝性脑病治疗中的作用机制和临床结局。乳果糖通过降低肠道pH值和减少氨吸收改善肝性脑病症状。',
    keywords: ['乳果糖', '肝性脑病', '氨代谢', '肠道菌群'],
    url: 'https://doi.org/10.1053/j.gastro.2023.06.042'
  },
  {
    id: 'LIT014',
    title: 'HFE gene mutations and iron overload in liver disease',
    authors: 'Iron Metabolism Research Network',
    year: 2024,
    abstract: '研究了HFE基因突变与肝病中铁过载的关系。C282Y和H63D突变显著增加肝铁沉积风险，加速肝纤维化进展，需要早期干预。',
    keywords: ['HFE基因', '铁过载', '血色病', '肝纤维化'],
    url: 'https://doi.org/10.1016/j.jhep.2024.03.008'
  },
  {
    id: 'LIT015',
    title: 'Interferon-based therapy for chronic hepatitis C: Historical perspective',
    authors: 'Hepatitis C Treatment Consortium',
    year: 2023,
    abstract: '回顾了干扰素治疗慢性丙型肝炎的历史发展。从单用干扰素到聚乙二醇干扰素联合利巴韦林，再到直接抗病毒药物时代的演变。',
    keywords: ['干扰素', '慢性丙型肝炎', '利巴韦林', '抗病毒治疗'],
    url: 'https://doi.org/10.1002/hep.32789'
  },
  {
    id: 'LIT016',
    title: 'Spironolactone and furosemide in cirrhotic ascites: Optimal dosing strategies',
    authors: 'Ascites Management Study Group',
    year: 2024,
    abstract: '优化了螺内酯和呋塞米在肝硬化腹水治疗中的剂量策略。研究确定了最佳的药物比例和递增方案，提高了治疗效果并减少了不良反应。',
    keywords: ['螺内酯', '呋塞米', '肝硬化腹水', '利尿剂'],
    url: 'https://doi.org/10.1053/j.gastro.2024.02.018'
  },
  {
    id: 'LIT017',
    title: 'L-carnitine supplementation in fatty liver disease: A randomized trial',
    authors: 'Metabolic Liver Disease Research Group',
    year: 2023,
    abstract: '随机对照试验评估了左卡尼汀补充在脂肪肝治疗中的作用。结果显示左卡尼汀能显著改善肝脂肪变性、炎症和胰岛素抵抗。',
    keywords: ['左卡尼汀', '脂肪肝', '随机对照试验', '胰岛素抵抗'],
    url: 'https://doi.org/10.1016/j.jhep.2023.09.021'
  },
  {
    id: 'LIT018',
    title: 'Glycyrrhizin in chronic hepatitis: Anti-inflammatory and antiviral effects',
    authors: 'Traditional Medicine Research Institute',
    year: 2024,
    abstract: '研究了甘草酸二铵在慢性肝炎治疗中的抗炎和抗病毒作用。甘草酸能抑制炎症因子释放，保护肝细胞膜稳定性，并具有一定的抗病毒活性。',
    keywords: ['甘草酸二铵', '慢性肝炎', '抗炎', '抗病毒'],
    url: 'https://doi.org/10.1002/hep.32978'
  },
  {
    id: 'LIT019',
    title: 'Glutathione in liver detoxification: Therapeutic implications',
    authors: 'Oxidative Stress Research Center',
    year: 2023,
    abstract: '综述了还原型谷胱甘肽在肝脏解毒中的作用及治疗意义。GSH是重要的抗氧化剂，在药物性肝损伤和肝功能不全的治疗中发挥关键作用。',
    keywords: ['还原型谷胱甘肽', '肝脏解毒', '抗氧化', '药物性肝损伤'],
    url: 'https://doi.org/10.1016/j.freeradbiomed.2023.07.015'
  },
  {
    id: 'LIT020',
    title: 'S-adenosylmethionine in intrahepatic cholestasis: Molecular mechanisms',
    authors: 'Cholestasis Research Network',
    year: 2024,
    abstract: '阐述了腺苷蛋氨酸在肝内胆汁淤积治疗中的分子机制。SAMe通过甲基化反应调节胆汁酸合成和转运，改善胆汁流动性。',
    keywords: ['腺苷蛋氨酸', '肝内胆汁淤积', '甲基化', '胆汁酸'],
    url: 'https://doi.org/10.1053/j.gastro.2024.01.035'
  },
  {
    id: 'LIT021',
    title: 'LOLA in hepatic encephalopathy: Ammonia detoxification pathways',
    authors: 'Neurohepatic Research Consortium',
    year: 2023,
    abstract: '研究了门冬氨酸鸟氨酸在肝性脑病中的氨解毒途径。LOLA通过激活尿素循环和谷氨酰胺合成酶降低血氨水平，改善神经精神症状。',
    keywords: ['门冬氨酸鸟氨酸', '肝性脑病', '氨解毒', '尿素循环'],
    url: 'https://doi.org/10.1002/hep.32856'
  },
  {
    id: 'LIT022',
    title: 'Phosphatidylcholine in liver regeneration: Membrane repair mechanisms',
    authors: 'Liver Regeneration Study Group',
    year: 2024,
    abstract: '探讨了多烯磷脂酰胆碱在肝再生中的膜修复机制。PC通过维持细胞膜完整性、调节膜流动性和促进肝细胞增殖发挥保肝作用。',
    keywords: ['多烯磷脂酰胆碱', '肝再生', '膜修复', '细胞膜'],
    url: 'https://doi.org/10.1016/j.jhep.2024.04.012'
  },
  {
    id: 'LIT023',
    title: 'Artificial intelligence in liver disease diagnosis: Deep learning approaches',
    authors: 'AI in Medicine Consortium',
    year: 2024,
    abstract: '综述了人工智能在肝病诊断中的深度学习方法。包括影像学AI诊断、病理学自动分析和多组学数据整合，显著提高了诊断准确性。',
    keywords: ['人工智能', '肝病诊断', '深度学习', '影像学'],
    url: 'https://doi.org/10.1038/s41591-024-02945-6'
  },
  {
    id: 'LIT024',
    title: 'Biomarkers for liver fibrosis: From serum markers to imaging',
    authors: 'Fibrosis Biomarker Research Network',
    year: 2023,
    abstract: '系统性回顾了肝纤维化的生物标志物，从血清标志物到影像学评估。包括透明质酸、IV型胶原、FibroScan等非侵入性诊断方法的进展。',
    keywords: ['生物标志物', '肝纤维化', '透明质酸', 'FibroScan'],
    url: 'https://doi.org/10.1002/hep.32834'
  },
  {
    id: 'LIT025',
    title: 'Precision medicine in hepatology: Genomics and personalized therapy',
    authors: 'Precision Hepatology Initiative',
    year: 2024,
    abstract: '探讨了精准医学在肝病学中的应用。通过基因组学分析实现个体化治疗，包括药物基因组学指导用药和基因治疗的最新进展。',
    keywords: ['精准医学', '肝病学', '基因组学', '个体化治疗'],
    url: 'https://doi.org/10.1016/j.jhep.2024.05.018'
  }
])

// 计算属性
const getCurrentTab = () => tabs.find(tab => tab.id === activeTab.value)

const filteredDrugs = computed(() => {
  return drugs.value.filter(drug => 
    drug.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    drug.mechanism.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const filteredDiseases = computed(() => {
  return diseases.value.filter(disease => 
    disease.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    disease.category.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const filteredGenes = computed(() => {
  return genes.value.filter(gene => 
    gene.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    gene.function.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const filteredLiterature = computed(() => {
  return literature.value.filter(paper => 
    paper.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    paper.abstract.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

// 方法
const exportData = () => {
  console.log('导出数据:', activeTab.value)
}

const addToComparison = (drug) => {
  console.log('添加到对比:', drug.name)
}
</script>

<script>
// 图标组件
const PillIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 0 1-.659 1.591L5 14.5a2.25 2.25 0 0 1-3.182 0 2.25 2.25 0 0 1 0-3.182l4.091-4.091A2.25 2.25 0 0 1 7.5 6.568V3.104a48.524 48.524 0 0 1 2.25-.546Z" /></svg>`
}

const HeartIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" /></svg>`
}

const DNAIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 0 1-.659 1.591L5 14.5a2.25 2.25 0 0 1-3.182 0 2.25 2.25 0 0 1 0-3.182l4.091-4.091A2.25 2.25 0 0 1 7.5 6.568V3.104a48.524 48.524 0 0 1 2.25-.546Z" /></svg>`
}

const BookIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25" /></svg>`
}

export default {
  components: {
    PillIcon,
    HeartIcon,
    DNAIcon,
    BookIcon
  }
}
</script>
