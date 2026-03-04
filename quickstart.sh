#!/bin/bash
# Quick start script for Wealth Wellness Hub

set -e

echo "🚀 Wealth Wellness Hub - Quick Start"
echo "===================================="
echo ""

# Check Python
echo "✓ Checking Python environment..."
if [ ! -d ".venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
echo "✓ Virtual environment activated"

# Install backend dependencies
echo ""
echo "✓ Installing backend dependencies..."
pip install -r src/server/requirements.txt > /dev/null 2>&1 || {
    pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-jose bcrypt python-multipart python-dotenv email-validator passlib > /dev/null 2>&1
}
echo "  Dependencies installed"

# Setup environment file
echo ""
echo "✓ Setting up environment..."
if [ ! -f "src/server/.env" ]; then
    cp src/server/.env.example src/server/.env
    echo "  Created .env file (edit with your settings)"
fi

# Install frontend dependencies
echo ""
echo "✓ Installing frontend dependencies..."
cd src/web
npm install > /dev/null 2>&1 || echo "  npm install already complete"
cd ../..

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo ""
echo "  Backend (FastAPI):"
echo "    cd src/server"
echo "    python main.py"
echo "    # API will be at http://localhost:8000"
echo "    # Swagger UI at http://localhost:8000/docs"
echo ""
echo "  Frontend (React):"
echo "    cd src/web"
echo "    npm run dev"
echo "    # App will be at http://localhost:5173"
echo ""
