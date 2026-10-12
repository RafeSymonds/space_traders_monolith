<!-- Mirrored from https://docs.spacetraders.io/quickstart/last-steps -->

# Last Steps

When you've mined a full cargo hold of the ores in your contract, you can send your ship to the delivery waypoint to deliver goods on the contract. Once the terms of the contract are complete, you can submit it to receive the full payment.

## Navigate to delivery waypoint

With a full cargo hold and a full tank, you can navigate your ship to the delivery waypoint. You can send a POST request to the `my/ships/:shipSymbol/navigate` endpoint to navigate your ship to a waypoint.

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:miningShipSymbol/navigate' \
  -H 'Authorization: Bearer $AGENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"waypointSymbol":":deliveryWaypointSymbol"}'
```

## Deliver contract goods

Once your ship arrives, send a POST request to the `my/contracts/:contractId/deliver` endpoint. You will need to specify the ship you are delivering with, along with the type of good you are delivering, and the number of units.

This request will only succeed if your ship is at the delivery waypoint, and your cargo hold contains the required goods.

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/contracts/:contractId/deliver' \
  -H 'Authorization: Bearer $AGENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"shipSymbol":":miningShipSymbol","tradeSymbol":"COPPER_ORE","units":100}'
```

## Fulfill contract

You will need to continue to mine ores and ship them to the delivery waypoint until the contract is complete.

Once the terms have been met, you can send a request to the following endpoint to receive the full payment.

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/contracts/:contractId/fulfill' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```
