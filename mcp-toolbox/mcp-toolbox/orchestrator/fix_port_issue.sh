#!/bin/bash

echo "=== Fixing Streamlit Port Issue ==="

# Kill any existing Streamlit processes
echo "1. Stopping existing Streamlit processes..."
pkill -f streamlit
pkill -f "streamlit_ui.py"

# Wait a moment for processes to stop
sleep 2

# Check if port 8508 is still in use
echo "2. Checking port 8508 status..."
if lsof -i :8508 > /dev/null 2>&1; then
    echo "Port 8508 still in use. Finding and killing process..."
    PID=$(lsof -t -i :8508)
    if [ ! -z "$PID" ]; then
        kill -9 $PID
        echo "Killed process $PID using port 8508"
    fi
else
    echo "Port 8508 is now free"
fi

# Wait another moment
sleep 1

# Start Streamlit on port 5000 (or find next available port)
echo "3. Starting Streamlit on port 5000..."
streamlit run streamlit_ui.py --server.address 0.0.0.0 --server.port 5000 --browser.gatherUsageStats false &

echo "4. Streamlit should now be running on http://0.0.0.0:5000"
echo "   Access it via: http://your-server-ip:5000"

# Show running processes
echo "5. Current Streamlit processes:"
ps aux | grep streamlit | grep -v grep