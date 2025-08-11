#!/usr/bin/env python3
"""
Development setup script for dealer scraper.

This script sets up the development environment with all necessary
dependencies and tools for professional development.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors gracefully."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up Dealer Scraper development environment...")
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    success = True
    
    # Install production dependencies
    success &= run_command(
        "pip install -r requirements.txt",
        "Installing production dependencies"
    )
    
    # Install development dependencies
    success &= run_command(
        "pip install pytest pytest-cov black flake8 mypy isort safety bandit",
        "Installing development dependencies"
    )
    
    # Install Playwright browsers
    success &= run_command(
        "playwright install chromium",
        "Installing Playwright browser"
    )
    
    # Create necessary directories
    directories = ["logs", "temp", "tests/fixtures"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Copy environment file
    env_example = Path("env.example")
    env_file = Path(".env")
    if env_example.exists() and not env_file.exists():
        env_file.write_text(env_example.read_text())
        print("📄 Created .env file from template")
    
    if success:
        print("\n🎉 Development environment setup completed successfully!")
        print("\nNext steps:")
        print("1. Review and update .env file with your settings")
        print("2. Run tests: python -m pytest tests/")
        print("3. Start development: python main.py")
        print("4. Format code: black .")
        print("5. Check types: mypy .")
    else:
        print("\n❌ Setup completed with errors. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()