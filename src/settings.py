import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """ 全局配置 """
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USER = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    NEO4J_MAX_CONNECTION_POOL_SIZE = int(os.getenv("NEO4J_MAX_CONNECTION_POOL_SIZE", "50"))

    # 缓存配置
    CACHE_ENABLED = True
    CACHE_MAXSIZE = 128
    CACHE_EXPIRE_SECONDS = 3600  # 缓存过期时间（秒）

    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = int(os.getenv("REDIS_PORT"))
    REDIS_DB = int(os.getenv("REDIS_DB"))

    # 日志文件路径
    LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "app.log")


config = Config()
