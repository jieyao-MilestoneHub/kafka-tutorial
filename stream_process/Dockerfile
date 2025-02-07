FROM python:3.9-slim

WORKDIR /app

# 複製 requirements 並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製 stream process 程式
COPY stream_process.py .

CMD ["python", "stream_process.py"]