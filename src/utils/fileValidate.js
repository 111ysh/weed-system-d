/**
 * 文件格式校验脚本
 * 用于精准识别 GeoTIFF/PNG/JPG 文件，排除非法格式
 */

/**
 * 校验文件后缀
 * @param {File} file - 待校验的文件对象
 * @returns {boolean} - 是否通过校验
 */
export const checkFileExtension = (file) => {
  // 支持的文件后缀列表（不区分大小写）
  const validExtensions = ['.tif', '.tiff', '.png', '.jpg', '.jpeg'];
  
  // 获取文件后缀（转为小写）
  const fileExtension = `.${file.name.split('.').pop().toLowerCase()}`;
  
  // 检查后缀是否在支持列表中
  return validExtensions.includes(fileExtension);
};

/**
 * 校验文件 MIME 类型
 * @param {File} file - 待校验的文件对象
 * @returns {boolean} - 是否通过校验
 */
export const checkFileMime = (file) => {
  // 支持的 MIME 类型映射
  const validMimeTypes = {
    '.tif': 'image/tiff',
    '.tiff': 'image/tiff',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg'
  };
  
  // 获取文件后缀（转为小写）
  const fileExtension = `.${file.name.split('.').pop().toLowerCase()}`;
  
  // 获取预期的 MIME 类型
  const expectedMimeType = validMimeTypes[fileExtension];
  
  // 检查 MIME 类型是否匹配
  return file.type === expectedMimeType;
};

/**
 * 校验 GeoTIFF 文件有效性
 * 通过读取文件头前 4 字节确认是否为标准 TIFF 格式
 * @param {File} file - 待校验的 GeoTIFF 文件对象
 * @returns {Promise<boolean>} - 是否通过校验
 */
export const checkGeoTiffValidity = (file) => {
  return new Promise((resolve) => {
    // 创建文件读取器
    const reader = new FileReader();
    
    // 读取文件头前 4 字节
    reader.onload = (event) => {
      try {
        // 获取文件头前 4 字节的二进制数据
        const arrayBuffer = event.target.result;
        const dataView = new DataView(arrayBuffer);
        
        // 读取前 4 字节
        const byte1 = dataView.getUint8(0);
        const byte2 = dataView.getUint8(1);
        const byte3 = dataView.getUint8(2);
        const byte4 = dataView.getUint8(3);
        
        // 标准 TIFF 格式的文件头标识
        // Little-endian: 49 49 2A 00 (II*)
        // Big-endian: 4D 4D 00 2A (MM*)
        const isLittleEndianTIFF = byte1 === 0x49 && byte2 === 0x49 && byte3 === 0x2A && byte4 === 0x00;
        const isBigEndianTIFF = byte1 === 0x4D && byte2 === 0x4D && byte3 === 0x00 && byte4 === 0x2A;
        
        // 如果是标准 TIFF 格式，返回 true，否则返回 false
        resolve(isLittleEndianTIFF || isBigEndianTIFF);
      } catch (error) {
        // 读取过程中发生错误，返回 false
        resolve(false);
      }
    };
    
    // 读取文件失败时的处理
    reader.onerror = () => {
      resolve(false);
    };
    
    // 仅读取文件的前 4 字节
    const blob = file.slice(0, 4);
    reader.readAsArrayBuffer(blob);
  });
};

/**
 * 统一的文件格式校验函数
 * @param {File} file - 待校验的文件对象
 * @returns {Promise<{valid: boolean, error: string|null}>} - 校验结果和错误信息
 */
export const validateFile = async (file) => {
  // 1. 校验文件后缀
  if (!checkFileExtension(file)) {
    return {
      valid: false,
      error: '仅支持 GeoTIFF (.tif/.tiff)、PNG (.png)、JPG (.jpg/.jpeg) 格式'
    };
  }
  
  // 2. 校验 MIME 类型
  if (!checkFileMime(file)) {
    return {
      valid: false,
      error: '文件格式与后缀不匹配，请检查文件完整性'
    };
  }
  
  // 3. 如果是 GeoTIFF 文件，额外校验文件头
  const fileExtension = `.${file.name.split('.').pop().toLowerCase()}`;
  if (fileExtension === '.tif' || fileExtension === '.tiff') {
    const isGeoTiffValid = await checkGeoTiffValidity(file);
    if (!isGeoTiffValid) {
      return {
        valid: false,
        error: 'GeoTIFF 文件损坏或非标准格式，无法上传'
      };
    }
  }
  
  // 所有校验通过
  return {
    valid: true,
    error: null
  };
};