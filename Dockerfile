# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y curl unzip && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    playwright install chromium

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.enableCORS=false"]
