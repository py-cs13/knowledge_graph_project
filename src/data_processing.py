"""
当前文件下的数据清洗与提取实体和关系均为测试逻辑，实际项目中会根据业务数据调整清洗与提取逻辑
"""

import json
import re
import uuid

import spacy

from neo4j_service import neo4j_service

nlp = spacy.load("zh_core_web_sm")  # 加载中文 NLP 模型


def clean_text(text):
    """对文本进行基础清理，如去除特殊字符和多余空格"""
    text = re.sub(r"[^\w\s·-]", "", text)  # 仅保留文字、空格、点、连字符
    text = re.sub(r"\s+", " ", text).strip()  # 规范空格
    return text


def load_and_clean_data(file_path):
    """加载 JSON 数据并进行清理"""
    with open(file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    cleaned_data = [{"raw_text": clean_text(item["raw_text"])} for item in raw_data]
    return cleaned_data


def extract_entities_and_relations(cleaned_text):
    """使用 NLP 提取实体和关系"""
    doc = nlp(cleaned_text)
    entities = {ent.text: ent.label_ for ent in doc.ents}  # 提取实体
    relations = []

    # 关系示例规则（可扩展）
    if "CEO" in cleaned_text or "创办" in cleaned_text or "创立" in cleaned_text:
        words = cleaned_text.split("是") if "是" in cleaned_text else cleaned_text.split("创办了")
        if len(words) > 1:
            subject = words[0].strip()
            obj = words[1].split("的")[0].strip()
            relations.append((subject, "担任", obj))

    return entities, relations


def process_and_store_data(file_path, neo4j_service):
    """加载清理后的数据，提取实体和关系，并存入 Neo4j"""
    cleaned_data = load_and_clean_data(file_path)  # 使用清理后的数据

    for item in cleaned_data:
        text = item["raw_text"]
        entities, relations = extract_entities_and_relations(text)

        # 存入 Neo4j
        for entity, label in entities.items():
            entity_id = str(uuid.uuid4())  # 生成唯一 ID
            neo4j_service.create_or_update_node(label, {"id": entity_id, "name": entity})

        print(relations)
        for sub, rel, obj in relations:
            sub_entity = {"id": str(uuid.uuid4()), "name": sub}  # 确保是字典
            obj_entity = {"id": str(uuid.uuid4()), "name": obj}
            neo4j_service.create_or_update_relationship("Entity", sub_entity, "Entity", obj_entity, rel)


if __name__ == "__main__":
    process_and_store_data("../data_processing/test_data.json", neo4j_service)
    print("清洗后的数据已存入 Neo4j")
