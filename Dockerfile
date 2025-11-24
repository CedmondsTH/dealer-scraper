# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install basic system dependencies
RUN apt-get update && \
    apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install Playwright and its dependencies (this handles all browser deps automatically)
RUN playwright install --with-deps chromium

# Expose port
EXPOSE 8080

# Start Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.enableCORS=false", "--server.address=0.0.0.0"]
