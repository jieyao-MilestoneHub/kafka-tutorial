import json
import sqlite3
from kafka import KafkaConsumer
from sklearn.feature_extraction.text import TfidfVectorizer
from kafka.errors import KafkaError
import time

# Kafka broker 與 topic 設定
KAFKA_BROKER = "kafka:9092"
TOPIC_NAME = "processed_text_data"
CONSUMER_GROUP = "etl_consumer_group"  # 使用 consumer group 以便水平擴展

# SQLite 資料庫儲存路徑（容器內映射資料夾，可依需求調整）
DB_PATH = "/app/etl_data.db"

def wait_for_kafka(broker="kafka:9092", retries=30, delay=2):
    """等待 Kafka 準備好"""
    for i in range(retries):
        try:
            consumer = KafkaConsumer(bootstrap_servers=broker)
            consumer.close()
            print("✅ Kafka 連線成功！")
            return
        except KafkaError:
            print(f"⚠️ Kafka 尚未就緒，等待 {delay} 秒後重試（{i+1}/{retries}）...")
            time.sleep(delay)
    print("❌ Kafka 仍然無法連線，請檢查 Kafka 服務！")
    exit(1)

def simple_embedding(text):
    """將單一文本轉換為 TF-IDF 向量"""
    vectorizer = TfidfVectorizer()
    embedding = vectorizer.fit_transform([text]).toarray()
    return embedding.tolist()[0]  # 轉換為 Python List 格式，方便存入 SQLite

def init_db():
    """初始化 SQLite 資料庫"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS text_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            content TEXT,
            embedding TEXT
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
    """, (url, content, json.dumps(embedding)))  # 轉換 embedding 為 JSON 字串儲存
    conn.commit()
    conn.close()

def main():
    wait_for_kafka()
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BROKER,
        group_id=CONSUMER_GROUP,
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    print("Consumer 已啟動，等待訊息...")

    for message in consumer:
        data = message.value
        url = data.get("url", "N/A")
        content = data.get("content", "")

        if not content.strip():  # 忽略空訊息
            print(f"⚠️ 忽略空訊息：{url}")
            continue

        # 轉換內容為向量
        embedding = simple_embedding(content)
        save_to_db(url, content, embedding)
        print(f"✅ 已將資料存入 DB：{url}")

if __name__ == "__main__":
    init_db()
    main()