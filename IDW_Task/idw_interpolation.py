import numpy as np
from scipy.spatial import KDTree
import matplotlib.pyplot as plt
from osgeo import gdal
import os
from PIL import Image

# 设置中文字体支持
import matplotlib.font_manager as fm

# 尝试设置中文字体
chinese_fonts = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS', 'Microsoft YaHei', 'Noto Sans CJK SC']
available_fonts = [f.name for f in fm.fontManager.ttflist]

# 选择第一个可用的中文字体
chosen_font = 'DejaVu Sans'  # 默认字体
for font in chinese_fonts:
    if font in available_fonts:
        chosen_font = font
        break

plt.rcParams['font.sans-serif'] = [chosen_font]
plt.rcParams['axes.unicode_minus'] = False

print(f"使用字体: {chosen_font}")

# 检查字体是否支持中文
def check_chinese_support():
    """检查当前字体是否支持中文"""
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 1, figsize=(1, 1))
        ax.text(0.5, 0.5, '中', transform=ax.transAxes)
        fig.savefig('font_test.png')
        plt.close(fig)
        return True
    except:
        return False

# 如果字体不支持中文，使用英文标签
if not check_chinese_support():
    print("警告：中文字体不可用，将使用英文标签")
    # 英文标签版本
    EN_LABELS = {
        'title': 'Weed Density IDW Interpolation Heatmap',
        'xlabel': 'X Coordinate (pixels)',
        'ylabel': 'Y Coordinate (pixels)', 
        'colorbar': 'Weed Density (plants/m²)',
        'legend': 'Sample Points',
        'stats_template': 'Samples: {} | Max: {:.1f} | Min: {:.1f}'
    }
else:
    # 中文标签版本
    EN_LABELS = {
        'title': '杂草密度IDW插值热力图',
        'xlabel': 'X坐标（像素）',
        'ylabel': 'Y坐标（像素）',
        'colorbar': '杂草密度（株/m²）',
        'legend': '样本点',
        'stats_template': '样本点: {} | 最大密度: {:.1f} | 最小密度: {:.1f}'
    }


def read_sample_data(sample_path):
    """读取样本数据（自动识别GeoTIFF/PNG）"""
    try:
        if sample_path.endswith('.tif'):
            # 读取GeoTIFF格式
            dataset = gdal.Open(sample_path)
            density_matrix = dataset.ReadAsArray().astype(np.float32)
            geotransform = dataset.GetGeoTransform()
            origin_x, pixel_width = geotransform[0], geotransform[1]
            origin_y, pixel_height = geotransform[3], geotransform[5]

            # 提取有效样本点（过滤背景）
            y_indices, x_indices = np.where(density_matrix > 0)
            x_coords = origin_x + x_indices * pixel_width
            y_coords = origin_y + y_indices * pixel_height
            densities = density_matrix[y_indices, x_indices]
            dataset = None
        elif sample_path.endswith('.png'):
            # 读取PNG格式（灰度值映射为密度）
            img = Image.open(sample_path).convert('L')
            density_matrix = np.array(img).astype(np.float32) / 255 * 100  # 0-100密度范围
            y_indices, x_indices = np.where(density_matrix > 5)  # 过滤噪声
            
            # 改进：稀疏采样，避免样本点过多
            total_points = len(y_indices)
            if total_points > 10000:  # 如果样本点超过10000个，进行稀疏采样
                sampling_ratio = 10000 / total_points  # 目标采样比例
                step = max(1, int(1 / sampling_ratio))  # 计算采样步长
                selected_indices = np.arange(0, total_points, step)
                
                x_coords = x_indices[selected_indices].astype(np.float32)
                y_coords = y_indices[selected_indices].astype(np.float32)
                densities = density_matrix[y_indices[selected_indices], x_indices[selected_indices]]
                print(f"稀疏采样：从{total_points}个样本中选择了{len(x_coords)}个样本点")
            else:
                x_coords = x_indices.astype(np.float32)
                y_coords = y_indices.astype(np.float32)
                densities = density_matrix[y_indices, x_indices]
        else:
            print("错误：仅支持.tif和.png格式！")
            return None, None

        # 组合样本点
        samples = np.vstack((x_coords, y_coords)).T
        print(f"成功读取样本：{len(samples)}个有效样本点")
        return samples, densities
    except Exception as e:
        print(f"读取样本失败：{str(e)}")
        return None, None


def idw_interpolation(samples, densities, grid_x, grid_y, power=2, max_neighbors=10):
    """
    核心IDW插值计算（改进版，支持参数调节）
    
    参数:
    - samples: 样本点坐标 (N, 2)
    - densities: 样本点密度值 (N,)
    - grid_x, grid_y: 插值网格
    - power: 距离衰减系数 (默认2)
    - max_neighbors: 最大近邻点数 (默认10)
    """
    tree = KDTree(samples)
    grid_points = np.vstack((grid_x.ravel(), grid_y.ravel())).T
    interpolated = np.zeros(grid_points.shape[0])
    
    # 批量查询以提高性能
    k_neighbors = min(max_neighbors, len(samples))
    
    print(f"正在使用IDW插值，参数：power={power}, max_neighbors={k_neighbors}")
    
    # 分批处理以减少内存占用
    batch_size = 1000
    for i in range(0, len(grid_points), batch_size):
        end_idx = min(i + batch_size, len(grid_points))
        batch_points = grid_points[i:end_idx]
        
        # 查询近邻点
        distances, indices = tree.query(batch_points, k=k_neighbors)
        
        # 计算权重
        distances = np.maximum(distances, 1e-8)  # 避免除零
        weights = 1 / (distances ** power)
        
        # 批量计算插值结果
        batch_interpolated = np.sum(weights * densities[indices], axis=1) / np.sum(weights, axis=1)
        interpolated[i:end_idx] = batch_interpolated
        
        if i % (batch_size * 10) == 0:
            print(f"处理进度: {i/len(grid_points)*100:.1f}%")

    return interpolated.reshape(grid_x.shape)


def generate_heatmap():
    """主函数：生成热力图"""
    # 1. 配置文件路径（无需修改，样本已重命名）
    sample_path = "weed_sample.png"  # 使用PNG格式样本
    output_path = "weed_density_heatmap.png"

    # 2. 读取样本
    samples, densities = read_sample_data(sample_path)
    if samples is None or len(samples) < 3:
        print("错误：样本点不足3个，无法插值！")
        return

    # 3. 创建插值网格
    x_min, x_max = samples[:, 0].min(), samples[:, 0].max()
    y_min, y_max = samples[:, 1].min(), samples[:, 1].max()
    x_range = np.arange(x_min - 10, x_max + 10, 1)  # 扩展边界，分辨率1
    y_range = np.arange(y_min - 10, y_max + 10, 1)
    grid_x, grid_y = np.meshgrid(x_range, y_range)

    # 4. 执行插值
    print("正在计算插值...")
    heatmap = idw_interpolation(samples, densities, grid_x, grid_y, power=2, max_neighbors=10)

    # 5. 保存热力图
    plt.figure(figsize=(12, 10))
    
    # 主热力图
    im = plt.imshow(heatmap, extent=(x_min - 10, x_max + 10, y_min - 10, y_max + 10), 
                    cmap='YlOrRd', alpha=0.8)
    
    # 叠加样本点（根据密度值着色）
    sample_colors = densities / densities.max() if densities.max() > 0 else densities
    scatter = plt.scatter(samples[:, 0], samples[:, 1], c=sample_colors, 
                         cmap='viridis', s=20, alpha=0.7, edgecolors='black', linewidth=0.5,
                         label=f'{EN_LABELS["legend"]} ({len(samples)}个)' if '个' in EN_LABELS["legend"] else f'{EN_LABELS["legend"]} ({len(samples)})')
    
    # 添加颜色条
    cbar = plt.colorbar(im, label=EN_LABELS["colorbar"])
    cbar.ax.tick_params(labelsize=12)
    
    # 图表美化
    plt.title(EN_LABELS["title"], fontsize=16, fontweight='bold')
    plt.xlabel(EN_LABELS["xlabel"], fontsize=12)
    plt.ylabel(EN_LABELS["ylabel"], fontsize=12)
    
    # 添加网格
    plt.grid(True, alpha=0.3)
    
    # 图例
    plt.legend(loc='upper right', fontsize=10)
    
    # 添加统计信息
    stats_text = EN_LABELS["stats_template"].format(len(samples), heatmap.max(), heatmap.min())
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
             fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"成功！热力图已保存为：{output_path}")
    print(f"热力图尺寸：{heatmap.shape}，最大密度：{heatmap.max():.2f}，最小密度：{heatmap.min():.2f}")


# 脚本入口点
if __name__ == "__main__":
    print("=== 杂草密度IDW插值系统 ===")
    print("开始生成热力图...")
    generate_heatmap()
    print("完成！")