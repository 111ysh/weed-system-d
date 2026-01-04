import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
// 引入Element Plus核心库
import ElementPlus from 'element-plus'
// 引入Element Plus的样式文件
import 'element-plus/dist/index.css'
// 引入Element Plus图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
// 引入路由配置
import router from './router'

const app = createApp(App)

// 注册Element Plus组件
app.use(ElementPlus)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册路由
app.use(router)

app.mount('#app')
