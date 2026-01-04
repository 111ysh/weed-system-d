"""
处方图生成工具 - Day 4 任务
整合IDW插值功能、除草规则和元数据，生成单张样本处方图

除草规则：
- 规则1：密度≥0.3株/㎡ → 常规除草 (优先级=1)
- 规则2：离玉米距离<30cm → 精准除草 (优先级=2)
- 优先级编码：0=不除草, 1=常规除草, 2=精准除草
"""

import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from osgeo import gdal
import os
from datetime import datetime
import json

class PrescriptionMapGenerator:
    """处方图生成器"""
    
    def __init__(self):
        # 除草规则参数 (2024年1月更新版)
        self.DENSITY_LOW = 5.0      # 低密度阈值 (株/㎡)
        self.DENSITY_HIGH = 15.0    # 高密度阈值 (株/㎡)
        self.DISTANCE_THRESHOLD = 30.0  # 距离阈值 (cm)
        
        # 元数据
        self.metadata = {
            "model_version": "v1.0",
            "generation_time": None,
            "weed_rules": {
                "rule_1": "density_based: <5 plants/m²=0, 5-15 plants/m²=1, >15 plants/m²=2",
                "rule_2": "distance_protection: distance<30cm -> no_weeding (protect_corn)"
            },
            "priority_encoding": {
                "0": "不除草",
                "1": "轻度除草 (5-15株/㎡)", 
                "2": "重度除草 (>15株/㎡)"
            },
            "density_calculation": "IDW插值算法，基于检测点密度值",
            "coordinate_system": "UTM 50N"
        }
    
    def load_detection_data(self, csv_path):
        """加载检测数据"""
        try:
            data = pd.read_csv(csv_path)
            required_columns = ['x_coord', 'y_coord', 'density_plants_per_m2', 'distance_to_corn_cm']
            
            # 检查必需列
            for col in required_columns:
                if col not in data.columns:
                    raise ValueError(f"缺少必需列: {col}")
            
            print(f"成功加载检测数据: {len(data)}个杂草样本")
            print("数据预览:")
            print(data.head())
            
            return data
        except Exception as e:
            print(f"加载检测数据失败: {str(e)}")
            return None
    
    def idw_interpolation(self, samples, values, grid_x, grid_y, power=2, max_neighbors=8):
        """IDW插值算法"""
        tree = KDTree(samples)
        grid_points = np.vstack((grid_x.ravel(), grid_y.ravel())).T
        interpolated = np.zeros(grid_points.shape[0])
        
        k_neighbors = min(max_neighbors, len(samples))
        print(f"IDW插值参数: power={power}, neighbors={k_neighbors}")
        
        batch_size = 1000
        for i in range(0, len(grid_points), batch_size):
            end_idx = min(i + batch_size, len(grid_points))
            batch_points = grid_points[i:end_idx]
            
            distances, indices = tree.query(batch_points, k=k_neighbors)
            distances = np.maximum(distances, 1e-8)
            weights = 1 / (distances ** power)
            
            batch_interpolated = np.sum(weights * values[indices], axis=1) / np.sum(weights, axis=1)
            interpolated[i:end_idx] = batch_interpolated
            
            if i % (batch_size * 10) == 0:
                progress = i / len(grid_points) * 100
                print(f"插值进度: {progress:.1f}%")
        
        return interpolated.reshape(grid_x.shape)
    
    def generate_density_map(self, data, output_size=(500, 500)):
        """生成杂草密度分布图"""
        # 创建网格
        x_min, x_max = data['x_coord'].min(), data['x_coord'].max()
        y_min, y_max = data['y_coord'].min(), data['y_coord'].max()
        
        # 扩展边界
        margin = 50
        x_min -= margin
        x_max += margin
        y_min -= margin
        y_max += margin
        
        x_range = np.linspace(x_min, x_max, output_size[1])
        y_range = np.linspace(y_min, y_max, output_size[0])
        grid_x, grid_y = np.meshgrid(x_range, y_range)
        
        # 准备样本数据
        samples = data[['x_coord', 'y_coord']].values
        densities = data['density_plants_per_m2'].values
        
        # 执行IDW插值
        print("正在生成密度分布图...")
        density_map = self.idw_interpolation(samples, densities, grid_x, grid_y)
        
        print(f"密度图生成完成: {density_map.shape}")
        print(f"密度范围: {density_map.min():.2f} - {density_map.max():.2f} 株/㎡")
        
        return density_map, (x_min, x_max, y_min, y_max)
    
    def generate_distance_map(self, data, output_size=(500, 500)):
        """生成玉米距离分布图"""
        # 使用相同的网格参数
        x_min, x_max = data['x_coord'].min() - 50, data['x_coord'].max() + 50
        y_min, y_max = data['y_coord'].min() - 50, data['y_coord'].max() + 50
        
        x_range = np.linspace(x_min, x_max, output_size[1])
        y_range = np.linspace(y_min, y_max, output_size[0])
        grid_x, grid_y = np.meshgrid(x_range, y_range)
        
        # 准备距离样本数据
        samples = data[['x_coord', 'y_coord']].values
        distances = data['distance_to_corn_cm'].values
        
        # 执行IDW插值
        print("正在生成距离分布图...")
        distance_map = self.idw_interpolation(samples, distances, grid_x, grid_y)
        
        print(f"距离图生成完成: {distance_map.shape}")
        print(f"距离范围: {distance_map.min():.1f} - {distance_map.max():.1f} cm")
        
        return distance_map
    
    def apply_weed_rules(self, density_map, distance_map):
        """应用除草规则，生成处方图"""
        print("正在应用除草规则...")
        
        # 初始化处方图
        prescription_map = np.zeros_like(density_map, dtype=np.uint8)
        
        # 规则2优先：离玉米近的杂草不除 (距离<30cm → 不除草)
        close_to_corn_mask = distance_map < self.DISTANCE_THRESHOLD
        prescription_map[close_to_corn_mask] = 0
        
        # 规则1：密度分级除草 (仅在距离≥30cm的区域)
        far_from_corn_mask = ~close_to_corn_mask
        
        # 密度分级
        low_density_mask = (density_map < self.DENSITY_LOW) & far_from_corn_mask
        medium_density_mask = (density_map >= self.DENSITY_LOW) & (density_map < self.DENSITY_HIGH) & far_from_corn_mask
        high_density_mask = (density_map >= self.DENSITY_HIGH) & far_from_corn_mask
        
        # 应用密度规则
        prescription_map[low_density_mask] = 0      # <5株/㎡ → 不除草
        prescription_map[medium_density_mask] = 1   # 5-15株/㎡ → 轻度除草
        prescription_map[high_density_mask] = 2     # >15株/㎡ → 重度除草
        
        # 统计结果
        no_action = np.sum(prescription_map == 0)
        light_weeding = np.sum(prescription_map == 1)
        heavy_weeding = np.sum(prescription_map == 2)
        total_pixels = prescription_map.size
        
        # 统计受保护区域
        protected_area = np.sum(close_to_corn_mask)
        
        print(f"处方图生成完成:")
        print(f"  玉米保护区域 (距离<30cm): {protected_area} 像素 ({protected_area/total_pixels*100:.1f}%)")
        print(f"  不除草区域 (<5株/㎡): {no_action - protected_area} 像素 ({(no_action - protected_area)/total_pixels*100:.1f}%)")
        print(f"  轻度除草区域 (5-15株/㎡): {light_weeding} 像素 ({light_weeding/total_pixels*100:.1f}%)")
        print(f"  重度除草区域 (>15株/㎡): {heavy_weeding} 像素 ({heavy_weeding/total_pixels*100:.1f}%)")
        
        return prescription_map
    
    def add_metadata(self, data, density_map, prescription_map, extent):
        """添加元数据"""
        self.metadata["generation_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.metadata["data_summary"] = {
            "total_weeds_detected": len(data),
            "density_map_size": density_map.shape,
            "prescription_map_size": prescription_map.shape,
            "spatial_extent": {
                "x_min": float(extent[0]),
                "x_max": float(extent[1]),
                "y_min": float(extent[2]),
                "y_max": float(extent[3])
            }
        }
        self.metadata["processing_parameters"] = {
            "density_low_threshold": self.DENSITY_LOW,
            "density_high_threshold": self.DENSITY_HIGH,
            "distance_protection_threshold": self.DISTANCE_THRESHOLD,
            "idw_power": 2,
            "max_neighbors": 8
        }
        
        print("元数据添加完成")
    
    def save_as_geotiff(self, density_map, prescription_map, extent, output_path):
        """保存为GeoTIFF格式"""
        try:
            # 获取数据维度
            height, width = density_map.shape
            
            # 创建GeoTIFF文件 (双波段)
            driver = gdal.GetDriverByName('GTiff')
            dataset = driver.Create(output_path, width, height, 2, gdal.GDT_Float32)
            
            # 设置地理变换参数
            geotransform = [
                extent[0],  # 左上角x坐标
                (extent[1] - extent[0]) / width,  # 像素宽度
                0,  # 旋转
                extent[3],  # 左上角y坐标
                0,  # 旋转
                -(extent[3] - extent[2]) / height  # 像素高度
            ]
            dataset.SetGeoTransform(geotransform)
            
            # 设置投影 (UTM 50N)
            srs = gdal.osr.SpatialReference()
            srs.ImportFromEPSG(32650)  # UTM Zone 50N
            dataset.SetProjection(srs.ExportToWkt())
            
            # 写入数据
            band1 = dataset.GetRasterBand(1)
            band1.WriteArray(density_map)
            band1.SetDescription("杂草密度分布 (株/㎡)")
            
            band2 = dataset.GetRasterBand(2)
            band2.WriteArray(prescription_map.astype(np.float32))
            band2.SetDescription("除草处方图 (0=不除草, 1=常规除草, 2=精准除草)")
            
            # 写入元数据
            metadata_json = json.dumps(self.metadata, ensure_ascii=False, indent=2)
            dataset.SetMetadataItem('PROCESSING_INFO', metadata_json)
            
            # 关闭文件
            dataset = None
            
            print(f"GeoTIFF文件保存成功: {output_path}")
            return True
            
        except Exception as e:
            print(f"保存GeoTIFF文件失败: {str(e)}")
            return False
    
    def generate_prescription_map(self, csv_path, output_path):
        """生成完整处方图的主函数"""
        print("=== 处方图生成工具 ===")
        print("开始处理...")
        
        # 1. 加载检测数据
        data = self.load_detection_data(csv_path)
        if data is None:
            return False
        
        # 2. 生成密度分布图
        density_map, extent = self.generate_density_map(data)
        
        # 3. 生成距离分布图
        distance_map = self.generate_distance_map(data, density_map.shape)
        
        # 4. 应用除草规则
        prescription_map = self.apply_weed_rules(density_map, distance_map)
        
        # 5. 添加元数据
        self.add_metadata(data, density_map, prescription_map, extent)
        
        # 6. 保存为GeoTIFF
        success = self.save_as_geotiff(density_map, prescription_map, extent, output_path)
        
        if success:
            print("=== 处方图生成完成 ===")
            print(f"输出文件: {output_path}")
            return True
        else:
            print("=== 处方图生成失败 ===")
            return False


def main():
    """主函数"""
    generator = PrescriptionMapGenerator()
    
    # 设置路径
    csv_path = "test_data/weed_detection_results.csv"
    output_path = "prescription_output/处方图样本.tif"
    
    # 生成处方图
    success = generator.generate_prescription_map(csv_path, output_path)
    
    if success:
        print("🎉 第四天任务完成！")
        print("📊 生成了包含以下内容的处方图:")
        print("   - 杂草密度分布图 (波段1)")
        print("   - 除草处方图 (波段2)")
        print("   - 完整的元数据信息")
    else:
        print("❌ 处方图生成失败")


if __name__ == "__main__":
    main()