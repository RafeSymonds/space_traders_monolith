#!/bin/bash

echo "========================================"
echo "Space Traders - Quick Status Check"
echo "========================================"
echo ""

echo "1. Checking backend environment..."
if [ -d "space_traders/env" ]; then
    echo "   ✓ Python virtual env exists"
else
    echo "   ✗ Run './run.sh install' first"
fi

if grep -q "SPACE_TRADERS_TOKEN" space_traders/.env 2>/dev/null; then
    echo "   ✓ API token configured"
else
    echo "   ⚠ No API token found (will use dummy for testing)"
fi

echo ""
echo "2. Checking frontend environment..."
if [ -d "ui/node_modules" ]; then
    echo "   ✓ node_modules exists"
else
    echo "   ✗ Run './run.sh install' first"
fi

echo ""
echo "3. Checking generated API clients..."
if [ -d "space_traders/space_traders_api" ]; then
    echo "   ✓ Python API client exists"
else
    echo "   ✗ Run './run.sh install' first"
fi

if [ -d "ui/src/api" ]; then
    echo "   ✓ TypeScript API client exists"
else
    echo "   ✗ Run './run.sh install' first"
fi

echo ""
echo "4. Server status..."
if curl -s --max-time 2 http://localhost:8000/api/v1/fleet/agent > /dev/null 2>&1; then
    echo "   ✓ Backend running at http://localhost:8000"
else
    echo "   - Backend not running"
fi

if curl -s --max-time 2 http://localhost:5173 > /dev/null 2>&1; then
    echo "   ✓ Frontend running at http://localhost:5173"
else
    echo "   - Frontend not running"
fi

echo ""
echo "========================================"
echo "Quick Commands:"
echo "  ./run.sh install  - Install everything"
echo "  ./run.sh local    - Start servers (local)"
echo "  ./run.sh test     - Run tests"
echo "  ./run.sh status   - Check this again"
echo "========================================"