# Knowledge Graph Project

本项目旨在构建一个知识图谱构建与查询系统，主要包括以下模块：

- **日志模块**：单独的日志文件及装饰器实现，对各个操作记录日志，便于问题追踪和调试。
- **Neo4j 服务模块**：基于 neo4j 封装数据库交互，支持增删改查操作（创建节点和关系时均使用 MERGE），并使用连接池和缓存策略以优化高并发场景下的性能。
- **数据处理模块**：对非结构化数据进行清洗、预处理，并提取实体和关系，为知识图谱构建提供数据。
- **FastAPI 查询接口**：基于 FastAPI 提供查询知识图谱的 HTTP API 接口。
- **压力测试模块**：通过高并发模拟工具对查询接口进行压力测试。


## 目录结构
knowledge_graph_project/    # 根目录
├── README.md
├── requirements.txt
├── .gitignore
├── Dockerfile
├── logs/
│   └── app.log     # 日志暂存
├── src/
│   ├── __init__.py
│   ├── config.py   # 环境参数设置
│   ├── logger.py   # 日志
│   ├── neo4j_service.py    # neo4j 服务
│   ├── data_processing.py  # 数据处理
│   └── app.py  # API接口实现
└── tests/
    └── locustfile.py  # 压测


## 压力测试

本项目使用 Locust 进行高并发压力测试。
安装依赖后，可使用以下命令启动压力测试（默认 locust 服务监听在 8089 端口）：

```bash
locust -f tests/locustfile.py --host=http://127.0.0.1:8000
```
然后在浏览器中访问 http://localhost:8089 根据提示设置并发用户数和请求速率，开始测试。