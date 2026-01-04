# 文件上传组件校验规则

## 支持的文件类型
- GeoTIFF
- PNG
- JPG

## 支持的文件后缀
- .tif
- .tiff
- .png
- .jpg
- .jpeg

## 最大文件体积
- ≤ 500MB

## 校验规则清单

### 1. 文件后缀校验
- 检查文件的后缀名是否在允许的列表中
- 忽略大小写，例如 .TIF 和 .tif 都被允许

### 2. 文件大小校验
- 检查文件大小是否 ≤ 500MB（500 * 1024 * 1024 bytes）

### 3. MIME 类型校验
- PNG/JPG 文件：检查 MIME 类型是否为 image/png、image/jpeg 或 image/jpg
- GeoTIFF 文件：由于浏览器可能返回 application/octet-stream，主要通过后缀名校验

### 4. 上传数量限制
- 每次只能上传一个文件

## 使用说明

1. 引入组件
```vue
import Upload from '@/components/Upload/index.vue'
```

2. 在模板中使用
```vue
<Upload />
```

3. 组件会自动进行文件校验，校验通过后可以上传文件

## 错误提示
- 不支持的文件格式：显示错误提示
- 文件大小超过限制：显示错误提示
- 上传文件数量超过限制：显示错误提示
- 文件校验通过：显示成功提示
