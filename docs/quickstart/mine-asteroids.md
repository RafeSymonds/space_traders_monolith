<!-- Mirrored from https://docs.spacetraders.io/quickstart/mine-asteroids -->

# Mine Asteroids

Your mining drone is equipped with a mining laser, which can be used to extract
valuable ores and minerals. You will need to navigate your ship to an asteroid
field to send an extraction request.

## Find the nearby engineered asteroid

Your starting system contains an asteroid that was moved into orbit near your
starting location. Although the asteroid as some of the others in the asteroid
belt, it is much easier to mine because it is near local markets.

```bash
curl -X GET 'https://api.spacetraders.io/v2/systems/:systemSymbol/waypoints?type=ENGINEERED_ASTEROID'
```

## Fly to the asteroid

You can navigate your new mining drone to the nearby asteroid. Drones are slow to navigate but fairly cheap, so it may take a while for your drone to arrive.

First let's make sure your ship is in-orbit, and then we will navigate to our target waypoint.

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:miningShipSymbol/orbit' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

Now that your ship is in-orbit, we can navigate to the asteroid. You can navigate to a waypoint by sending the following request:

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:miningShipSymbol/navigate' \
  -H 'Authorization: Bearer $AGENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"waypointSymbol":":asteroidWaypointSymbol"}'
```

Your ship navigation status should now be `IN_TRANSIT` and your route will show you the timestamp of your ship's arrival.

While your ship is in transit, most other requests for that ship will return an error code. Try sending the navigation request again to see the response for a ship in transit error code.

## Dock your ship

When your ship arrives at the target waypoint, we will want to refuel the ship before extracting any ores. You can dock your ship at a waypoint by sending the following request:

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:miningShipSymbol/dock' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

## Refuel your ship

Fuel is consumed when traveling between waypoints and warping between systems. When your ship arrives at the target waypoint, you can refuel your ship by sending the following request:

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:miningShipSymbol/refuel' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

Refuel requests will only succeed if the current location has fuel offered for sale at the marketplace. One unit of fuel at the marketplace replenishes 100 units in the ship's tank. If you try to refuel at a location that doesn't have fuel, you will receive an error code.

Before we can extract any ores, we will need to orbit the asteroid. You can orbit a waypoint by sending the following request:

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:miningShipSymbol/orbit' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

## Extract ores and minerals

Your mining drone is equipped with a mining laser, which can be used to extract ores and minerals from an asteroid. You can extract ores by sending a POST request to the `extract` endpoint.

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:miningShipSymbol/extract' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

After extraction, your ship will be on a cooldown and you won't be able to extract again until the cooldown expires. Try sending another extract request to see the response for a cooldown error code.

### Optional: Yeet the non-contract cargo

If you want to fill up on only contract ores, you can jettison the non-contract cargo by sending a POST request to the `jettison` endpoint.

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:miningShipSymbol/jettison' \
  -H 'Authorization: Bearer $AGENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"symbol":":cargoSymbol","units":1}'
```

To find out what cargo you have on board, you can send a GET request to the `my/ships/:miningShipSymbol/cargo` endpoint.

```bash
curl -X GET 'https://api.spacetraders.io/v2/my/ships/:miningShipSymbol/cargo' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```
