<!-- Mirrored from https://docs.spacetraders.io/quickstart/purchase-ship -->

# Purchase Ship

Shipyards allow you to purchase ships, and repair them when they get damaged. They also allow you to swap out different modules and mounts. To purchase a ship, you will need to find a waypoint with a shipyard.

## Find a shipyard

Look for a waypoint with the `SHIPYARD` trait. You can use the following endpoint to find all waypoints in your current system. Take note of the symbol for the orbital station waypoint that has a shipyard, which you can use to purchase a mining drone.

```bash
curl -X GET 'https://api.spacetraders.io/v2/systems/:systemSymbol/waypoints?traits=SHIPYARD'
```

## View available ships

To view the ships available for purchase at a shipyard, send the following request. You will notice that there is a mining drone available for purchase, which can help you fulfill your starting contract.

```bash
curl -X GET 'https://api.spacetraders.io/v2/systems/:systemSymbol/waypoints/:shipyardWaypointSymbol/shipyard'
```

> **Note: Ship Price Visibility**
>
> Several parts of the API have some fields that are hidden unless you have a ship present at the location.
>
> When starting as a new agent, a probe ship was provided for you at this location, which allows you to see the details of the ships available for purchase.

## Purchase a ship

You can purchase a new ship at a shipyard when you have a ship present at the waypoint by sending a POST request to the `my/ships` endpoint. Sending this request will deduct the cost of the ship from your credits and add the ship to your fleet.

You will need to specify the type of ship you want to purchase, along with the waypoint you are purchasing from.

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships' \
  -H 'Authorization: Bearer $AGENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"shipType":":shipType","waypointSymbol":":shipyardWaypointSymbol"}'
```
