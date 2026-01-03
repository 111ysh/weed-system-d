from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import scipy  # 验证scipy是否安装成功

# 初始化FastAPI
app = FastAPI(
    title="农田杂草系统接口服务",
    version="v0.1",
    description="基于scipy==1.15.3的本地部署服务"
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 根路径
@app.get("/", tags=["基础接口"])
def root():
    logger.info("根路径访问")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "农田杂草系统接口服务",
            "version": "v0.1",
            "docs": "/docs",
            "health": "/health",
            "check_scipy": "/check-scipy"
        }
    )

# 验证scipy版本
@app.get("/check-scipy", tags=["环境校验"])
def check_scipy():
    return {"scipy_version": scipy.__version__, "status": "success"}

# 健康检查接口
@app.get("/health", tags=["基础接口"])
def health_check():
    logger.info("服务健康检查通过")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "healthy", "message": "服务正常运行"}
    )

# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )