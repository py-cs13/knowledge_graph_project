"""
本模块用于初始化日志配置，并提供日志装饰器，以便各模块记录函数调用及异常信息。
"""
import asyncio
import functools
import logging
import time

from src.settings import config

# 配置日志输出格式和级别
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# 获取全局logger对象
logger = logging.getLogger("knowledge_graph_app")


def log_execution(func):
    """ 记录函数执行时间、参数和返回值的装饰器，支持异步和同步函数 """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)  # 异步执行
            logging.info(
                f"Executed {func.__name__} | Args: {args}, Kwargs: {kwargs} | Time: {time.time() - start_time:.4f}s | Result: {result}")
            return result
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)  # 同步执行
            logging.info(
                f"Executed {func.__name__} | Args: {args}, Kwargs: {kwargs} | Time: {time.time() - start_time:.4f}s | Result: {result}")
            return result
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise

    # 自动检查是同步还是异步函数
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
