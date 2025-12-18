FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

# Make start script executable
RUN chmod +x start.sh

EXPOSE 8501

CMD ["./start.sh"]
