# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for Playwright
RUN apt-get update && \
    apt-get install -y \
    curl \
    unzip \
    wget \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    libxss1 \
    libgconf-2-4 \
    libexpat1 \
    libxshmfence1 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    playwright install chromium && \
    playwright install-deps chromium

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.enableCORS=false", "--server.address=0.0.0.0"]
