FROM python:3.11-slim

WORKDIR /app

# OS dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ build-essential \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app/

# 중요: src 폴더를 패키지로 인식시키기 위해 PYTHONPATH 설정
ENV PYTHONPATH=/app/src:/app

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
