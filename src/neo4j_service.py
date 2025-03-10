"""
封装 Neo4j 数据库交互功能，支持增删改查操作，所有创建节点和关系均使用 MERGE 语句。
并实现连接池和 Redis 缓存策略以提高并发处理能力。
"""

import json

import redis
from neo4j import GraphDatabase, basic_auth

from src.settings import config
from src.logger import logger, log_execution


class Neo4jService:
    """
    Neo4jService 封装与 Neo4j 数据库的交互，包括节点与关系的增删改查操作。
    """

    def __init__(self):
        # 初始化 Neo4j 驱动，自动启用连接池
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=basic_auth(config.NEO4J_USER, config.NEO4J_PASSWORD),
            max_connection_pool_size=config.NEO4J_MAX_CONNECTION_POOL_SIZE,
        )
        logger.info("Neo4j driver initialized with connection pool size %s", config.NEO4J_MAX_CONNECTION_POOL_SIZE)

        # 初始化 Redis 客户端用于缓存
        self.redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
        logger.info("Redis client initialized on %s:%s (db: %s)", config.REDIS_HOST, config.REDIS_PORT, config.REDIS_DB)

    @log_execution
    def close(self):
        """
        关闭数据库连接
        """
        self.driver.close()
        logger.info("Neo4j driver closed")

    @log_execution
    def create_or_update_node(self, label: str, properties: dict):
        """
        创建或更新节点，使用 MERGE 语句保证节点唯一性。
        :param label: 节点标签（如 Person, Company 等）
        :param properties: 节点属性字典
        :return: 节点信息
        """
        cypher = f"MERGE (n:{label} {{id: $id}}) SET n += $props RETURN n"
        with self.driver.session() as session:
            result = session.write_transaction(
                lambda tx: tx.run(cypher, id=properties.get("id"), props=properties).single()
            )
            logger.info(f"Executing CQL: {cypher}")
            return result["n"] if result else None

    @log_execution
    def create_or_update_relationship(self, start_label: str, start_props: dict,
                                      end_label: str, end_props: dict,
                                      rel_type: str, rel_props: dict = None):
        """
        创建或更新关系（边），使用 MERGE 语句保证关系唯一性。
        :param start_label: 起始节点标签
        :param start_props: 起始节点属性（必须包含 id）
        :param end_label: 结束节点标签
        :param end_props: 结束节点属性（必须包含 id）
        :param rel_type: 关系类型
        :param rel_props: 关系属性字典（可选）
        :return: 关系信息
        """
        cypher = (
            f"MATCH (a:{start_label} {{id: $start_id}}), (b:{end_label} {{id: $end_id}}) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            f"SET r += $rel_props RETURN r"
        )
        with self.driver.session() as session:
            result = session.write_transaction(lambda tx: tx.run(
                cypher,
                start_id=start_props.get("id"),
                end_id=end_props.get("id"),
                rel_props=rel_props or {}
            ).single())
            logger.info(f"Executing CQL: {cypher}")
            return result["r"] if result else None

    @log_execution
    def get_node(self, label: str, node_id: str):
        """
        根据节点 id 获取节点信息，优先从 Redis 缓存中获取，若未命中则查询数据库后写入缓存。
        :param label: 节点标签
        :param node_id: 节点 id
        :return: 节点信息（字典格式）
        """
        cache_key = f"{label}:{node_id}"
        # 先尝试从 Redis 中获取缓存数据
        cached_node = self.redis_client.get(cache_key)
        if cached_node:
            logger.info("Retrieved node from Redis cache with key: %s", cache_key)
            return json.loads(cached_node)

        # 缓存未命中，从数据库查询
        cypher = f"MATCH (n:{label} {{id: $id}}) RETURN n"
        with self.driver.session() as session:
            result = session.read_transaction(lambda tx: tx.run(cypher, id=node_id).single())
            if result:
                node = result["n"]
                # 将节点信息转换为字典后写入 Redis 缓存，设置过期时间
                node_dict = dict(node)
                self.redis_client.set(cache_key, json.dumps(node_dict), ex=config.CACHE_EXPIRE_SECONDS)
                logger.info("Cached node in Redis with key: %s", cache_key)
                return node_dict
            else:
                return None

    @log_execution
    def delete_node(self, label: str, node_id: str):
        """
        删除节点及其相关关系，同时删除 Redis 缓存中的对应记录。
        :param label: 节点标签
        :param node_id: 节点 id
        """
        cypher = f"MATCH (n:{label} {{id: $id}}) DETACH DELETE n"
        with self.driver.session() as session:
            session.write_transaction(lambda tx: tx.run(cypher, id=node_id))
            logger.info("Deleted node %s with label %s", node_id, label)
        # 删除 Redis 缓存记录
        cache_key = f"{label}:{node_id}"
        self.redis_client.delete(cache_key)
        logger.info("Deleted Redis cache for key: %s", cache_key)


# 全局单例模式（项目启动时可直接使用）
neo4j_service = Neo4jService()
