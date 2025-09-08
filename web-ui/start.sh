#!/bin/bash

# Start script for Task Agent Web UI

echo "Starting Task Agent Web UI..."

# Check if running as task-agent user
if [ "$USER" != "task-agent" ]; then
    echo "Warning: Not running as task-agent user. OAuth credentials may not be accessible."
fi

# Install backend dependencies if needed
if [ ! -d "backend/venv" ]; then
    echo "Setting up backend virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo "Activating backend virtual environment..."
    source backend/venv/bin/activate
fi

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start backend in background
echo "Starting backend server..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 2

# Start frontend
echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "Task Agent Web UI is running!"
echo "Frontend: http://localhost:5173"
echo "Backend: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up trap for cleanup
trap cleanup INT TERM

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID