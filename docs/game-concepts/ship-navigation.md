<!-- Mirrored from https://docs.spacetraders.io/game-concepts/ship-navigation -->

# Ship Navigation

## Overview

Ships can navigate between waypoints within a system and jump or warp between systems across the SpaceTraders universe. Ships can also dock at waypoints to refuel, repair, and trade goods.

Movement in the SpaceTraders universe is based on a grid system. Ships can only move from and to other waypoints within the same system. To move between systems, you must either jump or warp your ship.

When traveling to a new waypoint or system, your ship nav's `arrival` timestamp will be updated to reflect when your ship will arrive at it's destination.

## Orbiting and docking

Before a ship can travel, you must first confirm that the ship is undocked and in-orbit. You can call the following endpoint to confirm your ship is in orbit, or command it to move into orbit:

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/orbit' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

Conversely, you can call the following endpoint to dock your ship at a waypoint:

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/dock' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

The orbit and dock requests are idempotent, meaning you can call them successively and the result will be the same. This is useful if you want to ensure your ship is in orbit before you attempt to travel to another waypoint.

## Flight mode

Your ship's flight mode determines the rate at which it travels and the amount of fuel consumed. There are four flight modes:

- **CRUISE** - Cruise flight mode is the default mode for all ships. It consumes fuel at a normal rate and travels at a normal speed.
- **BURN** - Burn flight mode consumes fuel at a faster rate and travels at a faster speed.
- **DRIFT** - Drift flight mode consumes the least fuel and travels at a much slower speed. Drift mode is useful when your ship has run out of fuel and you need to conserve what little fuel you have left.
- **STEALTH** - Stealth flight mode runs with systems at a minimum, making it difficult to detect. It consumes fuel at a normal rate but travels at a reduced speed.

To update your ship's flight mode, you can call the following endpoint:

```bash
curl -X PATCH 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/nav' \
  -H 'Authorization: Bearer $AGENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"flightMode":"CRUISE"}'
```

## Waypoint navigation

When navigating, a ship will move to the destination, but it will not arrive immediately. Instead, it will take time to travel to the destination, and you can use the navigation status to determine when the ship will arrive.

Navigation also consumes fuel, which is required to power the ship's engines. The amount of fuel consumed is based on the distance between the current location and the destination.

To navigate your ship to a waypoint, you can call the following endpoint:

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/navigate' \
  -H 'Authorization: Bearer $AGENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"waypointSymbol":":waypointSymbol"}'
```

## Warping

When moving between systems, whether the ship can warp is dependent on whether the ship has a warp drive installed. Warping your ship moves it into interdimensional space, and it behaves very similar to normal waypoint travel in that it takes time and consumes normal fuel.

To warp your ship to a new system, you can call the following endpoint:

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/warp' \
  -H 'Authorization: Bearer $AGENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"systemSymbol":":systemSymbol"}'
```

## Jump gate travel

If your ship isn't equipped with a warp drive, you can still travel between systems by using faction gates. Gates are special waypoints that allow you to travel between systems.

Jumping a ship is instantaneous, but afterwards there is a jump cooldown that means you cannot jump again right away.

Jumping consumes a unit of antimatter, which, when jumping from a Jump Gate is automatically purchased and used at the gate's going rate (inspect the market at the gate to find out how much it costs).

To jump your ship to a new system, you can call the following endpoint:

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/jump' \
  -H 'Authorization: Bearer $AGENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"systemSymbol":":systemSymbol"}'
```

**Future** Some faction gates are restricted based on your agent's reputation with the faction. To unlock access to new systems, you can increase your reputation with the faction by completing contracts for them.

## Refueling

Ships can be refueled at any waypoint with a marketplace that offers fuel for sell. One unit of fuel at the marketplace replenishes 100 units in the ship's tank. Often fuel prices can be driven high by demand, so it's best to refuel your ship when fuel prices are low or to help drive prices down by selling fuel at high-traffic marketplaces.

You can also refuel your ship from it's cargo hold by sending a POST request to the [`my/ships/:shipSymbol/refuel`](http://localhost:3000/openapi#tag/fleet/POST/my/ships/%7BshipSymbol%7D/refuel) endpoint with a `fromCargo` value of `true`.

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/refuel' \
  -H 'Authorization: Bearer $AGENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"fromCargo":"true"}'
```
