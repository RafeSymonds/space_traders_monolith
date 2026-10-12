<!-- Mirrored from https://docs.spacetraders.io/game-concepts/maintenance -->

# Maintenance

> **Note: Preview Feature**
>
> This feature is a recent addition to the game and is still being tested. We
> welcome any feedback you have on this feature. Please share your thoughts in the
> feedback channel on our Discord server.

## Overview

Taking ship actions such as navigating and extracting have a chance of a
negative event occurring which degrades the condition of the frame, reactor, or
engine on a ship. Better ships will degrade at a lower rate than cheap ships.

All of the values for event frequency, repair cost, and scrap earnings are
currently ballparked, so things will be adjusted from player feedback.

## Ship Condition vs Ship Integrity

Ship components, such as the frame, reactor, and engine, have a condition and an
integrity value. The condition of a component can be repaired and is always
restored to a value of 1. The integrity of the component is the long-term wear
and cannot be repaired. The integrity of the component is reduced every time you
repair your ship.

## Negative Events

Ship actions such as navigating and extracting have a chance of a negative event
occurring which degrades the condition of the frame, reactor, or engine on a
ship. Better ships will degrade at a lower rate than cheap ships.

## Ship Repair

Repairing your ship costs credits and the cost of this repair will factor in the
type of component, the condition of the component (more damaged components are
more expensive to repair), and the price of ship parts and plating at the
market.

You can repair your ship by hitting the following endpoint at a shipyard:

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/repair' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

All of the components of your ship will be repaired to a condition of 1, and the
integrity of the components repaired will be slightly reduced.

If you want to get an estimate of the repair cost for your ship, you can send a
GET request to the following endpoint:

```bash
curl -X GET 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/repair' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

## Scrapping

Scrapping your ship will provide your agent with credits relative to the cost of
the ship, the condition of the components, the mounts and modules attached, and
the current price of ship parts and plating at the shipyard. You won't get a
great price for your mounts and modules, so you will likely want to remove
anything valuable. Cargo will be destroyed and not factored into the credits
given.

You can scrap your ship by hitting the following endpoint at a shipyard:

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/scrap' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

If you want to get an estimate of the scrap earnings for your ship, you can send
a GET request to the following endpoint:

```bash
curl -X GET 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/scrap' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```
