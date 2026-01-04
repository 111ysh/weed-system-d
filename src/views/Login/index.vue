<template>
  <div class="login-container">
    <div class="login-box">
      <h1 class="login-title">农田杂草预测系统</h1>
      
      <el-form
        :model="loginForm"
        :rules="loginRules"
        ref="loginFormRef"
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            type="text"
            autocomplete="off"
            class="login-input"
          >
            <template #prefix>
              <el-icon class="el-input__icon"><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            placeholder="请输入密码"
            type="password"
            show-password
            class="login-input"
          >
            <template #prefix>
              <el-icon class="el-input__icon"><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
            :style="{ backgroundColor: '#165DFF', borderColor: '#165DFF' }"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <el-link type="primary" href="/register" :style="{ color: '#165DFF' }">
          注册账号
        </el-link>
        <el-link type="primary" @click="handleSkipLogin" :style="{ color: '#165DFF' }">
          暂不登录
        </el-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
})

// 表单提交事件 - 后续对接 JWT 登录接口
const handleLogin = () => {
  loginFormRef.value.validate((valid) => {
    if (valid) {
      loading.value = true
      // 预留对接 JWT 登录接口，接收 token 并存储到 localStorage
      // 示例代码（后续替换为真实接口调用）：
      /*
      loginApi(loginForm).then(res => {
        const { token } = res.data
        localStorage.setItem('token', token)
        ElMessage.success('登录成功')
        router.push('/home')
      }).catch(err => {
        ElMessage.error('登录失败：' + err.message)
      }).finally(() => {
        loading.value = false
      })
      */
      
      // 模拟登录成功
      setTimeout(() => {
        loading.value = false
        ElMessage.success('登录成功（模拟）')
        localStorage.setItem('token', 'mock-token-123456')
        router.push('/home')
      }, 1000)
    }
  })
}

// 暂不登录 - 跳转到首页并存储临时用户状态
const handleSkipLogin = () => {
  localStorage.setItem('tempUser', 'guest')
  ElMessage.success('已设置临时用户，跳转到首页')
  router.push('/home')
}
</script>

<style scoped>
.login-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
}

.login-box {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-title {
  text-align: center;
  color: #165DFF;
  margin-bottom: 30px;
  font-size: 24px;
  font-weight: bold;
}

.login-form {
  width: 100%;
}

.login-input {
  width: 100%;
  max-width: 350px;
  margin: 0 auto;
  display: block;
  transition: all 0.3s ease;
}

.login-input:focus-within {
  box-shadow: 0 0 0 2px rgba(22, 93, 255, 0.2);
}

.login-button {
  width: 100%;
  max-width: 350px;
  margin: 0 auto;
  display: block;
  transition: all 0.3s ease;
  font-size: 16px;
  height: 40px;
}

.login-button:hover {
  background-color: #4080ff !important;
  border-color: #4080ff !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.3);
}

.login-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
  padding: 0 25px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-box {
    padding: 20px;
    margin: 0 20px;
  }
  
  .login-input,
  .login-button {
    max-width: 100%;
  }
  
  .login-footer {
    padding: 0;
  }
}
</style>