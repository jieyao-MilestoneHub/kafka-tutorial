#!/bin/bash
set -e

echo "等待 Kafka 端口開放中..."

MAX_RETRIES=30
RETRY_INTERVAL=2
RETRY_COUNT=0

while ! nc -z kafka 9092; do
  RETRY_COUNT=$((RETRY_COUNT+1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "❌ Kafka 端口在預期時間內未開放，退出！"
    docker logs kafka
    exit 1
  fi
  echo "Kafka 端口尚未開放，等待 ${RETRY_INTERVAL} 秒（嘗試次數：${RETRY_COUNT}）..."
  sleep ${RETRY_INTERVAL}
done

echo "✅ Kafka 端口已開放，繼續創建 topics..."

KAFKA_BIN="/opt/kafka/bin"

${KAFKA_BIN}/kafka-topics.sh --bootstrap-server kafka:9092 --create --if-not-exists --topic raw_text_data --partitions 3 --replication-factor 1
${KAFKA_BIN}/kafka-topics.sh --bootstrap-server kafka:9092 --create --if-not-exists --topic processed_text_data --partitions 3 --replication-factor 1

echo "🎯 目前已存在的 topics："
${KAFKA_BIN}/kafka-topics.sh --bootstrap-server kafka:9092 --list

echo "🎉 Kafka topic 初始化完成。"