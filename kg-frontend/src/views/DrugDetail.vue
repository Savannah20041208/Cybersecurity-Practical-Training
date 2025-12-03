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
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-600">正在加载药物信息...</p>
        </div>
      </div>

      <div v-else-if="drug" class="space-y-8">
        <!-- 药物基本信息 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-8 text-white">
            <div class="flex items-center gap-4">
              <div class="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
                <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div>
                <h1 class="text-3xl font-bold mb-2">{{ drug.name }}</h1>
                <p class="text-blue-100">{{ drug.genericName }}</p>
                <div class="flex gap-2 mt-3">
                  <span class="bg-white/20 px-3 py-1 rounded-full text-sm">{{ drug.drugClass }}</span>
                  <span class="bg-white/20 px-3 py-1 rounded-full text-sm">{{ drug.status }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="p-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h3 class="font-semibold text-gray-800 mb-2">基本信息</h3>
                <div class="space-y-2 text-sm">
                  <div><span class="text-gray-500">药物ID:</span> {{ drug.id }}</div>
                  <div><span class="text-gray-500">分子式:</span> {{ drug.formula }}</div>
                  <div><span class="text-gray-500">分子量:</span> {{ drug.molecularWeight }}</div>
                  <div><span class="text-gray-500">CAS号:</span> {{ drug.casNumber }}</div>
                </div>
              </div>
              
              <div>
                <h3 class="font-semibold text-gray-800 mb-2">药理信息</h3>
                <div class="space-y-2 text-sm">
                  <div><span class="text-gray-500">作用机制:</span> {{ drug.mechanism }}</div>
                  <div><span class="text-gray-500">半衰期:</span> {{ drug.halfLife }}</div>
                  <div><span class="text-gray-500">生物利用度:</span> {{ drug.bioavailability }}</div>
                  <div><span class="text-gray-500">代谢途径:</span> {{ drug.metabolism }}</div>
                </div>
              </div>
              
              <div>
                <h3 class="font-semibold text-gray-800 mb-2">临床信息</h3>
                <div class="space-y-2 text-sm">
                  <div><span class="text-gray-500">FDA批准:</span> {{ drug.fdaApproval }}</div>
                  <div><span class="text-gray-500">给药途径:</span> {{ drug.administration }}</div>
                  <div><span class="text-gray-500">剂型:</span> {{ drug.dosageForm }}</div>
                  <div><span class="text-gray-500">处方类型:</span> {{ drug.prescriptionType }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分子结构 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">分子结构</h2>
          <div class="flex flex-col lg:flex-row gap-6">
            <div class="lg:w-1/2">
              <div class="bg-gray-50 rounded-lg p-4">
                <div class="bg-white rounded-lg shadow-inner p-4">
                  <!-- 分子结构图 -->
                  <div class="w-full h-80 flex items-center justify-center">
                    <MolecularStructure :drugId="drug.id" :drugName="drug.name" />
                  </div>
                  <!-- 分子结构控制按钮 -->
                  <div class="flex justify-center gap-2 mt-4">
                    <button @click="rotateMolecule" class="px-3 py-1 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors text-sm">
                      旋转
                    </button>
                    <button @click="resetMolecule" class="px-3 py-1 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors text-sm">
                      重置
                    </button>
                    <button @click="downloadStructure" class="px-3 py-1 bg-green-100 text-green-700 rounded-md hover:bg-green-200 transition-colors text-sm">
                      下载
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div class="lg:w-1/2">
              <h3 class="font-semibold text-gray-800 mb-3">结构特征</h3>
              <div class="space-y-3 text-sm">
                <div class="bg-gray-50 p-3 rounded-lg">
                  <span class="font-medium">SMILES:</span>
                  <code class="block mt-1 text-xs bg-white p-2 rounded border">{{ drug.smiles }}</code>
                </div>
                <div class="bg-gray-50 p-3 rounded-lg">
                  <span class="font-medium">InChI:</span>
                  <code class="block mt-1 text-xs bg-white p-2 rounded border break-all">{{ drug.inchi }}</code>
                </div>
                <div class="grid grid-cols-2 gap-3">
                  <div><span class="text-gray-500">氢键供体:</span> {{ drug.hbondDonors }}</div>
                  <div><span class="text-gray-500">氢键受体:</span> {{ drug.hbondAcceptors }}</div>
                  <div><span class="text-gray-500">可旋转键:</span> {{ drug.rotatableBonds }}</div>
                  <div><span class="text-gray-500">拓扑极性表面积:</span> {{ drug.tpsa }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 适应症和疾病关联 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">适应症与疾病关联</h2>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 class="font-semibold text-gray-800 mb-3">已批准适应症</h3>
              <div class="space-y-2">
                <div v-for="indication in drug.approvedIndications" :key="indication.id" 
                     class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <div class="font-medium text-green-800">{{ indication.disease }}</div>
                    <div class="text-sm text-green-600">{{ indication.description }}</div>
                  </div>
                  <router-link :to="`/disease/${indication.diseaseId}`" 
                               class="text-green-600 hover:text-green-800 text-sm">
                    查看详情
                  </router-link>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="font-semibold text-gray-800 mb-3">潜在重定位机会</h3>
              <div class="space-y-2">
                <div v-for="opportunity in drug.repositioningOpportunities" :key="opportunity.id" 
                     class="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <div>
                    <div class="font-medium text-blue-800">{{ opportunity.disease }}</div>
                    <div class="text-sm text-blue-600">置信度: {{ opportunity.confidence }}%</div>
                  </div>
                  <div class="text-right">
                    <div class="text-sm font-medium text-blue-800">{{ opportunity.evidence }}</div>
                    <div class="text-xs text-blue-600">{{ opportunity.source }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 靶点信息 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">靶点信息</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">靶点名称</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">作用方式</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">亲和力</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">证据</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="target in drug.targets" :key="target.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{{ target.name }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ target.type }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ target.action }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ target.affinity }}</td>
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

        <!-- 副作用和安全性 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">副作用与安全性</h2>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 class="font-semibold text-gray-800 mb-3">常见副作用</h3>
              <div class="space-y-2">
                <div v-for="sideEffect in drug.sideEffects" :key="sideEffect.name" 
                     class="flex items-center justify-between p-2 rounded">
                  <span class="text-sm">{{ sideEffect.name }}</span>
                  <div class="flex items-center gap-2">
                    <div class="w-16 bg-gray-200 rounded-full h-2">
                      <div class="bg-orange-500 h-2 rounded-full" :style="{ width: sideEffect.frequency + '%' }"></div>
                    </div>
                    <span class="text-xs text-gray-500">{{ sideEffect.frequency }}%</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h3 class="font-semibold text-gray-800 mb-3">安全性警告</h3>
              <div class="space-y-2">
                <div v-for="warning in drug.warnings" :key="warning.type" 
                     class="p-3 rounded-lg" :class="[
                       warning.severity === 'High' ? 'bg-red-50 border border-red-200' :
                       warning.severity === 'Medium' ? 'bg-yellow-50 border border-yellow-200' :
                       'bg-blue-50 border border-blue-200'
                     ]">
                  <div class="flex items-start gap-2">
                    <svg class="w-5 h-5 mt-0.5" :class="[
                           warning.severity === 'High' ? 'text-red-500' :
                           warning.severity === 'Medium' ? 'text-yellow-500' :
                           'text-blue-500'
                         ]" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                    </svg>
                    <div>
                      <div class="font-medium" :class="[
                             warning.severity === 'High' ? 'text-red-800' :
                             warning.severity === 'Medium' ? 'text-yellow-800' :
                             'text-blue-800'
                           ]">{{ warning.type }}</div>
                      <div class="text-sm" :class="[
                             warning.severity === 'High' ? 'text-red-600' :
                             warning.severity === 'Medium' ? 'text-yellow-600' :
                             'text-blue-600'
                           ]">{{ warning.description }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 相关文献 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">相关文献</h2>
          <div class="space-y-4">
            <div v-for="paper in drug.relatedPapers" :key="paper.id" 
                 class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div class="flex justify-between items-start mb-2">
                <h3 class="font-semibold text-gray-900">{{ paper.title }}</h3>
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

      <div v-else class="text-center py-20">
        <div class="text-gray-400 mb-4">
          <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0118 12a8 8 0 00-8-8 8 8 0 00-8 8c0 2.485.953 4.743 2.51 6.42l1.49 2.08L12 22l6-1.5 1.49-2.08A7.962 7.962 0 0021 12a8 8 0 00-8-8z"></path>
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-gray-800 mb-2">未找到药物信息</h2>
        <p class="text-gray-600">请检查药物ID是否正确，或返回重新搜索。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import MolecularStructure from '../components/MolecularStructure.vue'

const route = useRoute()
const loading = ref(true)
const drug = ref(null)
const moleculeRotation = ref(0)

// 模拟药物数据库
const drugDatabase = {
  'DRUG001': {
    id: 'DRUG001',
    name: '恩替卡韦',
    genericName: 'Entecavir',
    drugClass: '核苷类逆转录酶抑制剂',
    status: 'FDA已批准',
    formula: 'C12H15N5O3',
    molecularWeight: '277.28 g/mol',
    casNumber: '142217-69-4',
    mechanism: '核苷类逆转录酶抑制剂',
    halfLife: '128-149小时',
    bioavailability: '100%',
    metabolism: '肾脏排泄',
    fdaApproval: '2005年',
    administration: '口服',
    dosageForm: '片剂',
    prescriptionType: '处方药',
    smiles: 'C1=NC2=C(N1[C@H]3[C@@H]([C@H]([C@H](O3)CO)O)O)N=CN=C2N',
    inchi: 'InChI=1S/C12H15N5O3/c13-10-8-11(15-3-14-10)17(4-16-8)12-9(19)6(18)5(2-1-20)7(12)21/h3-7,9,12,18-21H,1-2H2,(H2,13,14,15)',
    hbondDonors: 4,
    hbondAcceptors: 6,
    rotatableBonds: 3,
    tpsa: '104.6 Ų',
    approvedIndications: [
      {
        id: 1,
        disease: '慢性乙型肝炎',
        diseaseId: 'DIS004',
        description: 'HBeAg阳性和阴性的慢性乙型肝炎'
      },
      {
        id: 2,
        disease: '肝硬化',
        diseaseId: 'DIS002',
        description: '乙肝相关肝硬化的治疗'
      }
    ],
    repositioningOpportunities: [
      {
        id: 1,
        disease: '肝纤维化',
        confidence: 85,
        evidence: '抗病毒作用',
        source: '临床研究'
      },
      {
        id: 2,
        disease: '肝细胞癌预防',
        confidence: 72,
        evidence: '病毒抑制',
        source: '队列研究'
      }
    ],
    targets: [
      {
        id: 1,
        name: 'HBV聚合酶',
        type: '逆转录酶',
        action: '抑制',
        affinity: 'IC50: 0.004 μM',
        evidenceLevel: 'High'
      },
      {
        id: 2,
        name: 'HBV DNA聚合酶',
        type: '酶',
        action: '竞争性抑制',
        affinity: 'Ki: 0.0012 μM',
        evidenceLevel: 'High'
      }
    ],
    sideEffects: [
      { name: '头痛', frequency: 9 },
      { name: '疲劳', frequency: 6 },
      { name: '眩晕', frequency: 4 },
      { name: '恶心', frequency: 3 }
    ],
    warnings: [
      {
        type: '肾功能监测',
        severity: 'Medium',
        description: '需要定期监测肾功能，调整剂量'
      },
      {
        type: '停药反弹',
        severity: 'High',
        description: '突然停药可能导致肝炎急性加重'
      }
    ],
    relatedPapers: [
      {
        id: 1,
        title: 'Entecavir versus tenofovir in chronic hepatitis B: Long-term outcomes',
        authors: 'Park JH, Lee KM, Choi SY, Nam HC',
        year: 2023,
        abstract: '比较了恩替卡韦和替诺福韦在慢性乙型肝炎长期治疗中的疗效。10年随访结果显示两药在病毒学应答和肝硬化预防方面疗效相当，但安全性特征略有不同。恩替卡韦在肾功能保护方面表现更佳。',
        keywords: ['恩替卡韦', '替诺福韦', '慢性乙型肝炎', '长期随访'],
        url: 'https://doi.org/10.1053/j.gastro.2023.03.028'
      },
      {
        id: 2,
        title: 'Efficacy and safety of entecavir in treatment-naïve patients with hepatitis B-related decompensated cirrhosis',
        authors: 'Liaw YF, Sheen IS, Lee CM, Akarca US, Papatheodoridis GV',
        year: 2024,
        abstract: '研究了恩替卡韦在乙肝相关失代偿性肝硬化初治患者中的疗效和安全性。结果显示恩替卡韦能显著改善肝功能，降低肝脏相关事件发生率，且安全性良好。48周治疗后，67%患者获得病毒学应答。',
        keywords: ['恩替卡韦', '失代偿性肝硬化', '乙型肝炎', '安全性'],
        url: 'https://doi.org/10.1002/hep.32945'
      },
      {
        id: 3,
        title: 'Entecavir resistance in chronic hepatitis B patients: mechanisms and clinical implications',
        authors: 'Zoulim F, Locarnini S, Hepatitis B Virus Resistance Study Group',
        year: 2023,
        abstract: '系统分析了慢性乙型肝炎患者中恩替卡韦耐药的机制和临床意义。研究发现恩替卡韦耐药主要与既往拉米夫定治疗史相关，耐药率在初治患者中极低（<1%），但在拉米夫定耐药患者中可达1.2%。',
        keywords: ['恩替卡韦', '耐药性', '拉米夫定', '基因型'],
        url: 'https://doi.org/10.1016/j.antiviral.2023.105621'
      },
      {
        id: 4,
        title: 'Real-world effectiveness of entecavir in preventing hepatocellular carcinoma: A systematic review',
        authors: 'Kim BK, Revill PA, Ahn SH, International HBV Research Consortium',
        year: 2024,
        abstract: '系统性回顾了恩替卡韦在预防肝细胞癌方面的真实世界有效性。荟萃分析显示，恩替卡韦治疗可显著降低HCC发生风险（HR=0.63, 95%CI: 0.52-0.76），特别是在肝硬化患者中效果更为显著。',
        keywords: ['恩替卡韦', '肝细胞癌', '预防', '真实世界研究'],
        url: 'https://doi.org/10.1016/j.jhep.2024.02.018'
      },
      {
        id: 5,
        title: 'Pharmacokinetics and pharmacodynamics of entecavir in patients with varying degrees of hepatic impairment',
        authors: 'Fontana RJ, Hann HW, Perrillo RP, Vierling JM, Wright T',
        year: 2023,
        abstract: '研究了不同程度肝功能损害患者中恩替卡韦的药代动力学和药效学特征。结果显示轻度肝功能损害患者无需调整剂量，中度损害患者需减量50%，重度损害患者需减量75%。',
        keywords: ['恩替卡韦', '药代动力学', '肝功能损害', '剂量调整'],
        url: 'https://doi.org/10.1002/cpt.2891'
      },
      {
        id: 6,
        title: 'Entecavir monotherapy versus entecavir plus tenofovir combination in HBeAg-positive chronic hepatitis B',
        authors: 'Buti M, Tsai N, Petersen J, Flisiak R, Gurel S, Krastev Z',
        year: 2024,
        abstract: '比较了HBeAg阳性慢性乙型肝炎患者中恩替卡韦单药治疗与恩替卡韦联合替诺福韦治疗的疗效。48周结果显示联合治疗在病毒学应答率方面略有优势（89% vs 82%），但差异无统计学意义。',
        keywords: ['恩替卡韦', '联合治疗', 'HBeAg阳性', '病毒学应答'],
        url: 'https://doi.org/10.1053/j.gastro.2024.01.042'
      },
      {
        id: 7,
        title: 'Cost-effectiveness of entecavir versus other nucleos(t)ide analogues for chronic hepatitis B',
        authors: 'Wong GL, Chan HL, Mak CW, Lee SK, Ip ZM, Lam AT',
        year: 2023,
        abstract: '评估了恩替卡韦与其他核苷(酸)类似物治疗慢性乙型肝炎的成本效益。马尔可夫模型分析显示，恩替卡韦在预防肝硬化和肝癌方面具有良好的成本效益比，ICER为$28,450/QALY。',
        keywords: ['恩替卡韦', '成本效益', '核苷类似物', '经济学评价'],
        url: 'https://doi.org/10.1016/j.jval.2023.08.012'
      },
      {
        id: 8,
        title: 'Entecavir-induced lactic acidosis: case reports and literature review',
        authors: 'Chen CJ, Yang HI, Su J, Jen CL, You SL, Lu SN',
        year: 2023,
        abstract: '报告了恩替卡韦诱发乳酸性酸中毒的病例并进行文献回顾。虽然发生率极低（<0.1%），但临床医生需要警惕，特别是在有肝功能不全或肾功能损害的患者中。早期识别和停药是关键。',
        keywords: ['恩替卡韦', '乳酸性酸中毒', '不良反应', '病例报告'],
        url: 'https://doi.org/10.1002/hep.32756'
      }
    ]
  },
  'DRUG002': {
    id: 'DRUG002',
    name: '索拉非尼',
    genericName: 'Sorafenib',
    drugClass: '多激酶抑制剂',
    status: 'FDA已批准',
    formula: 'C21H16ClF3N4O3',
    molecularWeight: '464.83 g/mol',
    casNumber: '284461-73-0',
    mechanism: '多激酶抑制剂',
    halfLife: '25-48小时',
    bioavailability: '38-49%',
    metabolism: '肝脏CYP3A4代谢',
    fdaApproval: '2005年',
    administration: '口服',
    dosageForm: '片剂',
    prescriptionType: '处方药',
    smiles: 'CNC(=O)C1=CC=CC=C1C(=O)NC2=CC(=C(C=C2)OC3=CC=C(C=C3)C(F)(F)F)Cl',
    inchi: 'InChI=1S/C21H16ClF3N4O3/c1-26-20(31)15-4-2-3-5-16(15)19(30)28-14-8-9-18(17(22)11-14)32-13-6-7-12(10-13)21(23,24)25/h2-11H,1H3,(H,26,31)(H,28,30)',
    hbondDonors: 3,
    hbondAcceptors: 5,
    rotatableBonds: 5,
    tpsa: '92.4 Ų',
    approvedIndications: [
      {
        id: 1,
        disease: '肝细胞癌',
        diseaseId: 'DIS003',
        description: '不可切除的肝细胞癌'
      },
      {
        id: 2,
        disease: '肾细胞癌',
        diseaseId: 'DIS999',
        description: '晚期肾细胞癌'
      }
    ],
    repositioningOpportunities: [
      {
        id: 1,
        disease: '肝纤维化',
        confidence: 68,
        evidence: '抗血管生成',
        source: '体外研究'
      }
    ],
    targets: [
      {
        id: 1,
        name: 'VEGFR-2',
        type: '受体酪氨酸激酶',
        action: '抑制',
        affinity: 'IC50: 90 nM',
        evidenceLevel: 'High'
      },
      {
        id: 2,
        name: 'PDGFR-β',
        type: '受体酪氨酸激酶',
        action: '抑制',
        affinity: 'IC50: 57 nM',
        evidenceLevel: 'High'
      },
      {
        id: 3,
        name: 'RAF-1',
        type: '丝氨酸/苏氨酸激酶',
        action: '抑制',
        affinity: 'IC50: 6 nM',
        evidenceLevel: 'High'
      }
    ],
    sideEffects: [
      { name: '腹泻', frequency: 43 },
      { name: '疲劳', frequency: 46 },
      { name: '手足皮肤反应', frequency: 30 },
      { name: '皮疹', frequency: 19 },
      { name: '高血压', frequency: 17 }
    ],
    warnings: [
      {
        type: '心血管毒性',
        severity: 'High',
        description: '可能导致心肌缺血和心律失常'
      },
      {
        type: '出血风险',
        severity: 'High',
        description: '增加出血风险，特别是胃肠道出血'
      },
      {
        type: '肝毒性',
        severity: 'Medium',
        description: '需要定期监测肝功能'
      }
    ],
    relatedPapers: [
      {
        id: 1,
        title: 'Sorafenib in hepatocellular carcinoma: A systematic review and meta-analysis',
        authors: 'Rodriguez M, Kim S, Patel A, Johnson R',
        year: 2023,
        abstract: '系统性回顾和荟萃分析了索拉非尼在肝细胞癌治疗中的疗效和安全性。分析了来自15个随机对照试验的数据，证实索拉非尼能显著延长晚期肝癌患者的总生存期（中位OS: 10.7个月 vs 7.9个月，HR=0.69）。',
        keywords: ['索拉非尼', '肝细胞癌', '荟萃分析', '生存分析'],
        url: 'https://doi.org/10.1002/hep.32876'
      },
      {
        id: 2,
        title: 'Sorafenib versus placebo in patients with advanced hepatocellular carcinoma (SHARP trial): Final analysis',
        authors: 'Llovet JM, Ricci S, Mazzaferro V, Hilgard P, Gane E, Blanc JF',
        year: 2024,
        abstract: 'SHARP试验的最终分析结果显示，索拉非尼显著改善了晚期肝细胞癌患者的总生存期和无进展生存期。中位总生存期从7.9个月延长至10.7个月（HR=0.69, p<0.001），确立了索拉非尼作为HCC标准治疗的地位。',
        keywords: ['索拉非尼', 'SHARP试验', '晚期肝癌', '随机对照试验'],
        url: 'https://doi.org/10.1016/j.jhep.2024.01.028'
      },
      {
        id: 3,
        title: 'Real-world effectiveness and safety of sorafenib in Asian patients with hepatocellular carcinoma',
        authors: 'Cheng AL, Kang YK, Chen Z, Tsao CJ, Qin S, Kim JS',
        year: 2023,
        abstract: '亚洲人群中索拉非尼治疗肝细胞癌的真实世界研究。结果显示亚洲患者的中位生存期为6.5个月，略低于西方人群，但仍显著优于最佳支持治疗。手足皮肤反应发生率更高（45% vs 30%）。',
        keywords: ['索拉非尼', '亚洲人群', '真实世界研究', '种族差异'],
        url: 'https://doi.org/10.1002/ijc.34567'
      },
      {
        id: 4,
        title: 'Sorafenib-induced hand-foot skin reaction: mechanisms, management, and impact on treatment outcomes',
        authors: 'Lacouture ME, Wu S, Robert C, Atkins MB, Kong HH, Guitart J',
        year: 2024,
        abstract: '深入研究了索拉非尼诱发手足皮肤反应的机制、管理策略及其对治疗结局的影响。HFSR发生率约30-60%，通过预防性护理和剂量调整可有效管理。轻度HFSR与更好的治疗反应相关。',
        keywords: ['索拉非尼', '手足皮肤反应', '不良反应管理', '剂量调整'],
        url: 'https://doi.org/10.1200/JCO.2024.42.1234'
      },
      {
        id: 5,
        title: 'Combination therapy with sorafenib and immune checkpoint inhibitors in hepatocellular carcinoma',
        authors: 'Finn RS, Qin S, Ikeda M, Galle PR, Ducreux M, Kim TY',
        year: 2024,
        abstract: '探讨了索拉非尼与免疫检查点抑制剂联合治疗肝细胞癌的可行性和疗效。初步结果显示联合治疗可提高客观缓解率（22% vs 12%），但毒性增加，需要仔细的患者选择和监测。',
        keywords: ['索拉非尼', '免疫治疗', '联合治疗', '肝细胞癌'],
        url: 'https://doi.org/10.1016/j.jhep.2024.03.015'
      },
      {
        id: 6,
        title: 'Pharmacokinetic drug interactions with sorafenib: clinical implications and management strategies',
        authors: 'van Leeuwen RW, Jansman FG, Hunfeld NG, Peric R, Reyners AK',
        year: 2023,
        abstract: '系统分析了索拉非尼的药物相互作用及其临床意义。索拉非尼主要通过CYP3A4代谢，与强效CYP3A4诱导剂（如利福平）联用时血药浓度可降低50%。建议避免与华法林、多西他赛等药物联用。',
        keywords: ['索拉非尼', '药物相互作用', 'CYP3A4', '药代动力学'],
        url: 'https://doi.org/10.1002/cpt.2945'
      },
      {
        id: 7,
        title: 'Biomarkers for predicting sorafenib response in hepatocellular carcinoma: current status and future directions',
        authors: 'Personeni N, Rimassa L, Santoro A, European HCC Research Network',
        year: 2024,
        abstract: '综述了预测索拉非尼治疗肝细胞癌疗效的生物标志物研究现状。AFP、VEGF、FGF19等血清标志物显示出一定的预测价值，但仍需要大规模前瞻性验证。精准医学方法有望改善患者选择。',
        keywords: ['索拉非尼', '生物标志物', '个体化治疗', '预测因子'],
        url: 'https://doi.org/10.1038/s41571-2024-00789-2'
      },
      {
        id: 8,
        title: 'Economic evaluation of sorafenib for advanced hepatocellular carcinoma: a systematic review',
        authors: 'Zhang Y, Chen X, Wang L, Liu H, International Health Economics Consortium',
        year: 2023,
        abstract: '系统评价了索拉非尼治疗晚期肝细胞癌的经济学价值。在大多数国家，索拉非尼的ICER超过了支付意愿阈值（$50,000-100,000/QALY）。仿制药的出现显著改善了成本效益比。',
        keywords: ['索拉非尼', '经济学评价', '成本效益', '卫生技术评估'],
        url: 'https://doi.org/10.1016/j.jval.2023.09.018'
      },
      {
        id: 9,
        title: 'Sorafenib resistance mechanisms in hepatocellular carcinoma: molecular insights and therapeutic implications',
        authors: 'Zhai B, Sun XY, Molecular Oncology Research Group',
        year: 2024,
        abstract: '深入分析了肝细胞癌中索拉非尼耐药的分子机制。主要耐药机制包括PI3K/AKT通路激活、上皮间质转化、血管生成重编程等。基于耐药机制的联合治疗策略正在临床试验中评估。',
        keywords: ['索拉非尼', '耐药机制', '分子机制', 'PI3K/AKT通路'],
        url: 'https://doi.org/10.1038/s41388-2024-02987-1'
      },
      {
        id: 10,
        title: 'Quality of life outcomes in patients with hepatocellular carcinoma treated with sorafenib: patient-reported experience',
        authors: 'Abou-Alfa GK, Johnson P, Knox JJ, Capanu M, Davidenko I',
        year: 2023,
        abstract: '评估了索拉非尼治疗肝细胞癌患者的生活质量。患者报告结局显示，虽然索拉非尼延长了生存期，但在治疗初期生活质量有所下降，主要与腹泻、疲劳等不良反应相关。适当的支持治疗可改善生活质量。',
        keywords: ['索拉非尼', '生活质量', '患者报告结局', '支持治疗'],
        url: 'https://doi.org/10.1200/JCO.2023.41.4567'
      }
    ]
  },
  'DRUG003': {
    id: 'DRUG003',
    name: '熊去氧胆酸',
    genericName: 'Ursodeoxycholic Acid',
    drugClass: '胆汁酸',
    status: 'FDA已批准',
    formula: 'C24H40O4',
    molecularWeight: '392.57 g/mol',
    casNumber: '128-13-2',
    mechanism: '胆汁酸替代疗法',
    halfLife: '3.5-5.8天',
    bioavailability: '90%',
    metabolism: '肠肝循环',
    fdaApproval: '1987年',
    administration: '口服',
    dosageForm: '胶囊、片剂',
    prescriptionType: '处方药',
    smiles: 'C[C@H](CCC(=O)O)[C@H]1CC[C@@H]2[C@@]1(CC[C@H]3[C@H]2[C@H](C[C@H]4[C@@]3(CC[C@H](C4)O)C)O)C',
    inchi: 'InChI=1S/C24H40O4/c1-14(4-7-22(27)28)17-5-6-18-16-13-21(26)19-12-15(25)8-10-24(19,3)20(16)9-11-23(17,18)2/h14-21,25-26H,4-13H2,1-3H3,(H,27,28)',
    hbondDonors: 3,
    hbondAcceptors: 4,
    rotatableBonds: 4,
    tpsa: '83.8 Ų',
    approvedIndications: [
      {
        id: 1,
        disease: '原发性胆汁性肝硬化',
        diseaseId: 'DIS009',
        description: '原发性胆汁性胆管炎的一线治疗'
      },
      {
        id: 2,
        disease: '胆石症',
        diseaseId: 'DIS998',
        description: '胆固醇性胆结石的溶解治疗'
      }
    ],
    repositioningOpportunities: [
      {
        id: 1,
        disease: '脂肪肝',
        confidence: 75,
        evidence: '改善脂质代谢',
        source: '临床试验'
      },
      {
        id: 2,
        disease: '肝纤维化',
        confidence: 68,
        evidence: '抗纤维化作用',
        source: '体外研究'
      }
    ],
    targets: [
      {
        id: 1,
        name: 'FXR',
        type: '核受体',
        action: '激活',
        affinity: 'EC50: 10 μM',
        evidenceLevel: 'High'
      },
      {
        id: 2,
        name: 'TGR5',
        type: 'G蛋白偶联受体',
        action: '激活',
        affinity: 'EC50: 5.4 μM',
        evidenceLevel: 'Medium'
      }
    ],
    sideEffects: [
      { name: '腹泻', frequency: 8 },
      { name: '便秘', frequency: 5 },
      { name: '恶心', frequency: 3 },
      { name: '腹痛', frequency: 4 }
    ],
    warnings: [
      {
        type: '肝功能恶化',
        severity: 'Medium',
        description: '极少数患者可能出现肝功能恶化'
      },
      {
        type: '胆结石钙化',
        severity: 'Low',
        description: '长期使用可能导致胆结石钙化'
      }
    ],
    relatedPapers: [
      {
        id: 1,
        title: 'Ursodeoxycholic acid in primary biliary cholangitis: Updated guidelines and clinical evidence',
        authors: 'European Association for Study of Liver',
        year: 2023,
        abstract: '更新了熊去氧胆酸在原发性胆汁性胆管炎治疗中的临床指南。推荐UDCA作为一线治疗药物，剂量为13-15mg/kg/day。长期治疗可显著改善生化指标和组织学，延缓疾病进展。',
        keywords: ['熊去氧胆酸', '原发性胆汁性胆管炎', '临床指南', 'UDCA'],
        url: 'https://doi.org/10.1016/j.jhep.2023.05.015'
      },
      {
        id: 2,
        title: 'Mechanisms of action of ursodeoxycholic acid in liver disease: from hepatoprotection to immunomodulation',
        authors: 'Poupon R, Chazouillères O, Corpechot C, Chrétien Y',
        year: 2024,
        abstract: '深入阐述了熊去氧胆酸在肝病中的作用机制。UDCA通过多种途径发挥作用：稳定细胞膜、抗凋亡、免疫调节、改善胆汁流动性等。这些机制解释了其在多种肝胆疾病中的疗效。',
        keywords: ['熊去氧胆酸', '作用机制', '肝保护', '免疫调节'],
        url: 'https://doi.org/10.1053/j.gastro.2024.02.025'
      },
      {
        id: 3,
        title: 'Ursodeoxycholic acid for nonalcoholic fatty liver disease: a systematic review and meta-analysis',
        authors: 'Ratziu V, Harrison SA, Francque S, Bedossa P, Lehert P',
        year: 2023,
        abstract: '系统性回顾和荟萃分析了UDCA治疗非酒精性脂肪肝病的疗效。分析显示UDCA可显著改善肝酶水平（ALT降低23.4 IU/L），但对肝脂肪变性和纤维化的改善有限。需要更大规模的研究验证。',
        keywords: ['熊去氧胆酸', '非酒精性脂肪肝', '荟萃分析', '肝酶'],
        url: 'https://doi.org/10.1002/hep.32834'
      },
      {
        id: 4,
        title: 'Long-term outcomes of ursodeoxycholic acid therapy in primary biliary cholangitis: 20-year follow-up study',
        authors: 'Corpechot C, Carrat F, Bahr A, Chrétien Y, Poupon RE, Poupon R',
        year: 2024,
        abstract: '20年长期随访研究评估了UDCA治疗原发性胆汁性胆管炎的长期结局。结果显示早期开始UDCA治疗的患者移植率显著降低（15% vs 35%），生存期明显延长。治疗应答者的预后更佳。',
        keywords: ['熊去氧胆酸', '长期随访', '肝移植', '生存分析'],
        url: 'https://doi.org/10.1016/j.jhep.2024.01.035'
      },
      {
        id: 5,
        title: 'Ursodeoxycholic acid and bezafibrate combination therapy in primary biliary cholangitis: the BEZURSO trial',
        authors: 'Corpechot C, Chazouillères O, Rousseau A, Le Gruyer A, Habersetzer F',
        year: 2023,
        abstract: 'BEZURSO试验评估了UDCA联合贝扎贝特治疗PBC的疗效。联合治疗组的生化应答率显著高于单药组（67% vs 31%），且安全性良好。联合治疗为UDCA应答不佳患者提供了新选择。',
        keywords: ['熊去氧胆酸', '贝扎贝特', '联合治疗', 'BEZURSO试验'],
        url: 'https://doi.org/10.1053/j.gastro.2023.08.042'
      },
      {
        id: 6,
        title: 'Pharmacokinetics and pharmacodynamics of ursodeoxycholic acid in patients with liver cirrhosis',
        authors: 'Kullak-Ublick GA, Stieger B, Hagenbuch B, Meier PJ',
        year: 2024,
        abstract: '研究了肝硬化患者中UDCA的药代动力学和药效学特征。肝硬化患者的UDCA清除率降低，血浆浓度升高，但治疗效果并未显著改变。建议根据Child-Pugh分级调整剂量。',
        keywords: ['熊去氧胆酸', '肝硬化', '药代动力学', '剂量调整'],
        url: 'https://doi.org/10.1002/hep.32967'
      },
      {
        id: 7,
        title: 'Ursodeoxycholic acid in pregnancy: safety profile and clinical applications',
        authors: 'Geenes V, Williamson C, Chappell LC, International ICP Research Network',
        year: 2023,
        abstract: '评估了UDCA在妊娠期的安全性和临床应用。UDCA是治疗妊娠期肝内胆汁淤积症的首选药物，可显著降低胎儿并发症风险。大规模队列研究证实其在妊娠期使用的安全性。',
        keywords: ['熊去氧胆酸', '妊娠期', '肝内胆汁淤积', '胎儿安全'],
        url: 'https://doi.org/10.1016/j.ajog.2023.09.015'
      },
      {
        id: 8,
        title: 'Novel formulations of ursodeoxycholic acid: improving bioavailability and patient compliance',
        authors: 'Fiorucci S, Distrutti E, Biagioli M, Zampella A, Ricci P',
        year: 2024,
        abstract: '开发了UDCA的新型制剂以改善生物利用度和患者依从性。缓释制剂可减少给药频次，提高患者依从性。纳米制剂显示出更好的溶解性和吸收性，有望提高治疗效果。',
        keywords: ['熊去氧胆酸', '新型制剂', '生物利用度', '患者依从性'],
        url: 'https://doi.org/10.1016/j.drudis.2024.03.008'
      }
    ]
  }
}

// 获取当前药物数据
const getCurrentDrug = (drugId) => {
  return drugDatabase[drugId] || drugDatabase['DRUG001'] // 默认返回恩替卡韦
}

// 分子结构控制函数
const rotateMolecule = () => {
  moleculeRotation.value += 90
  const moleculeElement = document.querySelector('.molecular-structure')
  if (moleculeElement) {
    moleculeElement.style.transform = `rotate(${moleculeRotation.value}deg)`
  }
}

const resetMolecule = () => {
  moleculeRotation.value = 0
  const moleculeElement = document.querySelector('.molecular-structure')
  if (moleculeElement) {
    moleculeElement.style.transform = 'rotate(0deg)'
  }
}

const downloadStructure = () => {
  // 创建一个简单的下载功能
  const svgElement = document.querySelector('.molecular-structure svg')
  if (svgElement) {
    const svgData = new XMLSerializer().serializeToString(svgElement)
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
    const svgUrl = URL.createObjectURL(svgBlob)
    
    const downloadLink = document.createElement('a')
    downloadLink.href = svgUrl
    downloadLink.download = `${drug.value?.name || 'molecule'}_structure.svg`
    document.body.appendChild(downloadLink)
    downloadLink.click()
    document.body.removeChild(downloadLink)
    URL.revokeObjectURL(svgUrl)
  }
}

onMounted(() => {
  // 模拟API调用
  setTimeout(() => {
    const drugId = route.params.id || 'DRUG001'
    drug.value = getCurrentDrug(drugId)
    loading.value = false
  }, 1000)
})
</script>
