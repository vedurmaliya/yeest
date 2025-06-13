#!/bin/bash

# yeest.xyz Development Startup Script

echo "🚀 Starting yeest.xyz development environment..."

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Creating backend/.env from template..."
    cp backend/.env.example backend/.env
    echo "📝 Please edit backend/.env with your API keys before continuing."
    echo "   Required: GROQ_API_KEY"
    echo "   Optional: NEWSAPI_KEY, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, LANGSMITH_API_KEY"
    exit 1
fi

# Check if GROQ_API_KEY is set
if ! grep -q "GROQ_API_KEY=.*[^[:space:]]" backend/.env; then
    echo "❌ GROQ_API_KEY is not set in backend/.env"
    echo "   Please get your API key from https://console.groq.com"
    exit 1
fi

echo "✅ Environment configuration looks good!"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command_exists python3; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is not installed"
    exit 1
fi

echo "✅ All dependencies are available!"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "🎉 Setup complete!"
echo ""
echo "To start the development servers:"
echo "1. Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "2. Frontend: cd frontend && npm run dev"
echo ""
echo "Or use Docker Compose: docker-compose up --build"
echo ""
echo "Access the application at: http://localhost:3000"
