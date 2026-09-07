"""
Logging Configuration
日志配置
"""
import os
import sys
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# 日志级别
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

# 确保日志目录存在
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# 移除默认处理器
logger.remove()

# 添加控制台处理器
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[service]}</cyan> | <cyan>{extra[trace_id]}</cyan> | <level>{message}</level>",
    level=LOG_LEVEL,
    colorize=True,
)

# 添加文件处理器
logger.add(
    LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[service]} | {extra[trace_id]} | {message}",
    level=LOG_LEVEL,
    rotation="10 MB",  # 每个文件最大10MB
    retention="7 days",  # 保留7天
    compression="zip",  # 压缩旧日志
    encoding="utf-8",
)

# 添加错误日志文件处理器
logger.add(
    "logs/error.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[service]} | {extra[trace_id]} | {message}",
    level="ERROR",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    encoding="utf-8",
)


def get_logger(service: str = "smartops", trace_id: str = "-"):
    """
    获取带有服务名和trace_id的logger
    """
    return logger.bind(service=service, trace_id=trace_id)


# 创建默认logger
default_logger = get_logger()
