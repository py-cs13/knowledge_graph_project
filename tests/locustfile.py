from locust import HttpUser, task, between
import random
import json


class KnowledgeGraphUser(HttpUser):
    wait_time = between(1, 2)  # 每个任务间等待 1-2 秒

    @task(3)  # 这个任务会被执行更多次，权重高
    def query_node(self):
        # 随机生成查询参数（这些参数可以根据实际的数据调整）
        query_data = [
            {
                "label": "PERSON",
                "node_id": "77272d45-d33e-4bc0-83e4-e758f32b815d"
            },
            {
                "label": "DATE",
                "node_id": "ccdfedf6-3cb6-4b14-a3c1-33309d99e90f"
            },
            {
                "label": "GPE",
                "node_id": "28130d1c-4983-45e3-990b-9a2860020f20"
            }
        ]

        # 构建查询参数
        index = random.randint(0, len(query_data) - 1)
        label = query_data[index]["label"]
        node_id = query_data[index]["node_id"]
        params = {
            "label": label,
            "node_id": node_id
        }

        # 执行 GET 请求
        response = self.client.get("/query_node", params=params)

        # 输出日志以查看请求结果
        if response.status_code == 200:
            print(f"Query node {node_id} succeeded.")
        else:
            print(f"Query node {node_id} failed with status {response.status_code}.")
