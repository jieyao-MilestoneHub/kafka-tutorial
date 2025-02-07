# Kafka ETL Pipeline 範例

## 目的
本範例展示如何利用 Kafka 構建一個簡單的 ETL (Extract-Transform-Load) 流程，透過以下三個主要元件：
- **Producer**：持續爬取或產生原始資料，並發送至 Kafka 的 `raw_text_data` Topic。
- **Stream Processor**：從 `raw_text_data` 中讀取訊息，根據特定規則（若訊息內容包含 "example" 則只保留 "example"，否則保持原樣）進行處理，並將結果發送至 `processed_text_data` Topic。
- **Consumer**：從 `processed_text_data` 中讀取經處理後的資料，並將其存入 SQLite 資料庫（或進一步處理）。

## 建置與執行

### 1. 建置並啟動所有容器
請在專案根目錄下執行：
```bash
docker-compose up --build
```

這將依序啟動 Kafka 服務、初始化 Topic 的服務（kafka-init），以及三個 ETL 服務：

- `etl-producer`
- `etl-consumer`
- `etl-stream-process`

### 2. 驗證 Kafka Topic
啟動後，可透過下列指令確認 Kafka 中已建立的 Topic：

```bash
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --list
```

預期輸出：

```nginx
raw_text_data
processed_text_data
```

### 3. 查看各容器日誌

- **Producer 日誌**：檢查是否持續發送訊息至 `raw_text_data`
```bash
docker logs -f etl-producer
```

- **Stream Processor 日誌**：檢查是否正確處理訊息，並發送至 `processed_text_data`
```bash
docker logs -f etl-stream-process
```

- **Consumer 日誌**：檢查是否正確接收處理後的訊息，並存入 
```bash
docker logs -f etl-consumer
```

### 4. 測試資料流程
**Producer** 會定期發送預設的訊息（例如：包含 "example" 的訊息）。
**Stream Processor** 會讀取這些訊息，若內容中包含 "example"，則將訊息內容轉為 "example"；否則保持原內容。
**Consumer** 則將處理後的結果存入 SQLite 資料庫。
你可以進入 etl-consumer 容器，並使用 sqlite3 工具查詢資料：
```bash
docker exec -it etl-consumer sqlite3 /app/etl_data.db "SELECT * FROM text_embeddings;"
```

## 停止與管理容器

停止所有容器：
```bash
docker-compose down
```
若需要重啟特定服務，可使用：
```bash
docker restart <容器名稱>
```
例如：
```bash
docker restart etl-producer
```

## 備註
- Producer 為持續運行的服務（利用 while 迴圈定時爬取並發送資料）。
- 若需要動態更新資料來源，可改進 Producer 讀取外部設定檔或透過 API 傳入新 URL，而無須重啟整個容器。

以上即為完整的範例說明與各檔案內容。你可以依據實際需求修改程式碼以擴展功能。

---

## 總結

以上提供了專案中所有檔案的詳細內容，包括 Docker Compose 配置、初始化 Topic 腳本、以及三個主要服務的程式碼與 Dockerfile、requirements.txt。  
請依照以上說明進行建置與測試，即可實現從 Producer → Stream Processor → Consumer 的完整 Kafka ETL Pipeline。