<template>
  <div class="home-container">
    <div class="header-section">
      <h1 class="main-title">农田杂草预测系统</h1>
      <el-button type="primary" @click="handleLogout" :style="{ backgroundColor: '#165DFF', borderColor: '#165DFF' }">
        退出登录
      </el-button>
    </div>
    
    <div class="upload-section">
      <h2 class="section-title">文件上传</h2>
      <p class="section-description">支持拖拽或点击上传，最多 5 个文件，单文件≤500MB</p>
      
      <!-- 引入文件上传组件 -->
      <FileUpload />
    </div>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

// 引入文件上传组件
import FileUpload from '../../components/Upload/FileUpload.vue'

const router = useRouter()

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('tempUser')
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.home-container {
  width: 100vw;
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.main-title {
  color: #165DFF;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.upload-section {
  max-width: 800px;
  margin: 0 auto;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 30px;
}

.section-title {
  color: #333333;
  margin: 0 0 10px 0;
  font-size: 20px;
  font-weight: 500;
}

.section-description {
  color: #666666;
  margin: 0 0 25px 0;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    gap: 15px;
  }
  
  .main-title {
    font-size: 20px;
  }
  
  .upload-section {
    padding: 20px;
    margin: 0 15px;
  }
  
  .section-title {
    font-size: 18px;
  }
}
</style>