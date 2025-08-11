#!/usr/bin/env python3
"""
Script to set the API key from environment and start the app
Make sure to set OPENAI_API_KEY environment variable before running this script
"""
import os
import subprocess
import sys

# Check if API key is set in environment
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    print("❌ OPENAI_API_KEY environment variable not set!")
    print("Please set it using: export OPENAI_API_KEY=your_api_key_here")
    sys.exit(1)

print(f"✅ API key found: {api_key[:20]}...")
print(f"✅ Environment variable confirmed: {os.environ.get('OPENAI_API_KEY', 'NOT FOUND')[:20]}...")

# Start the app with the environment variable
print("✅ Starting Streamlit app...")
subprocess.run(["streamlit", "run", "app.py"])
