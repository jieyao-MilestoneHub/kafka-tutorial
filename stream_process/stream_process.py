import json
from kafka import KafkaConsumer, KafkaProducer

KAFKA_BROKER = "kafka:9092"
RAW_TOPIC = "raw_text_data"
PROCESSED_TOPIC = "processed_text_data"

consumer = KafkaConsumer(
    RAW_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

def process_content(content):
    """
    處理訊息內容：
      - 若包含 "example"，只回傳 "example"
      - 否則保持原樣
    """
    if "example" in content:
        return "example"
    return content

print("Starting stream processor...")
for message in consumer:
    data = message.value  # 例如：{"url": "https://example.com/data1.txt", "content": "Hello example world"}
    original_content = data.get("content", "")
    url = data.get("url", "N/A")
    processed_content = process_content(original_content)
    
    new_message = {
        "url": url,
        "content": processed_content
    }
    
    producer.send(PROCESSED_TOPIC, new_message)
    print("Processed message:", new_message)