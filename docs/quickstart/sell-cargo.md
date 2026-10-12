<!-- Mirrored from https://docs.spacetraders.io/quickstart/sell-cargo -->

# Sell Cargo

After a few extractions, your cargo hold will likely be filled with ores and minerals that you may not need for your contract. You can sell your cargo at the nearby marketplace to unload those goods and earn some credits.

## View market data

To view the types of goods available at the market, you can send the following request. Each market has a list of imports, exports and exchange goods which can be purchased and sold at the location.

```bash
curl -X GET 'https://api.spacetraders.io/v2/systems/:systemSymbol/waypoints/:asteroidWaypointSymbol/market'
```

Since your ship is present at the location, you can see the purchase and sell prices for each good.

You can also see the estimated trade volume for each good, which is rough estimate of price stability. Larger trade volumes indicate more stable prices, while smaller trade volumes indicate more volatile prices.

## List ship cargo

You can view the cargo in your ship by sending a GET request to the `my/ships/:shipSymbol` endpoint. You will want to sell the ores and minerals in your cargo hold that don't match the contract requirements.

```bash
curl -X GET 'https://api.spacetraders.io/v2/my/ships/:miningShipSymbol/cargo' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

## Sell goods

Before you can sell your cargo at the market, you will first need to dock your ship. You can dock your ship by sending a POST request to the `my/ships/:shipSymbol/dock` endpoint.

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:miningShipSymbol/dock' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

You can sell your cargo at a marketplace by sending a POST request to the `my/ships/:shipSymbol/sell` endpoint. You will need to specify the type of good you want to sell, along with the number of units.

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:miningShipSymbol/sell' \
  -H 'Authorization: Bearer $AGENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"symbol":":tradeGoodSymbol","units":":units"}'
```

The response will include details about your agent, ship cargo, and the transaction. You can see the total price for the transaction in the `totalPrice` field.
