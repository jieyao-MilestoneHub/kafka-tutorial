FROM python:3.9-slim

WORKDIR /app

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製 consumer 程式
COPY consumer.py .

CMD ["python", "consumer.py"]