<template>
  <div class="file-upload-container">
    <h3 class="upload-title">文件上传</h3>
    
    <el-upload
      class="upload-dragger"
      action="/api/upload"
      accept=".tif,.tiff,.png,.jpg,.jpeg"
      :drag="true"
      :multiple="true"
      :limit="5"
      :file-list="fileList"
      :on-exceed="handleExceed"
      :before-upload="handleBeforeUpload"
      :on-progress="handleProgress"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-remove="handleRemove"
      :show-file-list="true"
    >
      <el-icon class="upload-icon"><UploadFilled /></el-icon>
      <div class="upload-text">
        <span class="primary-text">点击或拖拽文件到此处上传</span>
        <span class="secondary-text">支持 .tif/.tiff/.png/.jpg/.jpeg 格式，单个文件最大 500MB，最多上传 5 个文件</span>
      </div>
      <el-button type="primary" :style="{ backgroundColor: '#165DFF', borderColor: '#165DFF', marginTop: '20px' }">
        选择文件
      </el-button>
    </el-upload>
    
    <!-- 文件列表自定义展示 -->
    <div v-if="fileList.length > 0" class="file-list-section">
      <h4 class="file-list-title">文件列表</h4>
      <div class="file-list">
        <div
          v-for="file in fileList"
          :key="file.uid"
          class="file-item"
          :class="{
            'uploading': file.status === 'uploading',
            'success': file.status === 'success',
            'fail': file.status === 'fail'
          }"
        >
          <!-- 文件图标 -->
          <div class="file-icon">
            <el-icon v-if="isGeoTIFF(file.name)"><Document /></el-icon>
            <el-icon v-else-if="isImage(file.name)"><Picture /></el-icon>
            <el-icon v-else><DocumentCopy /></el-icon>
          </div>
          
          <!-- 文件信息 -->
          <div class="file-info">
            <div class="file-name">{{ file.name }}</div>
            <div class="file-meta">
              <span class="file-size">{{ formatFileSize(file.size) }}</span>
              <span class="file-status">
                <template v-if="file.status === 'ready'">待上传</template>
                <template v-else-if="file.status === 'uploading'">上传中</template>
                <template v-else-if="file.status === 'success'">上传成功</template>
                <template v-else-if="file.status === 'fail'">上传失败</template>
              </span>
            </div>
            
            <!-- 进度条 -->
            <el-progress
              v-if="file.status === 'uploading'"
              :percentage="file.percentage"
              :stroke-width="4"
              :format="progressFormat"
              class="file-progress"
            />
          </div>
          
          <!-- 操作按钮 -->
          <div class="file-actions">
            <!-- 上传成功图标 -->
            <el-icon v-if="file.status === 'success'" class="success-icon"><CircleCheckFilled /></el-icon>
            
            <!-- 失败重试按钮 -->
            <el-button
              v-else-if="file.status === 'fail'"
              type="text"
              size="small"
              @click="handleRetry(file)"
              class="retry-btn"
            >
              <el-icon><Refresh /></el-icon>
            </el-button>
            
            <!-- 删除按钮 -->
            <el-button
              type="text"
              size="small"
              @click="handleRemove(file)"
              class="delete-btn"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  UploadFilled,
  Document,
  Picture,
  DocumentCopy,
  CircleCheckFilled,
  Refresh,
  Delete
} from '@element-plus/icons-vue'

// 引入文件格式校验脚本
import { validateFile } from '../../utils/fileValidate.js'

const fileList = ref([])
const uploadedFileIds = ref([])

// 检查是否为 GeoTIFF 文件
const isGeoTIFF = (fileName) => {
  const ext = fileName.toLowerCase().split('.').pop()
  return ext === 'tif' || ext === 'tiff'
}

// 检查是否为图片文件
const isImage = (fileName) => {
  const ext = fileName.toLowerCase().split('.').pop()
  return ext === 'png' || ext === 'jpg' || ext === 'jpeg'
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (size < 1024) {
    return size + ' B'
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(2) + ' KB'
  } else if (size < 1024 * 1024 * 1024) {
    return (size / (1024 * 1024)).toFixed(2) + ' MB'
  } else {
    return (size / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
  }
}

// 进度条格式化
const progressFormat = (percentage) => {
  return `${percentage.toFixed(0)}%`
}

// 文件超出数量限制
const handleExceed = (files, fileList) => {
  ElMessage.warning(`最多只能上传 5 个文件，本次选择了 ${files.length} 个文件，将被忽略`)}

// 检查文件是否重复
const isFileDuplicate = (file) => {
  return fileList.value.some(item => item.name === file.name && item.size === file.size)}

// 文件上传前的校验
const handleBeforeUpload = async (file) => {
  // 1. 检查文件大小（500MB = 500 * 1024 * 1024 bytes）
  const maxSize = 500 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error(`文件 ${file.name} 大小超过 500MB 限制`)
    return false
  }
  
  // 2. 检查文件是否重复
  if (isFileDuplicate(file)) {
    ElMessage.warning(`文件 ${file.name} 已存在，请勿重复上传`)
    return false
  }
  
  // 3. 调用文件格式校验脚本
  const validationResult = await validateFile(file);
  if (!validationResult.valid) {
    ElMessage.error(validationResult.error);
    return false;
  }
  
  return true
}

// 上传进度处理
const handleProgress = (event, file, fileList) => {
  // 更新文件列表中的进度信息
  const index = fileList.value.findIndex(item => item.uid === file.uid)
  if (index !== -1) {
    fileList.value[index].percentage = event.percent
  }
}

// 上传成功处理
const handleSuccess = (response, file, fileList) => {
  // 预留后端返回结果处理逻辑（存储文件ID，用于后续推理请求）
  // 示例：获取文件ID并存储
  const fileId = response?.file_id || `file-${Date.now()}` // 模拟文件ID
  uploadedFileIds.value.push(fileId)
  
  ElMessage.success(`文件 ${file.name} 上传成功`)
}

// 上传失败处理
const handleError = (error, file, fileList) => {
  ElMessage.error(`文件 ${file.name} 上传失败，请重试`)
}

// 移除文件
const handleRemove = (file) => {
  const index = fileList.value.findIndex(item => item.uid === file.uid)
  if (index !== -1) {
    fileList.value.splice(index, 1)
    ElMessage.success(`文件 ${file.name} 已移除`)
  }
}

// 重试上传
const handleRetry = (file) => {
  // 重置文件状态，重新上传
  const index = fileList.value.findIndex(item => item.uid === file.uid)
  if (index !== -1) {
    fileList.value[index].status = 'ready'
    // 触发重新上传逻辑
    // 注意：这里需要根据实际需求实现重新上传，Element Plus 的 Upload 组件默认不支持重试，需要自定义实现
    ElMessage.info(`文件 ${file.name} 开始重试上传`)
  }
}
</script>

<style scoped>
.file-upload-container {
  width: 100%;
  max-width: 700px;
  margin: 0 auto;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 30px;
  transition: all 0.3s ease;
}

.upload-title {
  font-size: 20px;
  font-weight: 600;
  color: #333333;
  margin: 0 0 25px 0;
  text-align: center;
}

.upload-dragger {
  border: 2px dashed #dcdfe6;
  border-radius: 10px;
  background-color: #fafafa;
  padding: 50px 20px;
  text-align: center;
  transition: all 0.3s ease;
}

.upload-dragger:hover {
  border-color: #165DFF;
  background-color: #f0f5ff;
}

.upload-dragger.is-dragover {
  border-color: #165DFF;
  background-color: #e6f0ff;
  box-shadow: 0 0 0 2px rgba(22, 93, 255, 0.1);
}

.upload-icon {
  font-size: 48px;
  color: #165DFF;
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.upload-dragger:hover .upload-icon {
  transform: scale(1.1);
}

.upload-text {
  margin-bottom: 20px;
}

.primary-text {
  display: block;
  font-size: 16px;
  font-weight: 500;
  color: #333333;
  margin-bottom: 8px;
}

.secondary-text {
  display: block;
  font-size: 14px;
  color: #999999;
}

.file-list-section {
  margin-top: 30px;
}

.file-list-title {
  font-size: 16px;
  font-weight: 500;
  color: #333333;
  margin: 0 0 15px 0;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background-color: #fafafa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.file-item.uploading {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.file-item.success {
  border-color: #67c23a;
  background-color: #f0f9eb;
}

.file-item.fail {
  border-color: #f56c6c;
  background-color: #fef0f0;
}

.file-icon {
  font-size: 28px;
  margin-right: 16px;
}

.file-icon :deep(.el-icon) {
  font-size: 28px;
  color: #165DFF;
}

.file-item.success .file-icon :deep(.el-icon) {
  color: #67c23a;
}

.file-item.fail .file-icon :deep(.el-icon) {
  color: #f56c6c;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #333333;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #999999;
  margin-bottom: 8px;
}

.file-status {
  font-weight: 500;
}

.file-item.uploading .file-status {
  color: #409eff;
}

.file-item.success .file-status {
  color: #67c23a;
}

.file-item.fail .file-status {
  color: #f56c6c;
}

.file-progress {
  margin-top: 8px;
}

.file-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.success-icon {
  font-size: 20px;
  color: #67c23a;
}

.retry-btn :deep(.el-icon) {
  color: #409eff;
}

.delete-btn :deep(.el-icon) {
  color: #909399;
}

.delete-btn:hover :deep(.el-icon) {
  color: #f56c6c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .file-upload-container {
    padding: 20px;
    margin: 0 15px;
  }
  
  .upload-dragger {
    padding: 30px 15px;
  }
  
  .upload-title {
    font-size: 18px;
  }
  
  .primary-text {
    font-size: 14px;
  }
  
  .secondary-text {
    font-size: 12px;
  }
  
  .file-item {
    padding: 12px;
  }
  
  .file-icon {
    font-size: 24px;
    margin-right: 12px;
  }
  
  .file-icon :deep(.el-icon) {
    font-size: 24px;
  }
}
</style>