
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """配置类"""

    # 应用配置
    APP_NAME: str = "Vanna BI"
    APP_VERSION: str = "0.0.1"

    # 服务配置
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    # 模型配置
    MODEL_NAME: str = ""
    MODEL_API_KEY: str = ""
    BASE_URL: str = ""

    # 数据库配置
    DB_HOST: str = ""
    DB_PORT: int = 3306
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""

    # 认证配置
    AUTH_SECRET_KEY: str = ""
    AUTH_COOKIE_NAME: str = ""
    
    # ========== 日志配置 ==========
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "vanna.log"
    LOG_DIR: str = "./logs"
    LOG_CONSOLE_OUTPUT: bool = True
    LOG_SPLIT_BY_LEVEL: bool = True
    LOG_JSON_FORMAT: bool = False
    LOG_ROTATION_TYPE: str = "time"
    LOG_ROTATION_BACKUP_COUNT: int = 7
    LOG_ROTATION_MAX_BYTES: int = 50 * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENV', 'dev')}",
        env_file_encoding='utf-8'
    )


settings = Settings()