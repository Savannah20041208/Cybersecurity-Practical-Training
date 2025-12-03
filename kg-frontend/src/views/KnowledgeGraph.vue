<template>
  <div class="p-6 md:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">知识图谱展示</h1>
        <p class="text-gray-600">可视化展示药物、疾病、靶点之间的关系图</p>
      </div>

      <!-- 控制面板 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <div class="flex flex-wrap gap-4 items-center">
          <!-- 搜索框 -->
          <div class="flex-1 min-w-64">
            <input
              v-model="searchQuery"
              @keyup.enter="searchNodes"
              type="text"
              placeholder="搜索药物或疾病..."
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <!-- 筛选选项 -->
          <div class="flex gap-2">
            <select v-model="selectedNodeType" @change="filterNodes" class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
              <option value="all">全部类型</option>
              <option value="drug">药物</option>
              <option value="disease">疾病</option>
              <option value="target">靶点</option>
              <option value="gene">基因</option>
              <option value="biomarker">生物标志物</option>
              <option value="pathway">信号通路</option>
            </select>
            
            <button
              @click="resetGraph"
              class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              重置
            </button>
            
            <button
              @click="searchNodes"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              搜索
            </button>
          </div>
        </div>
      </div>

      <!-- 图谱容器 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="p-4 border-b border-gray-100 flex justify-between items-center">
          <h3 class="font-semibold text-gray-800">关系图谱</h3>
          <div class="flex gap-2">
            <button
              @click="zoomIn"
              class="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="放大"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
            </button>
            <button
              @click="zoomOut"
              class="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="缩小"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 12H6"></path>
              </svg>
            </button>
            <button
              @click="rearrangeGraph"
              class="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
              title="重新布局"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
            </button>
            <div class="text-sm text-gray-500 px-2">
              缩放: {{ Math.round(zoomLevel * 100) }}%
            </div>
          </div>
        </div>
        
        <!-- 图谱画布 -->
        <div 
          ref="graphContainer" 
          class="relative bg-gray-50"
          style="height: 600px;"
        >
          <!-- 增强的知识图谱 -->
          <div v-if="!loading" class="absolute inset-0">
            <svg width="100%" height="100%" class="absolute inset-0" :style="{ transform: `scale(${zoomLevel})`, transformOrigin: 'center' }">
              <!-- 定义渐变和阴影效果 -->
              <defs>
                <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                  <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
                </filter>
                <linearGradient id="edgeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color:#e5e7eb;stop-opacity:0.8" />
                  <stop offset="100%" style="stop-color:#9ca3af;stop-opacity:0.8" />
                </linearGradient>
              </defs>
              
              <!-- 连接线层 -->
              <g class="edges-layer">
              <g v-for="edge in filteredEdges" :key="edge.id">
                  <!-- 主连接线 -->
                <line
                  :x1="edge.source.x"
                  :y1="edge.source.y"
                  :x2="edge.target.x"
                  :y2="edge.target.y"
                    stroke="url(#edgeGradient)"
                    :stroke-width="hoveredNode && (hoveredNode.id === edge.source.id || hoveredNode.id === edge.target.id) ? 3 : 2"
                    class="transition-all duration-300"
                    :class="{ 'opacity-30': hoveredNode && hoveredNode.id !== edge.source.id && hoveredNode.id !== edge.target.id }"
                  />
                  <!-- 箭头 -->
                  <polygon
                    :points="getArrowPoints(edge)"
                    fill="#9ca3af"
                    class="transition-all duration-300"
                    :class="{ 'opacity-30': hoveredNode && hoveredNode.id !== edge.source.id && hoveredNode.id !== edge.target.id }"
                  />
                  <!-- 关系标签背景 -->
                  <rect
                    :x="(edge.source.x + edge.target.x) / 2 - edge.relation.length * 3"
                    :y="(edge.source.y + edge.target.y) / 2 - 8"
                    :width="edge.relation.length * 6"
                    height="16"
                    fill="white"
                    fill-opacity="0.9"
                    rx="8"
                  class="transition-all duration-300"
                    :class="{ 'opacity-30': hoveredNode && hoveredNode.id !== edge.source.id && hoveredNode.id !== edge.target.id }"
                />
                  <!-- 关系标签 -->
                <text
                  :x="(edge.source.x + edge.target.x) / 2"
                    :y="(edge.source.y + edge.target.y) / 2 + 3"
                  text-anchor="middle"
                    class="text-xs fill-gray-600 font-medium transition-all duration-300"
                    :class="{ 'opacity-30': hoveredNode && hoveredNode.id !== edge.source.id && hoveredNode.id !== edge.target.id }"
                >
                  {{ edge.relation }}
                </text>
                </g>
              </g>
              
              <!-- 节点层 -->
              <g class="nodes-layer">
              <g v-for="node in filteredNodes" :key="node.id">
                  <!-- 节点阴影 -->
                  <circle
                    :cx="node.x + 2"
                    :cy="node.y + 2"
                    :r="node.radius"
                    fill="rgba(0,0,0,0.1)"
                    class="transition-all duration-300"
                  />
                  <!-- 主节点 -->
                <circle
                  :cx="node.x"
                  :cy="node.y"
                  :r="node.radius"
                  :fill="node.color"
                    :stroke="node.selected ? '#3b82f6' : (hoveredNode?.id === node.id ? '#f59e0b' : '#ffffff')"
                    :stroke-width="node.selected ? 4 : (hoveredNode?.id === node.id ? 3 : 2)"
                    class="cursor-pointer transition-all duration-300"
                    :class="{ 
                      'opacity-30': hoveredNode && hoveredNode.id !== node.id,
                      'transform scale-110': hoveredNode?.id === node.id,
                      'filter drop-shadow-lg': node.selected || hoveredNode?.id === node.id
                    }"
                  @click="selectNode(node)"
                    @mousedown="startDrag(node, $event)"
                    @mouseenter="handleNodeHover(node)"
                    @mouseleave="handleNodeLeave()"
                  />
                  <!-- 节点标签背景 -->
                  <rect
                    :x="node.x - Math.min(node.label.length * 3, 40)"
                    :y="node.y + node.radius + 5"
                    :width="Math.min(node.label.length * 6, 80)"
                    height="16"
                    fill="rgba(255,255,255,0.95)"
                    rx="8"
                    class="transition-all duration-300"
                    :class="{ 'opacity-30': hoveredNode && hoveredNode.id !== node.id }"
                  />
                  <!-- 节点标签 -->
                  <text
                    :x="node.x"
                    :y="node.y + node.radius + 15"
                    text-anchor="middle"
                    class="text-xs font-medium fill-gray-700 pointer-events-none transition-all duration-300"
                    :class="{ 'opacity-30': hoveredNode && hoveredNode.id !== node.id }"
                  >
                    {{ node.label.length > 10 ? node.label.substring(0, 10) + '...' : node.label }}
                  </text>
                  <!-- 节点类型图标 -->
                <text
                  :x="node.x"
                    :y="node.y + 3"
                  text-anchor="middle"
                    class="text-sm font-bold fill-white pointer-events-none"
                    :class="{ 'opacity-30': hoveredNode && hoveredNode.id !== node.id }"
                >
                    {{ getNodeIcon(node.type) }}
                </text>
                </g>
              </g>
            </svg>
            
            <!-- 悬停提示 -->
            <div
              v-if="hoveredNode"
              class="absolute bg-gray-900 text-white p-3 rounded-lg shadow-lg pointer-events-none z-10 max-w-xs"
              :style="{ 
                left: hoveredNode.x + 50 + 'px', 
                top: hoveredNode.y - 20 + 'px',
                transform: hoveredNode.x > 800 ? 'translateX(-100%)' : ''
              }"
            >
              <div class="font-semibold">{{ hoveredNode.label }}</div>
              <div class="text-xs text-gray-300 mt-1">{{ hoveredNode.description }}</div>
              <div class="text-xs text-blue-300 mt-1">类型: {{ getTypeLabel(hoveredNode.type) }}</div>
            </div>
          </div>
          
          <!-- 加载状态 -->
          <div v-if="loading" class="absolute inset-0 flex items-center justify-center">
            <div class="text-center">
              <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p class="text-gray-600">正在加载知识图谱...</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 节点详情面板 -->
      <div v-if="selectedNode" class="mt-6 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex justify-between items-start mb-4">
          <h3 class="text-xl font-bold text-gray-800">{{ selectedNode.label }}</h3>
          <button
            @click="selectedNode = null"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 class="font-semibold text-gray-700 mb-2">基本信息</h4>
            <div class="space-y-2 text-sm">
              <div><span class="text-gray-500">类型:</span> {{ selectedNode.type }}</div>
              <div><span class="text-gray-500">ID:</span> {{ selectedNode.id }}</div>
              <div v-if="selectedNode.description"><span class="text-gray-500">描述:</span> {{ selectedNode.description }}</div>
            </div>
          </div>
          
          <div>
            <h4 class="font-semibold text-gray-700 mb-2">关联关系</h4>
            <div class="space-y-1 text-sm">
              <div v-for="relation in getNodeRelations(selectedNode)" :key="relation.id" class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: relation.color }"></span>
                <span>{{ relation.relation }} {{ relation.target }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 图例 -->
      <div class="mt-6 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 class="font-semibold text-gray-800 mb-4">图例</h3>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded-full bg-blue-500"></div>
            <span class="text-sm text-gray-600">药物</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded-full bg-red-500"></div>
            <span class="text-sm text-gray-600">疾病</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded-full bg-green-500"></div>
            <span class="text-sm text-gray-600">靶点</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded-full bg-purple-500"></div>
            <span class="text-sm text-gray-600">基因</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded-full bg-yellow-500"></div>
            <span class="text-sm text-gray-600">生物标志物</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded-full bg-cyan-500"></div>
            <span class="text-sm text-gray-600">信号通路</span>
          </div>
        </div>
        
        <!-- 关系类型说明 -->
        <div class="mt-6 pt-4 border-t border-gray-100">
          <h4 class="font-medium text-gray-700 mb-3">关系类型</h4>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm text-gray-600">
            <div class="flex items-center gap-2">
              <div class="w-3 h-0.5 bg-gray-400"></div>
              <span>治疗/抑制</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-0.5 bg-gray-400"></div>
              <span>调控/激活</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-0.5 bg-gray-400"></div>
              <span>发展/进展</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-0.5 bg-gray-400"></div>
              <span>编码/表达</span>
            </div>
          </div>
        </div>
        
        <!-- 统计信息 -->
        <div class="mt-4 pt-4 border-t border-gray-100">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div class="bg-blue-50 rounded-lg p-3">
              <div class="text-2xl font-bold text-blue-600">{{ nodes.filter(n => n.type === 'drug').length }}</div>
              <div class="text-xs text-blue-600">药物</div>
            </div>
            <div class="bg-red-50 rounded-lg p-3">
              <div class="text-2xl font-bold text-red-600">{{ nodes.filter(n => n.type === 'disease').length }}</div>
              <div class="text-xs text-red-600">疾病</div>
            </div>
            <div class="bg-green-50 rounded-lg p-3">
              <div class="text-2xl font-bold text-green-600">{{ nodes.filter(n => n.type === 'target').length }}</div>
              <div class="text-xs text-green-600">靶点</div>
            </div>
            <div class="bg-purple-50 rounded-lg p-3">
              <div class="text-2xl font-bold text-purple-600">{{ edges.length }}</div>
              <div class="text-xs text-purple-600">关系</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const searchQuery = ref('')
const selectedNodeType = ref('all')
const selectedNode = ref(null)
const loading = ref(true)
const graphContainer = ref(null)
const zoomLevel = ref(1)
const isDragging = ref(false)
const draggedNode = ref(null)
const hoveredNode = ref(null)

// 真实的肝脏疾病药物重定位知识图谱数据
const nodes = ref([
  // 肝脏疾病
  { id: 'disease1', label: '肝纤维化', type: 'disease', x: 400, y: 300, radius: 35, color: '#ef4444', description: '肝脏纤维组织过度增生，可发展为肝硬化' },
  { id: 'disease2', label: '肝硬化', type: 'disease', x: 600, y: 400, radius: 35, color: '#dc2626', description: '慢性肝病的终末期表现' },
  { id: 'disease3', label: '肝细胞癌', type: 'disease', x: 800, y: 350, radius: 35, color: '#b91c1c', description: '原发性肝癌，预后较差' },
  { id: 'disease4', label: '脂肪肝', type: 'disease', x: 200, y: 250, radius: 30, color: '#f87171', description: '肝细胞内脂肪过度沉积' },
  { id: 'disease5', label: '肝炎', type: 'disease', x: 300, y: 150, radius: 30, color: '#fca5a5', description: '肝脏炎症性疾病' },
  { id: 'disease6', label: '门脉高压', type: 'disease', x: 700, y: 500, radius: 28, color: '#ef4444', description: '肝硬化常见并发症' },
  
  // 抗纤维化药物
  { id: 'drug1', label: '恩替卡韦', type: 'drug', x: 150, y: 350, radius: 28, color: '#3b82f6', description: '核苷类逆转录酶抑制剂，抗HBV' },
  { id: 'drug2', label: '索拉非尼', type: 'drug', x: 900, y: 250, radius: 28, color: '#2563eb', description: '多激酶抑制剂，治疗肝癌' },
  { id: 'drug3', label: '熊去氧胆酸', type: 'drug', x: 100, y: 200, radius: 26, color: '#1d4ed8', description: '胆汁酸，保肝利胆' },
  { id: 'drug4', label: '吡非尼酮', type: 'drug', x: 500, y: 150, radius: 26, color: '#1e40af', description: '抗纤维化药物' },
  { id: 'drug5', label: '秋水仙碱', type: 'drug', x: 350, y: 450, radius: 24, color: '#3730a3', description: '抗炎抗纤维化' },
  { id: 'drug6', label: '甲氨蝶呤', type: 'drug', x: 750, y: 200, radius: 24, color: '#312e81', description: '免疫抑制剂' },
  { id: 'drug7', label: '利巴韦林', type: 'drug', x: 250, y: 350, radius: 24, color: '#1e3a8a', description: '抗病毒药物' },
  { id: 'drug8', label: '普萘洛尔', type: 'drug', x: 800, y: 550, radius: 24, color: '#1e40af', description: 'β受体阻滞剂，降门脉压' },
  
  // 分子靶点
  { id: 'target1', label: 'TGF-β1', type: 'target', x: 450, y: 200, radius: 22, color: '#22c55e', description: '转化生长因子β1，关键纤维化因子' },
  { id: 'target2', label: 'PDGFR', type: 'target', x: 550, y: 250, radius: 22, color: '#16a34a', description: '血小板衍生生长因子受体' },
  { id: 'target3', label: 'VEGFR', type: 'target', x: 850, y: 300, radius: 22, color: '#15803d', description: '血管内皮生长因子受体' },
  { id: 'target4', label: 'mTOR', type: 'target', x: 700, y: 150, radius: 20, color: '#166534', description: '雷帕霉素靶蛋白' },
  { id: 'target5', label: 'NF-κB', type: 'target', x: 300, y: 250, radius: 20, color: '#14532d', description: '核因子κB，炎症调节' },
  { id: 'target6', label: 'HSCs', type: 'target', x: 400, y: 380, radius: 22, color: '#22c55e', description: '肝星状细胞，纤维化主要细胞' },
  { id: 'target7', label: 'Kupffer细胞', type: 'target', x: 200, y: 300, radius: 20, color: '#16a34a', description: '肝脏巨噬细胞' },
  
  // 关键基因
  { id: 'gene1', label: 'COL1A1', type: 'gene', x: 500, y: 350, radius: 18, color: '#a855f7', description: 'I型胶原α1链基因' },
  { id: 'gene2', label: 'ACTA2', type: 'gene', x: 450, y: 400, radius: 18, color: '#9333ea', description: 'α-平滑肌肌动蛋白基因' },
  { id: 'gene3', label: 'TIMP1', type: 'gene', x: 350, y: 350, radius: 18, color: '#7c3aed', description: '金属蛋白酶组织抑制因子1' },
  { id: 'gene4', label: 'MMP2', type: 'gene', x: 550, y: 400, radius: 18, color: '#6d28d9', description: '基质金属蛋白酶2' },
  { id: 'gene5', label: 'SMAD3', type: 'gene', x: 400, y: 250, radius: 18, color: '#5b21b6', description: 'TGF-β信号转导关键基因' },
  { id: 'gene6', label: 'TP53', type: 'gene', x: 750, y: 300, radius: 18, color: '#581c87', description: '肿瘤抑制基因p53' },
  { id: 'gene7', label: 'CTNNB1', type: 'gene', x: 800, y: 250, radius: 18, color: '#4c1d95', description: 'β-连环蛋白基因' },
  
  // 生物标志物
  { id: 'biomarker1', label: 'ALT', type: 'biomarker', x: 150, y: 150, radius: 16, color: '#f59e0b', description: '丙氨酸氨基转移酶' },
  { id: 'biomarker2', label: 'AST', type: 'biomarker', x: 200, y: 100, radius: 16, color: '#d97706', description: '天冬氨酸氨基转移酶' },
  { id: 'biomarker3', label: 'AFP', type: 'biomarker', x: 850, y: 200, radius: 16, color: '#b45309', description: '甲胎蛋白，肝癌标志物' },
  { id: 'biomarker4', label: '透明质酸', type: 'biomarker', x: 500, y: 450, radius: 16, color: '#92400e', description: '肝纤维化血清标志物' },
  { id: 'biomarker5', label: 'IV型胶原', type: 'biomarker', x: 450, y: 500, radius: 16, color: '#78350f', description: '纤维化标志物' },
  
  // 通路
  { id: 'pathway1', label: 'TGF-β通路', type: 'pathway', x: 350, y: 200, radius: 20, color: '#06b6d4', description: 'TGF-β信号转导通路' },
  { id: 'pathway2', label: 'Wnt通路', type: 'pathway', x: 750, y: 250, radius: 20, color: '#0891b2', description: 'Wnt/β-catenin信号通路' },
  { id: 'pathway3', label: 'PI3K/AKT通路', type: 'pathway', x: 650, y: 200, radius: 20, color: '#0e7490', description: 'PI3K/AKT信号通路' },
  { id: 'pathway4', label: 'NF-κB通路', type: 'pathway', x: 250, y: 200, radius: 20, color: '#155e75', description: 'NF-κB炎症通路' }
])

const edges = ref([
  // 疾病发展关系
  { id: 'e1', source: nodes.value.find(n => n.id === 'disease4'), target: nodes.value.find(n => n.id === 'disease1'), relation: '发展为' },
  { id: 'e2', source: nodes.value.find(n => n.id === 'disease5'), target: nodes.value.find(n => n.id === 'disease1'), relation: '导致' },
  { id: 'e3', source: nodes.value.find(n => n.id === 'disease1'), target: nodes.value.find(n => n.id === 'disease2'), relation: '进展为' },
  { id: 'e4', source: nodes.value.find(n => n.id === 'disease2'), target: nodes.value.find(n => n.id === 'disease3'), relation: '易发展为' },
  { id: 'e5', source: nodes.value.find(n => n.id === 'disease2'), target: nodes.value.find(n => n.id === 'disease6'), relation: '并发' },
  
  // 药物-疾病关系
  { id: 'e6', source: nodes.value.find(n => n.id === 'drug1'), target: nodes.value.find(n => n.id === 'disease5'), relation: '治疗' },
  { id: 'e7', source: nodes.value.find(n => n.id === 'drug2'), target: nodes.value.find(n => n.id === 'disease3'), relation: '治疗' },
  { id: 'e8', source: nodes.value.find(n => n.id === 'drug3'), target: nodes.value.find(n => n.id === 'disease4'), relation: '改善' },
  { id: 'e9', source: nodes.value.find(n => n.id === 'drug4'), target: nodes.value.find(n => n.id === 'disease1'), relation: '抗纤维化' },
  { id: 'e10', source: nodes.value.find(n => n.id === 'drug5'), target: nodes.value.find(n => n.id === 'disease1'), relation: '抑制' },
  { id: 'e11', source: nodes.value.find(n => n.id === 'drug7'), target: nodes.value.find(n => n.id === 'disease5'), relation: '抗病毒' },
  { id: 'e12', source: nodes.value.find(n => n.id === 'drug8'), target: nodes.value.find(n => n.id === 'disease6'), relation: '降压' },
  
  // 药物-靶点关系
  { id: 'e13', source: nodes.value.find(n => n.id === 'drug4'), target: nodes.value.find(n => n.id === 'target1'), relation: '抑制' },
  { id: 'e14', source: nodes.value.find(n => n.id === 'drug2'), target: nodes.value.find(n => n.id === 'target3'), relation: '阻断' },
  { id: 'e15', source: nodes.value.find(n => n.id === 'drug6'), target: nodes.value.find(n => n.id === 'target4'), relation: '抑制' },
  { id: 'e16', source: nodes.value.find(n => n.id === 'drug5'), target: nodes.value.find(n => n.id === 'target6'), relation: '抑制激活' },
  { id: 'e17', source: nodes.value.find(n => n.id === 'drug3'), target: nodes.value.find(n => n.id === 'target7'), relation: '调节' },
  
  // 靶点-基因关系
  { id: 'e18', source: nodes.value.find(n => n.id === 'target1'), target: nodes.value.find(n => n.id === 'gene5'), relation: '激活' },
  { id: 'e19', source: nodes.value.find(n => n.id === 'target6'), target: nodes.value.find(n => n.id === 'gene1'), relation: '上调' },
  { id: 'e20', source: nodes.value.find(n => n.id === 'target6'), target: nodes.value.find(n => n.id === 'gene2'), relation: '表达' },
  { id: 'e21', source: nodes.value.find(n => n.id === 'target2'), target: nodes.value.find(n => n.id === 'gene4'), relation: '调控' },
  { id: 'e22', source: nodes.value.find(n => n.id === 'target3'), target: nodes.value.find(n => n.id === 'gene6'), relation: '影响' },
  
  // 基因-生物标志物关系
  { id: 'e23', source: nodes.value.find(n => n.id === 'gene1'), target: nodes.value.find(n => n.id === 'biomarker5'), relation: '编码' },
  { id: 'e24', source: nodes.value.find(n => n.id === 'gene4'), target: nodes.value.find(n => n.id === 'biomarker4'), relation: '降解' },
  { id: 'e25', source: nodes.value.find(n => n.id === 'gene6'), target: nodes.value.find(n => n.id === 'biomarker3'), relation: '调控' },
  
  // 通路-靶点关系
  { id: 'e26', source: nodes.value.find(n => n.id === 'pathway1'), target: nodes.value.find(n => n.id === 'target1'), relation: '包含' },
  { id: 'e27', source: nodes.value.find(n => n.id === 'pathway2'), target: nodes.value.find(n => n.id === 'gene7'), relation: '调控' },
  { id: 'e28', source: nodes.value.find(n => n.id === 'pathway3'), target: nodes.value.find(n => n.id === 'target4'), relation: '激活' },
  { id: 'e29', source: nodes.value.find(n => n.id === 'pathway4'), target: nodes.value.find(n => n.id === 'target5'), relation: '调节' },
  
  // 疾病-生物标志物关系
  { id: 'e30', source: nodes.value.find(n => n.id === 'disease1'), target: nodes.value.find(n => n.id === 'biomarker4'), relation: '升高' },
  { id: 'e31', source: nodes.value.find(n => n.id === 'disease1'), target: nodes.value.find(n => n.id === 'biomarker5'), relation: '增加' },
  { id: 'e32', source: nodes.value.find(n => n.id === 'disease3'), target: nodes.value.find(n => n.id === 'biomarker3'), relation: '显著升高' },
  { id: 'e33', source: nodes.value.find(n => n.id === 'disease5'), target: nodes.value.find(n => n.id === 'biomarker1'), relation: '升高' },
  { id: 'e34', source: nodes.value.find(n => n.id === 'disease5'), target: nodes.value.find(n => n.id === 'biomarker2'), relation: '升高' },
  
  // 更多复杂关系
  { id: 'e35', source: nodes.value.find(n => n.id === 'target1'), target: nodes.value.find(n => n.id === 'pathway1'), relation: '激活' },
  { id: 'e36', source: nodes.value.find(n => n.id === 'gene5'), target: nodes.value.find(n => n.id === 'gene1'), relation: '上调' },
  { id: 'e37', source: nodes.value.find(n => n.id === 'gene3'), target: nodes.value.find(n => n.id === 'gene4'), relation: '抑制' },
  { id: 'e38', source: nodes.value.find(n => n.id === 'target6'), target: nodes.value.find(n => n.id === 'target1'), relation: '分泌' },
  { id: 'e39', source: nodes.value.find(n => n.id === 'pathway1'), target: nodes.value.find(n => n.id === 'gene2'), relation: '诱导' },
  { id: 'e40', source: nodes.value.find(n => n.id === 'drug4'), target: nodes.value.find(n => n.id === 'pathway1'), relation: '阻断' }
])

// 过滤后的节点和边
const filteredNodes = computed(() => {
  let filtered = nodes.value
  
  if (selectedNodeType.value !== 'all') {
    filtered = filtered.filter(node => node.type === selectedNodeType.value)
  }
  
  if (searchQuery.value) {
    filtered = filtered.filter(node => 
      node.label.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }
  
  return filtered
})

const filteredEdges = computed(() => {
  const nodeIds = new Set(filteredNodes.value.map(node => node.id))
  return edges.value.filter(edge => 
    nodeIds.has(edge.source.id) && nodeIds.has(edge.target.id)
  )
})

// 方法
const searchNodes = () => {
  // 实际应用中这里会调用API搜索
  console.log('搜索:', searchQuery.value)
}

const filterNodes = () => {
  // 过滤逻辑已在computed中处理
}

const resetGraph = () => {
  searchQuery.value = ''
  selectedNodeType.value = 'all'
  selectedNode.value = null
}

const selectNode = (node) => {
  // 重置所有节点的选中状态
  nodes.value.forEach(n => n.selected = false)
  // 选中当前节点
  node.selected = true
  selectedNode.value = node
}

const getNodeRelations = (node) => {
  return edges.value
    .filter(edge => edge.source.id === node.id || edge.target.id === node.id)
    .map(edge => ({
      id: edge.id,
      relation: edge.relation,
      target: edge.source.id === node.id ? edge.target.label : edge.source.label,
      color: edge.source.id === node.id ? edge.target.color : edge.source.color
    }))
}

const zoomIn = () => {
  if (zoomLevel.value < 3) {
    zoomLevel.value += 0.2
    updateNodePositions()
  }
}

const zoomOut = () => {
  if (zoomLevel.value > 0.5) {
    zoomLevel.value -= 0.2
    updateNodePositions()
  }
}

const updateNodePositions = () => {
  // 根据缩放级别更新节点位置
  nodes.value.forEach(node => {
    node.displayX = node.x * zoomLevel.value
    node.displayY = node.y * zoomLevel.value
    node.displayRadius = node.radius * zoomLevel.value
  })
}

// 节点拖拽功能
const startDrag = (node, event) => {
  isDragging.value = true
  draggedNode.value = node
  
  const rect = graphContainer.value.getBoundingClientRect()
  const offsetX = event.clientX - rect.left - node.x
  const offsetY = event.clientY - rect.top - node.y
  
  const handleMouseMove = (e) => {
    if (isDragging.value && draggedNode.value) {
      const newX = e.clientX - rect.left - offsetX
      const newY = e.clientY - rect.top - offsetY
      
      // 限制在容器范围内
      draggedNode.value.x = Math.max(draggedNode.value.radius, Math.min(1000 - draggedNode.value.radius, newX))
      draggedNode.value.y = Math.max(draggedNode.value.radius, Math.min(600 - draggedNode.value.radius, newY))
    }
  }
  
  const handleMouseUp = () => {
    isDragging.value = false
    draggedNode.value = null
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

// 节点悬停效果
const handleNodeHover = (node) => {
  hoveredNode.value = node
}

const handleNodeLeave = () => {
  hoveredNode.value = null
}

// 自动布局算法 - 力导向布局
const applyForceLayout = () => {
  const iterations = 100
  const repulsionForce = 5000
  const attractionForce = 0.01
  const damping = 0.9
  
  for (let iter = 0; iter < iterations; iter++) {
    // 计算排斥力
    nodes.value.forEach(node => {
      node.vx = node.vx || 0
      node.vy = node.vy || 0
      
      nodes.value.forEach(otherNode => {
        if (node !== otherNode) {
          const dx = node.x - otherNode.x
          const dy = node.y - otherNode.y
          const distance = Math.sqrt(dx * dx + dy * dy) || 1
          const force = repulsionForce / (distance * distance)
          
          node.vx += (dx / distance) * force
          node.vy += (dy / distance) * force
        }
      })
    })
    
    // 计算连接的吸引力
    edges.value.forEach(edge => {
      const dx = edge.target.x - edge.source.x
      const dy = edge.target.y - edge.source.y
      const distance = Math.sqrt(dx * dx + dy * dy)
      const force = distance * attractionForce
      
      edge.source.vx += (dx / distance) * force
      edge.source.vy += (dy / distance) * force
      edge.target.vx -= (dx / distance) * force
      edge.target.vy -= (dy / distance) * force
    })
    
    // 更新位置并应用阻尼
    nodes.value.forEach(node => {
      node.vx *= damping
      node.vy *= damping
      node.x += node.vx
      node.y += node.vy
      
      // 边界约束
      node.x = Math.max(node.radius, Math.min(1000 - node.radius, node.x))
      node.y = Math.max(node.radius, Math.min(600 - node.radius, node.y))
    })
  }
}

// 重新排列图谱
const rearrangeGraph = () => {
  loading.value = true
  setTimeout(() => {
    applyForceLayout()
    updateNodePositions()
    loading.value = false
  }, 500)
}

// 辅助函数
const getNodeIcon = (type) => {
  const icons = {
    drug: '💊',
    disease: '🦠', 
    target: '🎯',
    gene: '🧬',
    biomarker: '📊',
    pathway: '🔄'
  }
  return icons[type] || '●'
}

const getTypeLabel = (type) => {
  const labels = {
    drug: '药物',
    disease: '疾病',
    target: '靶点', 
    gene: '基因',
    biomarker: '生物标志物',
    pathway: '信号通路'
  }
  return labels[type] || type
}

const getArrowPoints = (edge) => {
  const dx = edge.target.x - edge.source.x
  const dy = edge.target.y - edge.source.y
  const length = Math.sqrt(dx * dx + dy * dy)
  const unitX = dx / length
  const unitY = dy / length
  
  // 箭头位置（在目标节点边缘）
  const arrowX = edge.target.x - unitX * (edge.target.radius + 5)
  const arrowY = edge.target.y - unitY * (edge.target.radius + 5)
  
  // 箭头大小
  const arrowSize = 8
  const perpX = -unitY * arrowSize / 2
  const perpY = unitX * arrowSize / 2
  
  return `${arrowX - unitX * arrowSize},${arrowY - unitY * arrowSize} 
          ${arrowX + perpX},${arrowY + perpY} 
          ${arrowX - perpX},${arrowY - perpY}`
}

onMounted(() => {
  // 初始化图谱
  setTimeout(() => {
    updateNodePositions()
    loading.value = false
  }, 1500)
})
</script>
