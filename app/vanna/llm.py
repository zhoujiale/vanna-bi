from vanna.integrations.openai import OpenAILlmService
from app.core.config import settings
from app.core.logging_config import get_logger
from functools import lru_cache

logger = get_logger(__name__)

@lru_cache(maxsize=1)
def get_llm():
    """
    获取LLM服务实例
    
    通过 lru_cache 实现单例模式，确保全局只有一个 LLM 实例，
    避免重复创建连接和资源浪费。
    """
    logger.info("创建LLM服务实例", 
                model=settings.MODEL_NAME, 
                base_url=settings.BASE_URL)
    try:
        return OpenAILlmService(
            model=settings.MODEL_NAME,
            api_key=settings.MODEL_API_KEY,
            base_url=settings.BASE_URL,
        )
    except Exception as e:
        logger.error("创建LLM服务失败", error=str(e), exc_info=True)
        raise

llm_service = get_llm()