import json
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
import time

KAFKA_BROKER = "kafka:9092"
RAW_TOPIC = "raw_text_data"
PROCESSED_TOPIC = "processed_text_data"
CONSUMER_GROUP = "etl_stream_group"  # 使用 consumer group

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

def process_content(content):
    """
    處理訊息內容：
      - 若包含 "example"，則回傳 "example"
      - 否則回傳原始內容
    """
    if "example" in content:
        return "example"
    return content

def main():
    wait_for_kafka()
    consumer = KafkaConsumer(
        RAW_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id=CONSUMER_GROUP,
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    print("Stream Processor 已啟動，等待訊息處理...")
    for message in consumer:
        data = message.value
        url = data.get("url", "N/A")
        original_content = data.get("content", "")
        processed_content = process_content(original_content)
        new_message = {"url": url, "content": processed_content}
        producer.send(PROCESSED_TOPIC, new_message)
        print("已處理訊息：", new_message)

if __name__ == "__main__":
    main()
