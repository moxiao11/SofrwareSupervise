"""
SmartOps Backend Application
智维 - 软件系统故障诊断与根因分析智能体
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SmartOps API",
    description="智维 - 软件系统故障诊断与根因分析智能体",
    version="0.1.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to SmartOps API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "smartops-backend"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
