## 🔍 系統默認的 Topic
在使用 `docker-compose up -d --build` 後，會發現在 Kafka 的 Topic 列表中，會出現系統內建的Topic，如: `__consumer_offsets`。這個 Topic 是一個系統內建的隱藏 Topic，主要用來儲存 Consumer Group 的偏移量（offsets）。

當 Kafka Consumer 讀取訊息時，它會追蹤自己讀到哪裡，並定期將這個進度（offset）儲存到 Kafka 的 __consumer_offsets Topic，這樣：

- Consumer 重啟後，可以從上次讀取的地方繼續，而不會重複處理訊息。
- 當有多個 Consumer Group 時，Kafka 會追蹤每個 Group 的 offset 來確保不同的 Consumer 不會互相干擾。