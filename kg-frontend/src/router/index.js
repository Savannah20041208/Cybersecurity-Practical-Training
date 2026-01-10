import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Home from '../views/Home.vue'
import KnowledgeGraph from '../views/KnowledgeGraph.vue'
import DataBrowser from '../views/DataBrowser.vue'
import DrugDetail from '../views/DrugDetail.vue'
import DiseaseDetail from '../views/DiseaseDetail.vue'
import Analysis from '../views/Analysis.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '用户登录', requiresGuest: true }
  },
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首页 (问答主界面)', requiresAuth: true }
  },
  {
    path: '/knowledge-graph',
    name: 'KnowledgeGraph',
    component: KnowledgeGraph,
    meta: { title: '知识图谱展示页', requiresAuth: true }
  },
  {
    path: '/data-browser',
    name: 'DataBrowser',
    component: DataBrowser,
    meta: { title: '数据浏览页', requiresAuth: true }
  },
  {
    path: '/drug/:id?',
    name: 'DrugDetail',
    component: DrugDetail,
    meta: { title: '药物详情页', requiresAuth: true }
  },
  {
    path: '/disease/:id?',
    name: 'DiseaseDetail',
    component: DiseaseDetail,
    meta: { title: '疾病详情页', requiresAuth: true }
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: Analysis,
    meta: { title: '分析页', requiresAuth: true }
  },
  {
    path: '/config-management',
    name: 'ConfigManagement',
    component: () => import('../views/ConfigManagement.vue'),
    meta: { title: '配置管理', requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫，处理认证和更新页面标题
router.beforeEach(async (to, from, next) => {
  // 更新页面标题
  document.title = to.meta.title ? `${to.meta.title} - 智慧医疗知识服务平台` : '智慧医疗知识服务平台'
  
  const authStore = useAuthStore()
  
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // 未登录，跳转到登录页
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    
    
    // 已登录但需要验证token有效性
    try {
      const isValid = await authStore.checkAuth()
      if (!isValid) {
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
    } catch (error) {
      console.error('认证检查失败:', error)
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }
  
  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin) {
    if (!authStore.user || authStore.user.role !== 'admin') {
      // 非管理员用户，跳转到首页并显示错误
      alert('只有管理员可以访问此页面')
      next({ name: 'Home' })
      return
    }
  }
  
  // 检查是否是访客页面（如登录页）
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    // 已登录用户访问登录页，跳转到首页
    next({ name: 'Home' })
    return
  }
  
  next()
})

export default router
