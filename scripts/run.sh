#!/bin/bash

cd /Users/rafe/games/space_traders

echo "========================================"
echo "Space Traders - Full Stack Runner"
echo "========================================"
echo ""

case "$1" in
install)
    echo ">>> Installing dependencies..."
    cd space_traders && ./bin/install && cd ..
    cd ui && npm install && cd ..
    echo ">>> Done! Run './scripts/run.sh local' or './scripts/run.sh lan'"
    ;;

local)
    echo ">>> Starting backend (localhost only)..."
    cd space_traders && ./bin/run local &
    BACKEND_PID=$!
    sleep 3
    
    echo ">>> Starting frontend dev server..."
    cd ui && npm run dev &
    FRONTEND_PID=$!
    
    echo ""
    echo "========================================"
    echo "Servers running:"
    echo "  Backend: http://localhost:8000"
    echo "  Frontend: http://localhost:5173"
    echo ""
    echo "Press Ctrl+C to stop both servers"
    echo "========================================"
    
    wait
    ;;

lan)
    echo ">>> Starting backend (LAN accessible)..."
    cd space_traders && ./bin/run lan &
    BACKEND_PID=$!
    sleep 3
    
    echo ">>> Starting frontend dev server..."
    cd ui && npm run dev -- --host 0.0.0.0 &
    FRONTEND_PID=$!
    
    echo ""
    echo "========================================"
    echo "Servers running:"
    echo "  Backend: http://0.0.0.0:8000"
    echo "  Frontend: http://0.0.0.0:5173"
    echo ""
    echo "Press Ctrl+C to stop both servers"
    echo "========================================"
    
    wait
    ;;

test)
    echo ">>> Running backend tests..."
    cd space_traders && ./bin/test
    ;;

build)
    echo ">>> Building UI..."
    cd ui && npm run build
    echo ">>> Build complete! Output in ui/dist/"
    ;;

stop)
    echo ">>> Stopping all servers..."
    pkill -f "fastapi dev" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    echo ">>> Done"
    ;;

status)
    echo ">>> Checking server status..."
    if curl -s http://localhost:8000/api/v1/fleet/agent > /dev/null 2>&1; then
        echo "  Backend: RUNNING"
    else
        echo "  Backend: STOPPED"
    fi
    
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo "  Frontend: RUNNING"
    else
        echo "  Frontend: STOPPED"
    fi
    ;;

*)
    echo "Usage: $0 {install|local|lan|test|build|stop|status}"
    echo ""
    echo "Commands:"
    echo "  install  - Install all dependencies"
    echo "  local    - Start both servers (localhost only)"
    echo "  lan      - Start both servers (LAN accessible)"
    echo "  test     - Run backend tests"
    echo "  build    - Build UI for production"
    echo "  stop     - Stop all running servers"
    echo "  status   - Check if servers are running"
    exit 1
    ;;
esac