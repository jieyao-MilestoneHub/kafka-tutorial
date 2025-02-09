#!/bin/bash
set -e

echo "等待 Kafka 啟動..."

MAX_RETRIES=60  # 延長等待時間到 120 秒
RETRY_INTERVAL=2
RETRY_COUNT=0
KAFKA_BROKER="kafka"  # Kafka 的 Docker Compose 服務名稱
KAFKA_TOPICS_CMD="/opt/kafka/bin/kafka-topics.sh"  # 根據你的 Kafka 版本修改

while ! nc -z $KAFKA_BROKER 9092; do
  RETRY_COUNT=$((RETRY_COUNT+1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "❌ Kafka 未在預期時間內啟動，退出！"
    exit 1
  fi
  echo "Kafka 尚未啟動，等待 ${RETRY_INTERVAL} 秒（嘗試 ${RETRY_COUNT} 次）..."
  sleep ${RETRY_INTERVAL}
done

echo "✅ Kafka 已啟動，開始建立 topics..."

# 創建 topics
${KAFKA_TOPICS_CMD} --bootstrap-server $KAFKA_BROKER:9092 --create --if-not-exists --topic raw_text_data --partitions 3 --replication-factor 1
${KAFKA_TOPICS_CMD} --bootstrap-server $KAFKA_BROKER:9092 --create --if-not-exists --topic processed_text_data --partitions 3 --replication-factor 1

echo "目前存在的 topics："
${KAFKA_TOPICS_CMD} --bootstrap-server $KAFKA_BROKER:9092 --list
echo "Kafka topic 初始化完成。"