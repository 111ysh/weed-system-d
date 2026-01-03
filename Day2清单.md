# Day2清单

### 1、环境兼容性校验记录

python==3.13.5

pip  ==  25.1 

### 2、依赖安装清单

**文件**：requirements.txt

可通过`pip install -r requirements.txt`一键安装所有依赖

### 3、FastAPI 初始化代码

**mian.py**

包含：

- 项目基础配置（标题、版本）
- 核心接口（`/health`健康检查、`/check-scipy`环境校验）

- 服务启动逻辑

直接运行`python main.py`可启动服务，无报错

### 4、服务验证截图

网页：http://localhost:8000/check-scipy

![image-20251231174350828](C:\Users\86184\AppData\Roaming\Typora\typora-user-images\image-20251231174350828.png)

网页：http://localhost:8000/health

![image-20251231174532429](C:\Users\86184\AppData\Roaming\Typora\typora-user-images\image-20251231174532429.png)

网页：http://localhost:8000/docs

![image-20251231174620876](C:\Users\86184\AppData\Roaming\Typora\typora-user-images\image-20251231174620876.png)

网页：[localhost:8000](http://localhost:8000/)

![image-20251231174720490](C:\Users\86184\AppData\Roaming\Typora\typora-user-images\image-20251231174720490.png)