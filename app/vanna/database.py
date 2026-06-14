from vanna.tools import RunSqlTool
from vanna.integrations.mysql import MySQLRunner
from app.core.config import settings
from app.core.logging_config import get_logger
from functools import lru_cache

logger = get_logger(__name__)

@lru_cache(maxsize=1)
def get_db_tool():
    """获取数据库工具"""
    logger.info("创建数据库连接", 
                host=settings.DB_HOST, 
                port=settings.DB_PORT,
                database=settings.DB_NAME)
    try:
        return RunSqlTool(
            sql_runner = MySQLRunner(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME
            )
        )
    except Exception as e:
        logger.error("创建数据库连接失败", error=str(e), exc_info=True)
        raise

db_tool = get_db_tool()