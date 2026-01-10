<template>
  <div class="p-6 md:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">知识图谱展示</h1>
        <p class="text-gray-600">基于Neo4j医疗数据的可视化关系图谱</p>
      </div>

      <!-- 统计信息面板 -->
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 mb-6">
        <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-4 text-center">
          <div class="text-2xl font-bold text-red-600">1653</div>
          <div class="text-sm text-gray-600">疾病</div>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-4 text-center">
          <div class="text-2xl font-bold text-amber-600">2341</div>
          <div class="text-sm text-gray-600">症状</div>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-4 text-center">
          <div class="text-2xl font-bold text-blue-600">2847</div>
          <div class="text-sm text-gray-600">药物</div>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-4 text-center">
          <div class="text-2xl font-bold text-green-600">892</div>
          <div class="text-sm text-gray-600">靶点</div>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-4 text-center">
          <div class="text-2xl font-bold text-purple-600">1247</div>
          <div class="text-sm text-gray-600">基因</div>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-4 text-center">
          <div class="text-2xl font-bold text-pink-600">567</div>
          <div class="text-sm text-gray-600">通路</div>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-4 text-center">
          <div class="text-2xl font-bold text-gray-600">423</div>
          <div class="text-sm text-gray-600">分类</div>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-4 text-center">
          <div class="text-2xl font-bold text-indigo-600">15624</div>
          <div class="text-sm text-gray-600">关系</div>
        </div>
      </div>

      <!-- 控制面板 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <div class="flex flex-wrap gap-4 items-center">
          <!-- 搜索框 -->
          <div class="flex-1 min-w-64">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索疾病、症状、药物..."
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <!-- 筛选选项 -->
          <div class="flex gap-2">
            <select v-model="selectedNodeType" class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
              <option value="all">全部类型</option>
              <option value="disease">疾病</option>
              <option value="drug">药物</option>
              <option value="target">靶点</option>
              <option value="gene">基因</option>
              <option value="pathway">通路</option>
            </select>
            
            <button
              @click="resetGraph"
              class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              重置
            </button>
            
            <button
              @click="highlightTopNodes"
              class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              演示模式
            </button>
          </div>
        </div>
      </div>

      <!-- 图谱容器 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-800">关系图谱</h3>
          <div class="flex gap-2">
            <button @click="zoomIn" class="px-3 py-1 bg-gray-100 rounded text-sm">放大</button>
            <button @click="zoomOut" class="px-3 py-1 bg-gray-100 rounded text-sm">缩小</button>
            <span class="text-sm text-gray-600">缩放: {{ Math.round(zoomLevel * 100) }}%</span>
          </div>
        </div>
        
        <div class="relative h-[500px] bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-lg overflow-hidden shadow-inner" ref="graphContainer">
          <svg 
            width="100%" 
            height="100%" 
            :viewBox="`${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`" 
            class="border border-gray-200 cursor-move"
            @mousedown="startPan"
            @mousemove="handlePan"
            @mouseup="endPan"
            @wheel="handleZoom"
            @mouseleave="endPan"
          >
            <!-- 定义渐变和滤镜效果 -->
            <defs>
              <!-- 节点发光效果 -->
              <filter id="glow">
                <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                <feMerge> 
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
              
              <!-- 节点阴影效果 -->
              <filter id="shadow">
                <feDropShadow dx="3" dy="3" stdDeviation="3" flood-opacity="0.4"/>
              </filter>
              
              <!-- 强烈发光效果用于选中节点 -->
              <filter id="strongGlow">
                <feGaussianBlur stdDeviation="6" result="coloredBlur"/>
                <feMerge> 
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
              
              <!-- 节点渐变效果 -->
              <radialGradient id="nodeGradient" cx="30%" cy="30%">
                <stop offset="0%" style="stop-color:rgba(255,255,255,0.3)"/>
                <stop offset="100%" style="stop-color:rgba(0,0,0,0.1)"/>
              </radialGradient>
              
              <!-- 药物节点专用渐变 -->
              <radialGradient id="drugGradient" cx="30%" cy="30%">
                <stop offset="0%" style="stop-color:#60a5fa"/>
                <stop offset="100%" style="stop-color:#1e40af"/>
              </radialGradient>
              
              <!-- 疾病节点专用渐变 -->
              <radialGradient id="diseaseGradient" cx="30%" cy="30%">
                <stop offset="0%" style="stop-color:#f87171"/>
                <stop offset="100%" style="stop-color:#dc2626"/>
              </radialGradient>
              
              <!-- 靶点节点专用渐变 -->
              <radialGradient id="targetGradient" cx="30%" cy="30%">
                <stop offset="0%" style="stop-color:#4ade80"/>
                <stop offset="100%" style="stop-color:#16a34a"/>
              </radialGradient>
              
              <!-- 基因节点专用渐变 -->
              <radialGradient id="geneGradient" cx="30%" cy="30%">
                <stop offset="0%" style="stop-color:#a78bfa"/>
                <stop offset="100%" style="stop-color:#7c3aed"/>
              </radialGradient>
              
              <!-- 通路节点专用渐变 -->
              <radialGradient id="pathwayGradient" cx="30%" cy="30%">
                <stop offset="0%" style="stop-color:#fbbf24"/>
                <stop offset="100%" style="stop-color:#d97706"/>
              </radialGradient>
            </defs>
            
            <!-- 连接线 -->
            <g v-for="edge in filteredEdges" :key="edge.id">
              <line 
                :x1="edge.source.x" 
                :y1="edge.source.y" 
                :x2="edge.target.x" 
                :y2="edge.target.y" 
                :stroke="getEdgeColor(edge)"
                :stroke-width="getEdgeWidth(edge)" 
                :opacity="getEdgeOpacity(edge)"
                :class="getEdgeClass(edge)"
                @click="selectEdge(edge)"
                @mouseenter="hoveredEdge = edge"
                @mouseleave="hoveredEdge = null"
                class="cursor-pointer transition-all duration-300"
              />
            </g>
            
            <!-- 节点 -->
            <g v-for="node in filteredNodes" :key="node.id">
              <circle
                :cx="node.x"
                :cy="node.y"
                :r="getNodeRadius(node)"
                :fill="getNodeColor(node)"
                :stroke="getNodeStroke(node)"
                :stroke-width="getNodeStrokeWidth(node)"
                :opacity="getNodeOpacity(node)"
                :filter="node.selected ? 'url(#strongGlow)' : (node.id === hoveredNode?.id ? 'url(#glow)' : 'url(#shadow)')"
                :class="getNodeClass(node)"
                @click="selectNode(node)"
                @mouseenter="onNodeHover(node, $event)"
                @mouseleave="onNodeLeave(node)"
                @mousedown="startDrag(node, $event)"
                class="cursor-pointer transition-all duration-300"
              />
              <text
                :x="node.x"
                :y="node.y + getNodeRadius(node) + 15"
                text-anchor="middle"
                :class="getTextClass(node)"
                :opacity="getNodeOpacity(node)"
                style="font-size: 10px; pointer-events: none;"
              >
                {{ getDisplayLabel(node.label) }}
              </text>
            </g>
          </svg>
          
          <!-- 悬停工具提示 -->
          <div 
            v-if="tooltip.visible" 
            :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
            class="absolute z-50 bg-white rounded-lg shadow-xl border border-gray-200 p-4 max-w-xs pointer-events-none"
          >
            <div v-if="tooltip.type === 'node'">
              <h4 class="font-semibold text-gray-900 mb-2">{{ tooltip.data.label }}</h4>
              <p class="text-sm text-gray-600 mb-2">{{ tooltip.data.description }}</p>
              <div class="flex gap-2 mb-2">
                <span :class="`px-2 py-1 text-xs rounded ${getTypeColorClass(tooltip.data.type)}`">
                  {{ getTypeDisplayName(tooltip.data.type) }}
                </span>
                <span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                  {{ getNodeConnectionCount(tooltip.data.id) }} 连接
                </span>
              </div>
              <div class="text-xs text-gray-500">
                点击选择 • 拖拽移动 • 双击查看详情
              </div>
            </div>
            <div v-if="tooltip.type === 'edge'">
              <h4 class="font-semibold text-gray-900 mb-1">关系连接</h4>
              <p class="text-sm text-gray-600">
                {{ tooltip.data.source.label }} ↔ {{ tooltip.data.target.label }}
              </p>
              <div class="text-xs text-gray-500 mt-2">
                关系类型: {{ tooltip.data.relation }}
              </div>
            </div>
          </div>
          
          <!-- 选中节点的详细信息面板 -->
          <div 
            v-if="selectedNode && selectedNode.showDetails" 
            class="absolute top-4 left-4 bg-white rounded-lg shadow-xl border border-gray-200 p-4 max-w-sm z-40"
          >
            <div class="flex justify-between items-start mb-3">
              <h3 class="font-semibold text-gray-900">{{ selectedNode.label }}</h3>
              <button @click="closeNodeDetails" class="text-gray-400 hover:text-gray-600">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            <div class="space-y-2">
              <p class="text-sm text-gray-600">{{ selectedNode.description }}</p>
              <div class="flex gap-2">
                <span :class="`px-2 py-1 text-xs rounded ${getTypeColorClass(selectedNode.type)}`">
                  {{ getTypeDisplayName(selectedNode.type) }}
                </span>
              </div>
              <div class="text-xs text-gray-500">
                连接数: {{ getNodeConnectionCount(selectedNode.id) }}
              </div>
              <div class="flex gap-2 mt-3">
                <button 
                  @click="highlightConnections(selectedNode)" 
                  class="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 transition-colors"
                >
                  高亮关系
                </button>
                <button 
                  @click="centerOnNode(selectedNode)" 
                  class="px-3 py-1 bg-green-500 text-white text-xs rounded hover:bg-green-600 transition-colors"
                >
                  居中显示
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 节点详情面板 -->
      <div v-if="selectedNode" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">节点详情</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 class="font-medium text-gray-900 mb-2">{{ selectedNode.label }}</h4>
            <p class="text-sm text-gray-600 mb-4">{{ selectedNode.description }}</p>
            <div class="flex gap-2">
              <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">{{ selectedNode.type }}</span>
              <span class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">连接数: {{ getNodeConnectionCount(selectedNode.id) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 节点信息和关联关系面板 -->
      <div class="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 节点基本信息 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              节点信息
            </h3>
            <div class="text-sm text-gray-500">
              {{ selectedNode ? '已选中' : '点击节点查看详情' }}
            </div>
          </div>
          
          <div v-if="selectedNode" class="space-y-4">
            <!-- 基本信息 -->
            <div class="border-l-4 border-blue-500 pl-4">
              <h4 class="font-semibold text-gray-900 text-lg">{{ selectedNode.label }}</h4>
              <p class="text-gray-600 mt-1">{{ selectedNode.description }}</p>
              <div class="flex gap-2 mt-3">
                <span :class="`px-3 py-1 text-sm rounded-full ${getTypeColorClass(selectedNode.type)}`">
                  {{ getTypeDisplayName(selectedNode.type) }}
                </span>
                <span class="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">
                  ID: {{ selectedNode.id }}
                </span>
              </div>
            </div>
            
            <!-- 统计信息 -->
            <div class="grid grid-cols-2 gap-4">
              <div class="bg-blue-50 rounded-lg p-3">
                <div class="text-2xl font-bold text-blue-600">{{ getNodeConnectionCount(selectedNode.id) }}</div>
                <div class="text-sm text-blue-700">总连接数</div>
              </div>
              <div class="bg-green-50 rounded-lg p-3">
                <div class="text-2xl font-bold text-green-600">{{ getNodeRadius(selectedNode) }}</div>
                <div class="text-sm text-green-700">节点大小</div>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div class="flex gap-2">
              <button 
                @click="highlightConnections(selectedNode)" 
                class="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
                </svg>
                高亮关系
              </button>
              <button 
                @click="centerOnNode(selectedNode)" 
                class="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center justify-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                居中显示
              </button>
            </div>
          </div>
          
          <div v-else class="text-center py-8">
            <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p class="text-gray-500">点击图谱中的任意节点查看详细信息</p>
            <p class="text-sm text-gray-400 mt-1">支持拖拽、缩放和高亮显示</p>
          </div>
        </div>
        
        <!-- 关联关系列表 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
              </svg>
              关联关系
            </h3>
            <div v-if="selectedNode" class="text-sm text-gray-500">
              共 {{ getConnectedNodes(selectedNode).length }} 个关联
            </div>
          </div>
          
          <div v-if="selectedNode" class="space-y-3 max-h-80 overflow-y-auto">
            <div 
              v-for="connection in getConnectedNodes(selectedNode)" 
              :key="connection.node.id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
              @click="selectNode(connection.node)"
            >
              <div class="flex items-center gap-3">
                <div 
                  class="w-4 h-4 rounded-full" 
                  :style="{ backgroundColor: connection.node.color }"
                ></div>
                <div>
                  <div class="font-medium text-gray-900">{{ connection.node.label }}</div>
                  <div class="text-sm text-gray-500">{{ getTypeDisplayName(connection.node.type) }}</div>
                </div>
              </div>
              <div class="text-right">
                <div class="text-sm font-medium text-gray-700">{{ connection.relation }}</div>
                <div class="text-xs text-gray-500">点击查看</div>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center py-8">
            <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
            </svg>
            <p class="text-gray-500">选择节点后显示其关联关系</p>
            <p class="text-sm text-gray-400 mt-1">包括连接的节点和关系类型</p>
          </div>
        </div>
      </div>

      <!-- 智能问答模块 -->
      <div class="mt-6 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
            </svg>
            智能问答助手
          </h3>
          <div class="text-sm text-gray-500">
            基于知识图谱的AI助手
          </div>
        </div>
        
        <!-- 对话历史 -->
        <div class="mb-4 h-64 overflow-y-auto bg-gray-50 rounded-lg p-4 space-y-3">
          <div v-if="chatHistory.length === 0" class="text-center text-gray-500 py-8">
            <svg class="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
            </svg>
            <p>开始与AI助手对话</p>
            <p class="text-xs mt-1">询问关于医疗知识图谱的任何问题</p>
          </div>
          
          <div v-for="(message, index) in chatHistory" :key="index" class="flex gap-3">
            <div v-if="message.type === 'user'" class="flex justify-end w-full">
              <div class="bg-blue-500 text-white rounded-lg px-4 py-2 max-w-xs">
                {{ message.content }}
              </div>
            </div>
            <div v-else class="flex gap-3">
              <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
              </div>
              <div class="bg-white border rounded-lg px-4 py-2 max-w-md">
                {{ message.content }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- 快速问题建议 -->
        <div class="mb-4">
          <div class="flex flex-wrap gap-2">
            <button 
              v-for="suggestion in quickQuestions" 
              :key="suggestion"
              @click="askQuickQuestion(suggestion)"
              class="px-3 py-1 text-sm bg-purple-50 text-purple-700 rounded-full hover:bg-purple-100 transition-colors"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>
        
        <!-- 输入区域 -->
        <div class="flex gap-2">
          <input
            v-model="chatInput"
            @keyup.enter="sendMessage"
            type="text"
            placeholder="询问关于阿司匹林或其他医疗知识的问题..."
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
          <button
            @click="sendMessage"
            :disabled="!chatInput.trim()"
            class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            发送
          </button>
          <button
            @click="clearChat"
            class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            清除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 响应式数据
const searchQuery = ref('')
const selectedNodeType = ref('all')
const selectedNode = ref(null)
const hoveredNode = ref(null)
const hoveredEdge = ref(null)
const selectedEdge = ref(null)
const zoomLevel = ref(1)
const graphContainer = ref(null)

// 视图控制
const viewBox = ref({
  x: 0,
  y: 0,
  width: 1200,
  height: 600
})

// 拖拽和平移状态
const isDragging = ref(false)
const isPanning = ref(false)
const dragNode = ref(null)
const lastMousePos = ref({ x: 0, y: 0 })

// 工具提示
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  type: 'node', // 'node' 或 'edge'
  data: null
})

// 高亮状态
const highlightedNodes = ref(new Set())
const highlightedEdges = ref(new Set())

// 智能问答相关变量
const chatHistory = ref([])
const chatInput = ref('')
const quickQuestions = ref([
  '什么是知识图谱？',
  '药物与疾病之间有什么关系？',
  '基因如何影响药物疗效？',
  '靶点在药物作用中的角色？',
  '如何使用图谱查找信息？',
  '什么是药物相互作用？',
  '疾病的分子机制是什么？',
  '通路在疾病中的作用？'
])

// 生成大规模医疗知识图谱数据
const generateNodes = () => {
  const nodeTypes = [
    { type: 'disease', color: '#ef4444', count: 120, names: ['高血压', '糖尿病', '肝癌', '肺癌', '心脏病', '脑卒中', '肾病', '胃炎', '关节炎', '哮喘', '冠心病', '动脉硬化', '血栓', '心律不齐', '炎症', '疼痛综合征', '阿尔茨海默病', '帕金森病', '抑郁症', '焦虑症', '骨质疏松', '白血病', '淋巴瘤', '乳腺癌', '结肠癌', '胃癌', '食管癌', '膀胱癌', '前列腺癌', '卵巢癌'] },
    { type: 'drug', color: '#3b82f6', count: 150, names: ['二甲双胍', '索拉非尼', '恩替卡韦', '布洛芬', '青霉素', '胰岛素', '华法林', '氯吡格雷', '辛伐他汀', '美托洛尔', '卡托普利', '硝酸甘油', '奥美拉唑', '氨氯地平', '洛伐他汀', '阿托伐他汀', '利伐沙班', '达比加群', '多奈哌齐', '美金刚', '氟西汀', '舍曲林', '阿仑膦酸钠', '唑来膦酸', '伊马替尼', '吉非替尼', '厄洛替尼', '贝伐珠单抗', '曲妥珠单抗', '利妥昔单抗'] },
    { type: 'target', color: '#10b981', count: 90, names: ['COX-1', 'COX-2', 'EGFR', 'VEGF', 'HER2', 'PDGFR', 'mTOR', 'PI3K', 'AKT', 'p53', 'TXA2', 'PGI2', '血小板聚集受体', 'NF-κB', 'PTGS1', 'PTGS2', 'VEGFR', 'PDGFR-α', 'PDGFR-β', 'IGF-1R', 'FGFR', 'c-MET', 'ALK', 'ROS1', 'BRAF', 'MEK', 'ERK', 'JAK1', 'JAK2', 'STAT3', 'STAT5', 'BCL-2', 'MCL-1', 'MDM2', 'PARP', 'HDAC', 'DNA-PK', 'ATM', 'ATR', 'Chk1'] },
    { type: 'gene', color: '#8b5cf6', count: 80, names: ['TP53', 'BRCA1', 'BRCA2', 'KRAS', 'EGFR', 'HER2', 'PIK3CA', 'AKT1', 'PTGS1', 'PTGS2', 'CYP2C19', 'ABCB1', 'F2', 'F5', 'VKORC1', 'BRAF', 'NRAS', 'PIK3R1', 'PTEN', 'RB1', 'APC', 'MLH1', 'MSH2', 'MSH6', 'PMS2', 'ATM', 'CHEK2', 'PALB2', 'CDH1', 'STK11', 'VHL', 'NF1', 'NF2', 'TSC1', 'TSC2', 'CDKN2A', 'MDM2', 'ERBB2', 'MYC', 'CCND1'] },
    { type: 'pathway', color: '#f59e0b', count: 50, names: ['花生四烯酸代谢通路', '血小板聚集通路', '炎症反应通路', 'PI3K/AKT通路', 'MAPK通路', 'Wnt通路', 'p53通路', 'mTOR通路', 'JAK/STAT通路', '凝血级联反应', 'NF-κB信号通路', 'TGF-β信号通路', 'Notch信号通路', 'Hedgehog信号通路', 'VEGF信号通路', 'EGF信号通路', 'TNF信号通路', '细胞凋亡通路', '细胞周期通路', 'DNA损伤修复通路', '糖酵解通路', '三羧酸循环', '脂肪酸合成通路', '胆固醇合成通路', '嘌呤代谢通路', '嘧啶代谢通路', '氨基酸代谢通路', '免疫应答通路', 'T细胞激活通路', 'B细胞激活通路'] }
  ]

  const allNodes = []
  let nodeId = 1

  // 首先创建唯一的阿司匹林节点
  allNodes.push({
    id: 'drug_aspirin',
    label: '阿司匹林',
    type: 'drug',
    x: 600, // 稍偏右的中心位置
    y: 300,
    radius: 18, // 稍大一些，突出重要性
    color: '#2563eb',
    description: '阿司匹林是一种广泛使用的非甾体抗炎药(NSAID)，具有解热、镇痛、抗炎和抗血小板聚集的作用。常用于预防心血管疾病、治疗疼痛和炎症。',
    selected: false,
    isDemo: true // 标记为演示节点
  })

  // 使用更好的分布算法生成其他节点
  nodeTypes.forEach((nodeType, typeIndex) => {
    // 为每种类型的节点创建不同的分布区域，增加分布范围
    const angleStep = (2 * Math.PI) / nodeTypes.length
    const baseAngle = typeIndex * angleStep
    const centerX = 600 + Math.cos(baseAngle) * 250
    const centerY = 300 + Math.sin(baseAngle) * 180
    
    // 计算每种类型需要的分布层数
    const nodesPerLayer = 12
    const layers = Math.ceil(nodeType.count / nodesPerLayer)
    
    for (let i = 0; i < nodeType.count; i++) {
      const baseName = nodeType.names[i % nodeType.names.length]
      const label = nodeType.count > nodeType.names.length ? `${baseName}_${Math.floor(i / nodeType.names.length) + 1}` : baseName
      
      // 计算当前节点在哪一层
      const layer = Math.floor(i / nodesPerLayer)
      const positionInLayer = i % nodesPerLayer
      
      // 在类型区域内使用多层极坐标分布
      const layerAngle = (positionInLayer / nodesPerLayer) * 2 * Math.PI + Math.random() * 0.3
      const layerDistance = 60 + layer * 50 + Math.random() * 30
      
      // 添加一些随机偏移以避免过于规整
      const randomOffsetX = (Math.random() - 0.5) * 80
      const randomOffsetY = (Math.random() - 0.5) * 80
      
      const x = centerX + Math.cos(layerAngle) * layerDistance + randomOffsetX
      const y = centerY + Math.sin(layerAngle) * layerDistance + randomOffsetY
      
      // 确保节点在扩展的视图范围内
      const clampedX = Math.max(30, Math.min(1170, x))
      const clampedY = Math.max(30, Math.min(570, y))
      
      allNodes.push({
        id: `${nodeType.type}_${nodeId++}`,
        label: label,
        type: nodeType.type,
        x: clampedX,
        y: clampedY,
        radius: 8 + Math.random() * 10,
        color: nodeType.color,
        description: `${label}的详细医疗信息和相关研究`,
        selected: false
      })
    }
  })

  return allNodes
}

// 生成连接关系
const generateEdges = (nodeList) => {
  const edges = []
  let edgeId = 1
  
  // 找到阿司匹林节点
  const aspirinNode = nodeList.find(node => node.id === 'drug_aspirin')
  
  // 定义不同类型节点间的关系类型
  const relationTypes = {
    'drug-disease': ['治疗', '预防', '缓解', '副作用'],
    'drug-target': ['作用于', '抑制', '激活', '结合'],
    'drug-gene': ['调节', '影响表达', '突变影响'],
    'disease-gene': ['致病基因', '易感基因', '保护基因'],
    'disease-target': ['病理靶点', '治疗靶点'],
    'target-gene': ['编码', '调控', '相互作用'],
    'gene-pathway': ['参与', '调控', '激活'],
    'drug-pathway': ['影响通路', '激活通路', '抑制通路'],
    'disease-pathway': ['异常通路', '相关通路'],
    'default': ['相关', '关联', '相互作用']
  }
  
  // 为阿司匹林创建丰富的关联关系
  if (aspirinNode) {
    // 阿司匹林相关的疾病
    const aspirinDiseases = ['高血压', '心脏病', '脑卒中', '冠心病', '动脉硬化', '血栓', '炎症', '疼痛综合征', '关节炎']
    // 阿司匹林相关的靶点
    const aspirinTargets = ['COX-1', 'COX-2', 'TXA2', 'PGI2', '血小板聚集受体', 'NF-κB', 'PTGS1', 'PTGS2']
    // 阿司匹林相关的基因
    const aspirinGenes = ['PTGS1', 'PTGS2', 'CYP2C19', 'ABCB1', 'F2', 'F5']
    // 阿司匹林相关的通路
    const aspirinPathways = ['花生四烯酸代谢通路', '血小板聚集通路', '炎症反应通路', '凝血级联反应', 'NF-κB信号通路']
    
    // 创建阿司匹林与相关节点的连接
    nodeList.forEach(node => {
      if (node.id !== aspirinNode.id) {
        let shouldConnect = false
        let relation = '相关'
        
        if (node.type === 'disease' && aspirinDiseases.some(disease => node.label.includes(disease))) {
          shouldConnect = true
          relation = Math.random() > 0.3 ? '治疗' : '预防'
        } else if (node.type === 'target' && aspirinTargets.some(target => node.label.includes(target))) {
          shouldConnect = true
          relation = node.label.includes('COX') ? '抑制' : '作用于'
        } else if (node.type === 'gene' && aspirinGenes.some(gene => node.label.includes(gene))) {
          shouldConnect = true
          relation = '调节'
        } else if (node.type === 'pathway' && aspirinPathways.some(pathway => node.label.includes(pathway))) {
          shouldConnect = true
          relation = '影响通路'
        }
        
        if (shouldConnect) {
          edges.push({
            id: `edge_${edgeId++}`,
            source: aspirinNode,
            target: node,
            relation: relation
          })
        }
      }
    })
  }
  
  // 为其他节点生成随机连接（增加连接数量以匹配更多节点）
  const maxOtherEdges = Math.min(600, nodeList.length * 1.2)
  
  for (let i = 0; i < maxOtherEdges; i++) {
    const sourceIndex = Math.floor(Math.random() * nodeList.length)
    const targetIndex = Math.floor(Math.random() * nodeList.length)
    
    if (sourceIndex !== targetIndex) {
      const source = nodeList[sourceIndex]
      const target = nodeList[targetIndex]
      
      // 跳过已经与阿司匹林连接的关系，避免重复
      const existingEdge = edges.find(edge => 
        (edge.source.id === source.id && edge.target.id === target.id) ||
        (edge.source.id === target.id && edge.target.id === source.id)
      )
      
      if (!existingEdge) {
        // 根据节点类型确定关系类型
        const relationKey = `${source.type}-${target.type}`
        const reverseRelationKey = `${target.type}-${source.type}`
        
        let possibleRelations = relationTypes[relationKey] || relationTypes[reverseRelationKey] || relationTypes.default
        const relation = possibleRelations[Math.floor(Math.random() * possibleRelations.length)]
        
        edges.push({
          id: `edge_${edgeId++}`,
          source: source,
          target: target,
          relation: relation
        })
      }
    }
  }
  
  return edges
}

// 初始化数据
const nodes = ref(generateNodes())
const edges = ref(generateEdges(nodes.value))

// 计算节点连接数量
const getNodeConnectionCount = (nodeId) => {
  return edges.value.filter(edge => 
    edge.source.id === nodeId || edge.target.id === nodeId
  ).length
}

// 获取节点的关联关系
const getConnectedNodes = (node) => {
  if (!node) return []
  
  const connections = []
  edges.value.forEach(edge => {
    if (edge.source.id === node.id) {
      connections.push({
        node: edge.target,
        relation: edge.relation || '相关',
        direction: 'outgoing'
      })
    } else if (edge.target.id === node.id) {
      connections.push({
        node: edge.source,
        relation: edge.relation || '相关',
        direction: 'incoming'
      })
    }
  })
  
  return connections
}

// 移除了topConnectedNode计算属性，因为演示推荐模块已删除

// 过滤后的节点
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

// 过滤后的边
const filteredEdges = computed(() => {
  const nodeIds = new Set(filteredNodes.value.map(node => node.id))
  return edges.value.filter(edge => 
    nodeIds.has(edge.source.id) && nodeIds.has(edge.target.id)
  )
})

// 样式计算方法
const getNodeRadius = (node) => {
  const baseRadius = node.radius || 8
  const highlightMultiplier = highlightedNodes.value.has(node.id) ? 1.3 : 1
  const selectedMultiplier = node.selected ? 1.2 : 1
  return baseRadius * highlightMultiplier * selectedMultiplier
}

const getNodeColor = (node) => {
  // 使用渐变效果提升视觉质量
  const gradientMap = {
    'drug': 'url(#drugGradient)',
    'disease': 'url(#diseaseGradient)',
    'target': 'url(#targetGradient)',
    'gene': 'url(#geneGradient)',
    'pathway': 'url(#pathwayGradient)'
  }
  return gradientMap[node.type] || node.color
}

const getNodeStroke = (node) => {
  if (node.selected) return '#3b82f6'
  if (highlightedNodes.value.has(node.id)) return '#ffffff'
  return '#ffffff'
}

const getNodeStrokeWidth = (node) => {
  if (node.selected) return 3
  if (highlightedNodes.value.has(node.id)) return 2
  return 1
}

const getNodeOpacity = (node) => {
  if (highlightedNodes.value.size === 0) {
    // 没有高亮时，所有节点完全不透明
    return 1
  }
  if (highlightedNodes.value.has(node.id)) {
    // 高亮节点完全不透明
    return 1
  } else {
    // 非高亮节点设置为透明
    return 0.2
  }
}

const getNodeClass = (node) => {
  const classes = ['node']
  if (node.selected) classes.push('selected')
  if (highlightedNodes.value.has(node.id)) classes.push('highlighted')
  if (node.id === hoveredNode.value?.id) classes.push('hovered')
  return classes.join(' ')
}

const getTextClass = (node) => {
  const classes = ['text-xs', 'fill-gray-700']
  if (node.selected || highlightedNodes.value.has(node.id)) {
    classes.push('font-semibold')
  }
  return classes.join(' ')
}

const getDisplayLabel = (label) => {
  return label.length > 8 ? label.substring(0, 8) + '...' : label
}

const getEdgeColor = (edge) => {
  if (highlightedEdges.value.has(edge.id)) return '#60a5fa'
  if (edge === selectedEdge.value) return '#f59e0b'
  // 在暗色背景下使用更亮的边颜色
  return '#6b7280'
}

const getEdgeWidth = (edge) => {
  if (highlightedEdges.value.has(edge.id)) return 3
  if (edge === selectedEdge.value) return 2
  return 1
}

const getEdgeOpacity = (edge) => {
  if (highlightedEdges.value.size === 0) {
    // 没有高亮时，所有边保持原有透明度
    return 0.6
  }
  if (highlightedEdges.value.has(edge.id) || edge === selectedEdge.value) {
    // 高亮边完全不透明
    return 1
  } else {
    // 非高亮边设置为透明
    return 0.15
  }
}

const getEdgeClass = (edge) => {
  const classes = ['edge']
  if (edge === selectedEdge.value) classes.push('selected')
  if (highlightedEdges.value.has(edge.id)) classes.push('highlighted')
  return classes.join(' ')
}

const getTypeColorClass = (type) => {
  const colorMap = {
    'disease': 'bg-red-100 text-red-800',
    'drug': 'bg-blue-100 text-blue-800',
    'target': 'bg-green-100 text-green-800',
    'gene': 'bg-purple-100 text-purple-800',
    'pathway': 'bg-yellow-100 text-yellow-800'
  }
  return colorMap[type] || 'bg-gray-100 text-gray-800'
}

const getTypeDisplayName = (type) => {
  const nameMap = {
    'disease': '疾病',
    'drug': '药物',
    'target': '靶点',
    'gene': '基因',
    'pathway': '通路'
  }
  return nameMap[type] || type
}

// 交互方法
const selectNode = (node) => {
  // 清除之前的选择
  nodes.value.forEach(n => {
    n.selected = false
    n.showDetails = false
  })
  
  // 选中新节点
  node.selected = true
  node.showDetails = true
  selectedNode.value = node
  
  // 清除边选择
  selectedEdge.value = null
}

const selectEdge = (edge) => {
  selectedEdge.value = edge
  // 清除节点选择
  nodes.value.forEach(n => {
    n.selected = false
    n.showDetails = false
  })
  selectedNode.value = null
}

const onNodeHover = (node, event) => {
  hoveredNode.value = node
  const rect = graphContainer.value.getBoundingClientRect()
  tooltip.value = {
    visible: true,
    x: event.clientX - rect.left + 10,
    y: event.clientY - rect.top - 10,
    type: 'node',
    data: node
  }
}

const onNodeLeave = (node) => {
  if (hoveredNode.value === node) {
    hoveredNode.value = null
  }
  if (!isDragging.value) {
    tooltip.value.visible = false
  }
}

const closeNodeDetails = () => {
  if (selectedNode.value) {
    selectedNode.value.showDetails = false
  }
}

const highlightConnections = (node) => {
  const connectedNodeIds = new Set()
  const connectedEdgeIds = new Set()
  
  // 找到所有连接到这个节点的边和节点
  edges.value.forEach(edge => {
    if (edge.source.id === node.id) {
      connectedNodeIds.add(edge.target.id)
      connectedEdgeIds.add(edge.id)
    } else if (edge.target.id === node.id) {
      connectedNodeIds.add(edge.source.id)
      connectedEdgeIds.add(edge.id)
    }
  })
  
  // 添加选中的节点本身
  connectedNodeIds.add(node.id)
  
  // 更新高亮状态
  highlightedNodes.value = connectedNodeIds
  highlightedEdges.value = connectedEdgeIds
  
  // 3秒后清除高亮
  setTimeout(() => {
    highlightedNodes.value = new Set()
    highlightedEdges.value = new Set()
  }, 3000)
}

const centerOnNode = (node) => {
  const centerX = node.x - viewBox.value.width / 2
  const centerY = node.y - viewBox.value.height / 2
  
  viewBox.value.x = centerX
  viewBox.value.y = centerY
}

// 拖拽功能
const startDrag = (node, event) => {
  event.stopPropagation()
  isDragging.value = true
  dragNode.value = node
  
  const rect = graphContainer.value.getBoundingClientRect()
  lastMousePos.value = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
  
  // 添加全局事件监听
  document.addEventListener('mousemove', handleDrag)
  document.addEventListener('mouseup', endDrag)
}

const handleDrag = (event) => {
  if (!isDragging.value || !dragNode.value) return
  
  const rect = graphContainer.value.getBoundingClientRect()
  const currentMousePos = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
  
  // 计算移动距离
  const deltaX = currentMousePos.x - lastMousePos.value.x
  const deltaY = currentMousePos.y - lastMousePos.value.y
  
  // 更新节点位置
  dragNode.value.x += deltaX * (viewBox.value.width / rect.width)
  dragNode.value.y += deltaY * (viewBox.value.height / rect.height)
  
  lastMousePos.value = currentMousePos
}

const endDrag = () => {
  isDragging.value = false
  dragNode.value = null
  tooltip.value.visible = false
  
  // 移除全局事件监听
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', endDrag)
}

// 平移功能
const startPan = (event) => {
  if (isDragging.value) return
  
  isPanning.value = true
  const rect = graphContainer.value.getBoundingClientRect()
  lastMousePos.value = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
}

const handlePan = (event) => {
  if (!isPanning.value) return
  
  const rect = graphContainer.value.getBoundingClientRect()
  const currentMousePos = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
  
  const deltaX = currentMousePos.x - lastMousePos.value.x
  const deltaY = currentMousePos.y - lastMousePos.value.y
  
  // 更新视图框位置
  viewBox.value.x -= deltaX * (viewBox.value.width / rect.width)
  viewBox.value.y -= deltaY * (viewBox.value.height / rect.height)
  
  lastMousePos.value = currentMousePos
}

const endPan = () => {
  isPanning.value = false
}

// 缩放功能
const handleZoom = (event) => {
  event.preventDefault()
  
  const zoomIntensity = 0.1
  const zoomDirection = event.deltaY < 0 ? 1 : -1
  const zoomFactor = 1 + (zoomDirection * zoomIntensity)
  
  // 获取鼠标在视图中的位置
  const rect = graphContainer.value.getBoundingClientRect()
  const mouseX = event.clientX - rect.left
  const mouseY = event.clientY - rect.top
  
  // 计算鼠标在视图坐标系中的位置
  const viewMouseX = viewBox.value.x + (mouseX / rect.width) * viewBox.value.width
  const viewMouseY = viewBox.value.y + (mouseY / rect.height) * viewBox.value.height
  
  // 更新视图框尺寸
  viewBox.value.width *= zoomFactor
  viewBox.value.height *= zoomFactor
  
  // 调整视图框位置，保持鼠标指向的点不变
  viewBox.value.x = viewMouseX - (mouseX / rect.width) * viewBox.value.width
  viewBox.value.y = viewMouseY - (mouseY / rect.height) * viewBox.value.height
  
  // 更新缩放级别显示
  zoomLevel.value = 1200 / viewBox.value.width
}

const resetGraph = () => {
  searchQuery.value = ''
  selectedNodeType.value = 'all'
  selectedNode.value = null
  selectedEdge.value = null
  highlightedNodes.value = new Set()
  highlightedEdges.value = new Set()
  nodes.value.forEach(node => {
    node.selected = false
    node.showDetails = false
  })
  
  // 重置视图
  viewBox.value = {
    x: 0,
    y: 0,
    width: 1200,
    height: 600
  }
  zoomLevel.value = 1
}

const highlightTopNodes = () => {
  // 优先展示阿司匹林节点
  const aspirinNode = nodes.value.find(node => node.id === 'drug_aspirin')
  
  if (aspirinNode) {
    nodes.value.forEach(node => {
      node.selected = false
      node.showDetails = false
    })
    
    aspirinNode.selected = true
    aspirinNode.showDetails = true
    selectedNode.value = aspirinNode
    centerOnNode(aspirinNode)
    highlightConnections(aspirinNode)
  } else {
    // 如果没有阿司匹林节点，则显示连接数最多的节点
    const topNodes = nodes.value
      .map(node => ({ ...node, connectionCount: getNodeConnectionCount(node.id) }))
      .sort((a, b) => b.connectionCount - a.connectionCount)
      .slice(0, 5)
    
    nodes.value.forEach(node => {
      node.selected = false
      node.showDetails = false
    })
    
    if (topNodes.length > 0) {
      const topNode = nodes.value.find(n => n.id === topNodes[0].id)
      if (topNode) {
        topNode.selected = true
        topNode.showDetails = true
        selectedNode.value = topNode
        highlightConnections(topNode)
      }
    }
  }
}

const zoomIn = () => {
  const zoomFactor = 0.8
  const centerX = viewBox.value.x + viewBox.value.width / 2
  const centerY = viewBox.value.y + viewBox.value.height / 2
  
  viewBox.value.width *= zoomFactor
  viewBox.value.height *= zoomFactor
  viewBox.value.x = centerX - viewBox.value.width / 2
  viewBox.value.y = centerY - viewBox.value.height / 2
  
  zoomLevel.value = 1200 / viewBox.value.width
}

const zoomOut = () => {
  const zoomFactor = 1.25
  const centerX = viewBox.value.x + viewBox.value.width / 2
  const centerY = viewBox.value.y + viewBox.value.height / 2
  
  viewBox.value.width *= zoomFactor
  viewBox.value.height *= zoomFactor
  viewBox.value.x = centerX - viewBox.value.width / 2
  viewBox.value.y = centerY - viewBox.value.height / 2
  
  zoomLevel.value = 1200 / viewBox.value.width
}

// 智能问答功能
const sendMessage = () => {
  if (!chatInput.value.trim()) return
  
  // 添加用户消息
  chatHistory.value.push({
    type: 'user',
    content: chatInput.value,
    timestamp: new Date()
  })
  
  const userMessage = chatInput.value
  chatInput.value = ''
  
  // 模拟AI回复
  setTimeout(() => {
    const aiResponse = generateAIResponse(userMessage)
    chatHistory.value.push({
      type: 'ai',
      content: aiResponse,
      timestamp: new Date()
    })
  }, 1000)
}

const askQuickQuestion = (question) => {
  chatInput.value = question
  sendMessage()
}

const clearChat = () => {
  chatHistory.value = []
}

const generateAIResponse = (message) => {
  const lowerMessage = message.toLowerCase()
  
  // 基于关键词的智能回复
  if (lowerMessage.includes('知识图谱') || lowerMessage.includes('什么是知识图谱')) {
    return '知识图谱是一种结构化的知识表示方法，通过节点和边来表示实体及其关系。在医疗领域，它可以展示药物、疾病、基因、靶点和生物通路之间的复杂关联。我们的图谱包含5种类型的节点：药物（蓝色）、疾病（红色）、靶点（绿色）、基因（紫色）和通路（黄色）。'
  } else if (lowerMessage.includes('药物') && lowerMessage.includes('疾病')) {
    return '药物与疾病之间存在多种关系：1) 治疗关系 - 药物可以治疗特定疾病；2) 预防关系 - 药物可以预防疾病发生；3) 副作用关系 - 药物可能引起某些疾病；4) 禁忌关系 - 某些疾病患者不能使用特定药物。在图谱中，这些关系通过连接线表示，您可以点击节点查看具体的关联信息。'
  } else if (lowerMessage.includes('基因') && (lowerMessage.includes('药物') || lowerMessage.includes('疗效'))) {
    return '基因对药物疗效有重要影响，这被称为药物基因组学：1) 代谢基因 - 如CYP2C19影响某些药物的代谢速度；2) 靶点基因 - 基因变异可能影响药物与靶点的结合；3) 转运基因 - 影响药物在体内的分布；4) 毒性基因 - 决定个体对药物副作用的敏感性。个体化用药就是基于这些基因信息。'
  } else if (lowerMessage.includes('靶点') && lowerMessage.includes('作用')) {
    return '靶点是药物发挥作用的分子基础，通常是蛋白质：1) 受体 - 药物与受体结合产生生物效应；2) 酶 - 药物通过抑制或激活酶来发挥作用；3) 离子通道 - 药物调节离子通道的开闭；4) 转运蛋白 - 影响物质的跨膜转运。了解靶点有助于药物设计和副作用预测。'
  } else if (lowerMessage.includes('如何使用') || lowerMessage.includes('查找信息')) {
    return '使用图谱查找信息的方法：1) 搜索功能 - 在搜索框输入药物或疾病名称；2) 节点点击 - 点击任意节点查看详细信息和关联关系；3) 高亮功能 - 点击"高亮关系"查看所有相关连接；4) 拖拽交互 - 拖拽节点重新布局以便观察；5) 缩放平移 - 使用鼠标滚轮缩放，拖拽空白区域平移视图。'
  } else if (lowerMessage.includes('药物相互作用') || lowerMessage.includes('相互作用')) {
    return '药物相互作用是指两种或多种药物同时使用时产生的相互影响：1) 药效学相互作用 - 药物在作用部位的相互影响；2) 药代动力学相互作用 - 影响药物的吸收、分布、代谢、排泄；3) 协同作用 - 联合用药效果增强；4) 拮抗作用 - 一种药物减弱另一种的效果。在图谱中可以看到药物间的关联关系。'
  } else if (lowerMessage.includes('疾病') && lowerMessage.includes('分子机制')) {
    return '疾病的分子机制是指疾病发生发展的分子水平原理：1) 基因突变 - 导致蛋白质功能异常；2) 信号通路异常 - 细胞间通讯出现问题；3) 代谢紊乱 - 正常生化过程受到干扰；4) 免疫反应异常 - 自身免疫或免疫缺陷。理解分子机制有助于开发针对性治疗方法。'
  } else if (lowerMessage.includes('通路') && lowerMessage.includes('作用')) {
    return '生物通路在疾病中起关键作用：1) 信号传导通路 - 调节细胞的生长、分化、凋亡；2) 代谢通路 - 维持细胞的能量和物质代谢；3) 免疫通路 - 调节免疫反应；4) DNA修复通路 - 维护基因组稳定性。通路异常常常是疾病的根本原因，也是药物作用的重要靶点。'
  } else if (lowerMessage.includes('阿司匹林')) {
    if (lowerMessage.includes('作用') || lowerMessage.includes('功效')) {
      return '阿司匹林主要有四大作用：1) 解热镇痛 - 缓解发热和疼痛；2) 抗炎作用 - 减轻炎症反应；3) 抗血小板聚集 - 预防血栓形成；4) 心血管保护 - 预防心脏病和脑卒中。在知识图谱中，您可以看到阿司匹林与多种疾病和靶点的关联关系。'
    } else {
      return '阿司匹林是一种重要的非甾体抗炎药，在我们的知识图谱中处于核心位置。您可以点击阿司匹林节点查看其详细信息和关联关系，或者问我更具体的问题。'
    }
  } else if (lowerMessage.includes('药物') || lowerMessage.includes('疾病') || lowerMessage.includes('基因') || lowerMessage.includes('靶点') || lowerMessage.includes('通路')) {
    return '我们的知识图谱包含了丰富的医疗实体：药物节点（蓝色）、疾病节点（红色）、靶点节点（绿色）、基因节点（紫色）和通路节点（黄色）。每种类型的节点都有其特定的医疗信息和关联关系。您可以点击任意节点查看详细信息，或者问我关于特定实体类型的问题。'
  }
  
  return '感谢您的问题！我是基于医疗知识图谱的AI助手。您可以询问关于知识图谱、药物、疾病、基因、靶点、通路以及它们之间关系的问题。我会根据图谱中的关系为您提供专业的医疗知识解答。'
}

onMounted(() => {
  console.log('知识图谱页面已加载，节点数量:', nodes.value.length)
})
</script>

<style scoped>
.transition-all {
  transition: all 0.2s ease-in-out;
}

/* 节点交互样式 */
.node {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.node.selected {
  filter: drop-shadow(0 4px 8px rgba(59, 130, 246, 0.4));
}

.node.highlighted {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.node.hovered {
  transform: scale(1.1);
  filter: drop-shadow(0 6px 12px rgba(0, 0, 0, 0.3));
}

/* 边交互样式 */
.edge {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.edge.selected {
  stroke-dasharray: 5,5;
  animation: dash 1s linear infinite;
}

.edge.highlighted {
  filter: drop-shadow(0 1px 2px rgba(59, 130, 246, 0.3));
}

@keyframes dash {
  to {
    stroke-dashoffset: -10;
  }
}

/* SVG容器样式 */
svg {
  border-radius: 8px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

/* 工具提示动画 */
.absolute.z-50 {
  animation: fadeInTooltip 0.2s ease-out;
}

@keyframes fadeInTooltip {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 详情面板动画 */
.absolute.top-4.left-4 {
  animation: slideInPanel 0.3s ease-out;
}

@keyframes slideInPanel {
  from {
    opacity: 0;
    transform: translateX(-16px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 悬停效果 */
.cursor-move:hover {
  cursor: move;
}

.cursor-pointer:hover {
  cursor: pointer;
}

/* 按钮悬停效果增强 */
button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

button:active {
  transform: translateY(0);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .absolute.top-4.left-4 {
    position: fixed;
    top: 16px;
    left: 16px;
    right: 16px;
    max-width: none;
    z-index: 50;
  }
  
  .absolute.z-50 {
    max-width: 280px;
  }
}

/* 图谱容器边框增强 */
.bg-gray-50 {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  position: relative;
}

.bg-gray-50::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  pointer-events: none;
}

/* 搜索框增强 */
input:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  border-color: #3b82f6;
}

/* 选择框增强 */
select:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  border-color: #3b82f6;
}
</style>
