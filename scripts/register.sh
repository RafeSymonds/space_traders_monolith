#!/bin/bash

echo "=========================================="
echo "Space Traders - Account Registration"
echo "=========================================="
echo ""
echo "To play Space Traders, you need to register an account and get an API token."
echo ""
echo "Options:"
echo ""
echo "1. Register via the website (recommended)"
echo "   → Go to https://api.spacetraders.io/v2/docs#/Accounts/register"
echo "   → Use the 'Try it out' feature with symbol like MYBOT123 and faction COSMIC"
echo "   → Copy the 'token' from the response"
echo ""
echo "2. Use curl (in another terminal):"
echo "   curl -X POST https://api.spacetraders.io/v2/register \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"symbol\": \"YOUBOT42\", \"faction\": \"COSMIC\"}'"
echo ""
echo "3. Use the web playground:"
echo "   → https://api.spacetraders.io/v2/playground"
echo ""
echo "=========================================="
echo ""

read -p "Paste your API token here (or press Enter to skip): " TOKEN

if [ -n "$TOKEN" ]; then
    echo ""
    echo "Setting token in space_traders/.env ..."
    echo "SPACE_TRADERS_TOKEN=$TOKEN" > /Users/rafe/games/space_traders/space_traders/.env
    echo "✓ Token saved!"
    echo ""
    echo "Now run: ./scripts/run.sh local"
else
    echo ""
    echo "Skipped. You can manually create space_traders/.env with:"
    echo "  SPACE_TRADERS_TOKEN=your_token_here"
fi