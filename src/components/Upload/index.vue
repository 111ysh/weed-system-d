<template>
  <div class="upload-wrapper">
    <div class="upload-header">
      <h3 class="upload-title">文件上传</h3>
      <p class="upload-subtitle">支持上传 GeoTIFF/PNG/JPG 格式文件</p>
    </div>
    
    <el-upload
      class="upload-dragger"
      action=""
      :auto-upload="false"
      :before-upload="handleBeforeUpload"
      :on-error="handleError"
      :on-success="handleSuccess"
      :accept=".tif,.tiff,.png,.jpg,.jpeg"
      :file-list="fileList"
      :limit="1"
      :on-exceed="handleExceed"
      drag
    >
      <el-icon class="upload-icon"><Document /></el-icon>
      <div class="upload-text">
        <span class="upload-primary-text">点击或拖拽文件到此处上传</span>
        <span class="upload-secondary-text">支持 .tif/.tiff/.png/.jpg/.jpeg 格式，单个文件最大 500MB</span>
      </div>
      <el-button
        type="primary"
        :style="{ backgroundColor: '#165DFF', borderColor: '#165DFF', marginTop: '20px' }"
      >
        选择文件
      </el-button>
    </el-upload>
    
    <!-- 文件列表展示 -->
    <div v-if="fileList.length > 0" class="file-list-wrapper">
      <h4 class="file-list-title">已选择文件</h4>
      <div class="file-item">
        <el-icon class="file-item-icon"><DocumentCheck /></el-icon>
        <div class="file-item-info">
          <div class="file-item-name">{{ fileList[0].name }}</div>
          <div class="file-item-size">{{ formatFileSize(fileList[0].size) }}</div>
        </div>
        <el-button
          type="text"
          size="small"
          @click="handleRemove"
          :style="{ color: '#ff4d4f' }"
        >
          移除
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, DocumentCheck } from '@element-plus/icons-vue'

const fileList = ref([])

// 文件上传前的校验
const handleBeforeUpload = (file) => {
  // 1. 校验文件类型和后缀
  const validExtensions = ['.tif', '.tiff', '.png', '.jpg', '.jpeg']
  const fileExtension = `.${file.name.split('.').pop().toLowerCase()}`
  const isValidExtension = validExtensions.includes(fileExtension)
  
  if (!isValidExtension) {
    ElMessage.error('不支持的文件格式，请上传 GeoTIFF/PNG/JPG 格式文件，后缀为 .tif/.tiff/.png/.jpg/.jpeg')
    return false
  }
  
  // 2. 校验文件大小（500MB = 500 * 1024 * 1024 bytes）
  const maxSize = 500 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小超过限制，单个文件最大支持 500MB')
    return false
  }
  
  // 3. 校验文件类型（MIME 类型）
  const validMimeTypes = [
    'image/tiff',
    'image/png',
    'image/jpeg',
    'image/jpg' // 有些浏览器可能返回 image/jpg
  ]
  
  // 对于 GeoTIFF 文件，MIME 类型可能是 image/tiff 或 application/octet-stream
  const isGeoTIFF = ['.tif', '.tiff'].includes(fileExtension)
  const isImage = ['.png', '.jpg', '.jpeg'].includes(fileExtension)
  
  if (isImage && !validMimeTypes.includes(file.type)) {
    ElMessage.error('不支持的文件格式，请上传有效的 PNG/JPG 文件')
    return false
  }
  
  // GeoTIFF 文件可能返回 application/octet-stream，所以只校验后缀
  
  ElMessage.success('文件校验通过，可以上传')
  return true
}

// 文件超出数量限制
const handleExceed = (files, fileList) => {
  ElMessage.error('每次只能上传一个文件')
}

// 文件上传成功
const handleSuccess = (response, file, fileList) => {
  ElMessage.success('文件上传成功')
}

// 文件上传失败
const handleError = (error, file, fileList) => {
  ElMessage.error('文件上传失败，请重试')
}

// 移除文件
const handleRemove = () => {
  fileList.value = []
  ElMessage.success('文件已移除')
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
</script>

<style scoped>
.upload-wrapper {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 30px;
  transition: all 0.3s ease;
}

.upload-wrapper:hover {
  box-shadow: 0 6px 30px rgba(0, 0, 0, 0.12);
}

.upload-header {
  text-align: center;
  margin-bottom: 25px;
}

.upload-title {
  font-size: 22px;
  font-weight: 600;
  color: #333333;
  margin: 0 0 8px 0;
}

.upload-subtitle {
  font-size: 14px;
  color: #666666;
  margin: 0;
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

.upload-primary-text {
  display: block;
  font-size: 16px;
  font-weight: 500;
  color: #333333;
  margin-bottom: 8px;
}

.upload-secondary-text {
  display: block;
  font-size: 14px;
  color: #999999;
}

.file-list-wrapper {
  margin-top: 25px;
  padding: 20px;
  background-color: #fafafa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.file-list-title {
  font-size: 16px;
  font-weight: 500;
  color: #333333;
  margin: 0 0 15px 0;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background-color: #ffffff;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.file-item:hover {
  border-color: #165DFF;
  box-shadow: 0 2px 8px rgba(22, 93, 255, 0.15);
}

.file-item-icon {
  font-size: 24px;
  color: #67c23a;
  margin-right: 12px;
}

.file-item-info {
  flex: 1;
  min-width: 0;
}

.file-item-name {
  font-size: 14px;
  font-weight: 500;
  color: #333333;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-item-size {
  font-size: 12px;
  color: #999999;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .upload-wrapper {
    padding: 20px;
    margin: 0 15px;
  }
  
  .upload-dragger {
    padding: 30px 15px;
  }
  
  .upload-title {
    font-size: 20px;
  }
  
  .upload-primary-text {
    font-size: 14px;
  }
  
  .upload-secondary-text {
    font-size: 12px;
  }
}
</style>