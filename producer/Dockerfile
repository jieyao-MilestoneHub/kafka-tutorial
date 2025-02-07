FROM python:3.9-slim

WORKDIR /app

# 複製並安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製 producer 程式
COPY producer.py .

CMD ["python", "producer.py"]