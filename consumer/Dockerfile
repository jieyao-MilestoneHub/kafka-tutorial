# consumer/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 複製並安裝相依套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式原始碼
COPY consumer.py .

CMD ["python", "consumer.py"]
