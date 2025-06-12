from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from config import config
from logger import logger
import threading

app = FastAPI(title="牛魔日报 控制API")

class SourceStatusRequest(BaseModel):
    name: str
    enabled: bool

class IntervalRequest(BaseModel):
    interval_minutes: int

@app.get("/status")
def get_status():
    """获取当前服务状态和配置"""
    return {
        "sources": config.get_sources(),
        "postprocessors": config.get_postprocessors(),
        "schedule": config.get_schedule(),
        "webhook_url": config.get_webhook_url()
    }

@app.post("/reload")
def reload_config():
    try:
        config._load_config()
        logger.info("通过API重载了配置")
        return {"msg": "配置已重载"}
    except Exception as e:
        logger.error(f"API重载配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/source_status")
def update_source_status(req: SourceStatusRequest):
    ok = config.update_source_status(req.name, req.enabled)
    if not ok:
        raise HTTPException(status_code=404, detail="信息源不存在")
    return {"msg": f"信息源 {req.name} 状态已更新为 {'启用' if req.enabled else '禁用'}"}

@app.post("/interval")
def update_interval(req: IntervalRequest):
    ok = config.update_interval(req.interval_minutes)
    if not ok:
        raise HTTPException(status_code=400, detail="推送间隔无效")
    return {"msg": f"推送间隔已更新为 {req.interval_minutes} 分钟"}

# 你可以继续扩展更多API，如关键词管理、后处理器管理等

def run_api():
    import uvicorn
    logger.info("API 管理服务启动: http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_api() 