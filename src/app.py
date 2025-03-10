"""
基于 FastAPI 实现知识图谱查询接口，优化后使用 Pydantic 模型校验 GET 请求参数。Pydantic模型临时放在当前文件。
"""
import json
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from src.logger import log_execution
from src.neo4j_service import neo4j_service

app = FastAPI()


class QueryNodeParams(BaseModel):
    label: str = Field(..., description="节点标签")
    node_id: Optional[str] = Query(None, description="节点ID")


@app.on_event("shutdown")
def shutdown_event():
    """
    应用关闭时关闭数据库连接
    """
    neo4j_service.close()


@app.get("/query_node")
@log_execution
async def query_node(
        label: str = Query(..., description="节点的标签"),
        node_id: Optional[str] = Query(None, description="节点ID")
):
    result = {
        "status": 200,
        "message": "succeed！",
        "data": []
    }
    try:
        # 构造缓存键
        cache_key = f"query_node:{label}:{node_id}" if node_id else f"query_node:{label}"

        # 尝试从 Redis 缓存获取数据
        cached_result = neo4j_service.redis_client.get(cache_key)
        if cached_result:
            result["data"] = [json.loads(cached_result)]
            return result

        data = neo4j_service.get_node(label, node_id)
        if not data:
            result["message"] = "failed, there is no current node！"
            return result

        # 确保返回 JSON 格式
        if not isinstance(data, dict):
            result["data"] = [json.loads(json.dumps(data))]
        result["data"] = data
        # 存入 Redis 缓存（有效期60秒）
        neo4j_service.redis_client.setex(cache_key, 60, json.dumps(data))

        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


# 用于本地测试
if __name__ == '__main__':
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
