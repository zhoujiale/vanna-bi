import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from vanna import Agent
from vanna.servers.base import ChatHandler
from app.core.logging_config import setup_logging, get_logger
from app.vanna.llm import llm_service
from app.vanna.tools import tools
from app.vanna.auth import user_resolver
from app.vanna.memory import agent_memory
from app.core.config import settings
from vanna.servers.fastapi.routes import register_chat_routes

# 初始化日志
setup_logging()
logger = get_logger(__name__)


app = FastAPI(title="Vanna BI API", version="0.1.0")

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = Agent(
    llm_service = llm_service,
    tool_registry = tools,
    user_resolver = user_resolver,
    agent_memory = agent_memory
)

chat_handler = ChatHandler(agent)

register_chat_routes(app, chat_handler, config={
    "dev_mode": False,
    "cdn_url": "https://img.vanna.ai/vanna-components.js"
})

@app.get("/")
async def root():
    return {"message": "Welcome to Vanna BI API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    
    logger.info("启动服务", 
                host=settings.SERVER_HOST, 
                port=settings.SERVER_PORT,
                env=os.getenv("ENV", "dev"))
    
    try:
        uvicorn.run(
            app,
            host=settings.SERVER_HOST,
            port=settings.SERVER_PORT
        )
    except Exception as e:
        logger.error("服务启动失败", error=str(e), exc_info=True)
        raise