import json
import sqlite3
from kafka import KafkaConsumer
from sentence_transformers import SentenceTransformer

# 在容器內部，使用 Kafka 服務名稱 (kafka:9092)
KAFKA_BROKER = "kafka:9092"
TOPIC_NAME = "processed_text_data"
DB_PATH = "/app/etl_data.db"

# 初始化嵌入模型（此處作為範例，可根據需要替換或移除）
model = SentenceTransformer('all-MiniLM-L6-v2')

def init_db():
    """初始化 SQLite 資料庫"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS text_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            content TEXT,
            embedding BLOB
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(url, content, embedding):
    """將資料存入 SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO text_embeddings (url, content, embedding)
        VALUES (?, ?, ?)
    """, (url, content, json.dumps(embedding)))
    conn.commit()
    conn.close()

def main():
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    for message in consumer:
        data = message.value  # 預期格式：{"url": ..., "content": ...}
        url = data.get("url", "N/A")
        content = data.get("content", "")
        
        # 轉換為嵌入（範例用，可根據需求調整）
        embedding = model.encode(content).tolist()
        save_to_db(url, content, embedding)
        print(f"Saved to DB: {url}, {content}")

if __name__ == "__main__":
    init_db()
    main()