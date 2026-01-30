<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
    <!-- 顶部导航栏 -->
    <header class="bg-white/90 backdrop-blur-md shadow-sm py-3 px-6 md:px-12 transition-all duration-300 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto flex justify-between items-center">
        <div class="flex items-center gap-3 group">
          <router-link to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div class="w-10 h-10 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold shadow-md group-hover:scale-105 transition-transform">MK</div>
            <h1 class="text-xl md:text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-800 to-gray-600">智慧医疗知识服务平台</h1>
          </router-link>
          <!-- 演示模式提示 -->
          <div v-if="authStore.isDemoMode" class="hidden md:flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
            演示模式
          </div>
        </div>
        
        <!-- 导航菜单 -->
        <nav class="hidden lg:flex items-center gap-1">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-2"
            :class="$route.path === item.path 
              ? 'bg-blue-100 text-blue-700 shadow-sm' 
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'"
          >
            <component :is="item.icon" class="w-4 h-4" />
            {{ item.name }}
          </router-link>
        </nav>

        <!-- 移动端菜单按钮 -->
        <button 
          @click="mobileMenuOpen = !mobileMenuOpen"
          class="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
          </svg>
        </button>
      </div>

      <!-- 移动端导航菜单 -->
      <div v-if="mobileMenuOpen" class="lg:hidden mt-4 pb-4 border-t border-gray-200">
        <div class="flex flex-col gap-2 mt-4">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            @click="mobileMenuOpen = false"
            class="px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-3"
            :class="$route.path === item.path 
              ? 'bg-blue-100 text-blue-700' 
              : 'text-gray-600 hover:bg-gray-100'"
          >
            <component :is="item.icon" class="w-5 h-5" />
            <div>
              <div class="font-medium">{{ item.name }}</div>
              <div class="text-xs text-gray-500 mt-1">{{ item.description }}</div>
            </div>
          </router-link>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="flex-1">
      <router-view />
    </main>

    <!-- 页脚 -->
    <footer class="bg-white/80 backdrop-blur-md py-4 px-6 text-center text-sm text-gray-500 border-t border-gray-100">
      <p>© 2025 智慧医疗知识服务平台 | 仅供研究使用</p>
      <div class="mt-2 text-xs">
        <a href="#" class="hover:text-blue-600 transition-colors">使用说明</a> |
        <a href="#" class="hover:text-blue-600 transition-colors">关于系统</a> |
        <a href="#" class="hover:text-blue-600 transition-colors">联系我们</a>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const mobileMenuOpen = ref(false)

// 导航菜单项
const navItems = [
  {
    name: '首页',
    path: '/',
    description: '问答主界面',
    icon: 'HomeIcon'
  },
  {
    name: '药品识别',
    path: '/drug-identification',
    description: '上传药盒照片，自动识别药品信息',
    icon: 'CameraIcon'
  },
  {
    name: '知识图谱',
    path: '/knowledge-graph',
    description: '可视化展示药物、疾病、靶点之间的关系图',
    icon: 'GraphIcon'
  },
  {
    name: '数据浏览',
    path: '/data-browser',
    description: '查看药物、疾病、基因、文献等详细列表',
    icon: 'DatabaseIcon'
  },
  {
    name: '药物详情',
    path: '/drug',
    description: '单个药物的详细信息：结构、作用机制、关联疾病',
    icon: 'PillIcon'
  },
  {
    name: '疾病详情',
    path: '/disease',
    description: '展示疾病简介、治疗药物、关键靶点',
    icon: 'HeartIcon'
  },
  {
    name: '分析页',
    path: '/analysis',
    description: '可视化展示药物-疾病重定位结果分析、统计图表',
    icon: 'ChartIcon'
  }
]
</script>

<script>
// 图标组件
const HomeIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" /></svg>`
}

const GraphIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0 0 20.25 18V6A2.25 2.25 0 0 0 18 3.75H6A2.25 2.25 0 0 0 3.75 6v12A2.25 2.25 0 0 0 6 20.25Z" /></svg>`
}

const DatabaseIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" /></svg>`
}

const PillIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 0 1-.659 1.591L5 14.5a2.25 2.25 0 0 1-3.182 0 2.25 2.25 0 0 1 0-3.182l4.091-4.091A2.25 2.25 0 0 1 7.5 6.568V3.104a48.524 48.524 0 0 1 2.25-.546Zm-6.82 8.636a2.25 2.25 0 0 1 3.182 0l4.091 4.091A2.25 2.25 0 0 1 10.86 17.5v2.25a48.063 48.063 0 0 1-2.25.546v-2.796a2.25 2.25 0 0 1 .659-1.591L13.36 11.818a2.25 2.25 0 0 1 3.182 0 2.25 2.25 0 0 1 0 3.182L12.451 19.091A2.25 2.25 0 0 1 10.86 19.75H8.104a48.524 48.524 0 0 1-.546-2.25h2.796Z" /></svg>`
}

const HeartIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" /></svg>`
}

const ChartIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" /></svg>`
}

const CameraIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6.827 6.175A2.31 2.31 0 0 1 8.91 5.25h6.18c.8 0 1.55.37 2.083.925l.12.125H19.5A2.25 2.25 0 0 1 21.75 8.55v9.9A2.25 2.25 0 0 1 19.5 20.7h-15A2.25 2.25 0 0 1 2.25 18.45v-9.9A2.25 2.25 0 0 1 4.5 6.3h2.207l.12-.125Zm5.173 4.125a3.75 3.75 0 1 0 0 7.5 3.75 3.75 0 0 0 0-7.5Z" /></svg>`
}

export default {
  components: {
    HomeIcon,
    CameraIcon,
    GraphIcon,
    DatabaseIcon,
    PillIcon,
    HeartIcon,
    ChartIcon
  }
}
</script>
