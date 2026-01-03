# Day3

#### 1.配置文件

包含 Scipy、NumPy、GDAL、Matplotlib、Pillow 等依赖及版本约束（适配 Python3.7+，支持直接 pip 安装）

#### 2.IDW 插值核心脚本（代码）

文件名：`idw_interpolation.py`，包含 3 大核心逻辑：

1. 样本读取（自动识别 GeoTIFF/PNG 格式）；
2. IDW 插值计算（近邻点搜索 + 加权平均）；
3. 热力图生成与保存（含可视化标注）

#### 3.杂草密度热力图样本（可视化结果）

文件名：`weed_density_heatmap.png`，基于测试样本（GeoTIFF/PNG）生成的插值结果图