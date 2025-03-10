# 使用官方Python基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y curl libc6 git && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download zh_core_web_sm  || true

# 复制项目代码
COPY . .

# 对外暴露端口
EXPOSE 8000

# 启动 FastAPI 服务
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
