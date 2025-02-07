import json
import time
import requests
from kafka import KafkaProducer, KafkaAdminClient
from kafka.errors import KafkaError

KAFKA_BROKER = "kafka:9092"
TOPIC_NAME = "raw_text_data"

# 範例 URL 列表（在真實應用中可動態更新）
URLS = [
    "https://example.com/data1.txt",
    "https://example.com/data2.txt",
    "https://example.com/data3.txt"
]

def wait_for_kafka():
    """等待 Kafka 準備好"""
    max_retries = 30
    retry_count = 0
    while retry_count < max_retries:
        try:
            admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_BROKER)
            admin_client.close()
            print("✅ Kafka is ready!")
            return
        except KafkaError:
            retry_count += 1
            print(f"⚠️ Kafka 尚未就緒，等待 2 秒（嘗試次數：{retry_count}）...")
            time.sleep(2)
    print("❌ Kafka 未在預期時間內就緒，退出！")
    exit(1)

def fetch_text(url):
    """從 URL 獲取純文本數據"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

def main():
    wait_for_kafka()

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(3, 9, 0)
    )

    while True:
        for url in URLS:
            text_data = fetch_text(url)
            if text_data:
                message = {"url": url, "content": text_data}
                producer.send(TOPIC_NAME, value=message)
                print(f"✅ Sent to Kafka: {message}")
        time.sleep(30)  # 每 30 秒爬取一次

if __name__ == "__main__":
    main()