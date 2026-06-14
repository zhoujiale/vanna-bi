import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

import structlog

from app.core.config import settings

# 从 settings 读取配置
APP_ENV = os.getenv("ENV", "dev")
LOG_LEVEL = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
LOG_FORMAT = "json" if settings.LOG_JSON_FORMAT else "text"
LOG_DIR = Path(settings.LOG_DIR)
LOG_MAX_BYTES = settings.LOG_ROTATION_MAX_BYTES
LOG_BACKUP_COUNT = settings.LOG_ROTATION_BACKUP_COUNT
LOG_SPLIT_BY_LEVEL = settings.LOG_SPLIT_BY_LEVEL
LOG_CONSOLE_OUTPUT = settings.LOG_CONSOLE_OUTPUT


def _safe_add_logger_name(logger, method_name, event_dict):
    """安全地添加 logger 名称，处理 logger 为 None 的情况"""
    if logger is not None:
        event_dict["logger"] = logger.name
    return event_dict


def _build_processors(is_json: bool) -> list:
    """构建共享处理器链"""
    shared = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso"),
        _safe_add_logger_name,
    ]

    if is_json:
        return [*shared, structlog.processors.JSONRenderer(ensure_ascii=False)]
    else:
        return [*shared, structlog.dev.ConsoleRenderer(colors=sys.stdout.isatty())]


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    is_json = LOG_FORMAT == "json"

    # 定义桥接 Formatter
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
        ],
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            *_build_processors(is_json),
        ],
    )

    # 配置 Handlers
    handlers: list[logging.Handler] = []

    # 文件 Handler
    if LOG_SPLIT_BY_LEVEL:
        levels = [
            (logging.DEBUG, "debug"),
            (logging.INFO, "info"),
            (logging.WARNING, "warning"),
            (logging.ERROR, "error"),
            (logging.CRITICAL, "critical")
        ]
        
        for level, level_name in levels:
            file_handler = _create_rotating_handler(
                LOG_DIR / f"{level_name}-{APP_ENV}.log",
                level
            )
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
    else:
        file_handler = _create_rotating_handler(
            LOG_DIR / f"app-{APP_ENV}.log",
            logging.DEBUG
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # 控制台 Handler
    if LOG_CONSOLE_OUTPUT:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LOG_LEVEL)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    # 配置 Root Logger
    root = logging.getLogger()
    root.handlers.clear()
    for h in handlers:
        root.addHandler(h)
    root.setLevel(LOG_LEVEL)

    # 初始化 structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # 统一第三方框架日志格式
    for name in ("uvicorn.access", "uvicorn.error", "fastapi", "sqlalchemy.engine"):
        lib_logger = logging.getLogger(name)
        lib_logger.handlers.clear()
        lib_logger.propagate = True


def _create_rotating_handler(file_path: Path, level: int) -> logging.Handler:
    """创建滚动日志处理器"""
    if settings.LOG_ROTATION_TYPE == "time":
        handler = TimedRotatingFileHandler(
            filename=file_path,
            when="midnight",
            interval=1,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
    else:
        handler = RotatingFileHandler(
            filename=file_path,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
    handler.setLevel(level)
    return handler


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """获取结构化日志器"""
    return structlog.get_logger(name)