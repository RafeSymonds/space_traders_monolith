#!/bin/bash

echo "=========================================="
echo "Space Traders - Setup Wizard"
echo "=========================================="
echo ""
echo "To play Space Traders, you need an API token."
echo ""
echo "Steps:"
echo ""
echo "1. Go to https://my.spacetraders.io"
echo "2. Create a free account or sign in"
echo "3. Go to your dashboard and generate an API token"
echo "4. Copy the token and paste it below"
echo ""
echo "Alternative - Register directly via API:"
echo "  curl -X POST https://api.spacetraders.io/v2/register \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -H 'Authorization: Bearer YOUR_ACCOUNT_TOKEN' \\"
echo "    -d '{\"symbol\": \"YOUBOT42\", \"faction\": \"COSMIC\"}'"
echo ""
echo "=========================================="
echo ""

read -p "Paste your Account Token here: " TOKEN

if [ -n "$TOKEN" ]; then
    echo ""
    echo "Testing token..."
    
    # Test if it's a valid account token by trying to register
    RESULT=$(curl -s -X POST "https://api.spacetraders.io/v2/register" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"symbol": "TEMP'$(date +%s)'", "faction": "COSMIC"}')
    
    if echo "$RESULT" | grep -q "token"; then
        echo "✓ Account token valid!"
        # Extract the agent token
        AGENT_TOKEN=$(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('data',{}).get('token',''))" 2>/dev/null)
        if [ -n "$AGENT_TOKEN" ]; then
            echo "✓ Registered new agent! Token saved."
            echo "SPACE_TRADERS_TOKEN=$AGENT_TOKEN" > /Users/rafe/games/space_traders/space_traders/.env
            echo "Agent token saved to space_traders/.env"
        else
            echo "Got response but couldn't extract token:"
            echo "$RESULT" | head -3
        fi
    elif echo "$RESULT" | grep -q "already been taken"; then
        echo "✓ Account token valid! (agent symbol already exists)"
        echo "SPACE_TRADERS_TOKEN=$TOKEN" > /Users/rafe/games/space_traders/space_traders/.env
        echo "Account token saved to space_traders/.env"
    else
        echo "Token may be invalid. Response:"
        echo "$RESULT" | head -3
        echo ""
        read -p "Save anyway? (y/n): " SAVE
        if [ "$SAVE" = "y" ]; then
            echo "SPACE_TRADERS_TOKEN=$TOKEN" > /Users/rafe/games/space_traders/space_traders/.env
            echo "Saved to space_traders/.env"
        fi
    fi
else
    echo ""
    echo "No token provided."
    echo "You can manually create space_traders/.env with:"
    echo "  SPACE_TRADERS_TOKEN=your_token_here"
fi

echo ""
echo "Run './scripts/run.sh local' when ready."