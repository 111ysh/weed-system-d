import { createRouter, createWebHistory } from 'vue-router'

// 导入组件
import Login from '../views/Login/index.vue'

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    // 注册路由占位，后续实现
    component: () => import('../views/Register/index.vue')
  },
  {
    path: '/home',
    name: 'Home',
    // 首页路由占位，后续实现
    component: () => import('../views/Home/index.vue')
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router