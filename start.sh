#!/bin/bash
# Startup script for Railway deployment
# This script properly handles the PORT environment variable

# Use Railway's PORT if set, otherwise default to 8501
PORT=${PORT:-8501}

echo "Starting Streamlit on port $PORT..."

# Start Streamlit with the correct port
exec streamlit run run.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false

