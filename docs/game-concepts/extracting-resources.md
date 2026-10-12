<!-- Mirrored from https://docs.spacetraders.io/game-concepts/extracting-resources -->

# Extracting Resources

## Overview

Ships can extract resources from asteroids and other celestial bodies. The amount of resources extracted is based on the ship's mounts and modules, such as mining lasers and mineral processing bays.

Typically yields from an extraction will be a random quantity of those available based on the traits of the location. However, if you have a surveying mount installed, you can survey the location and find more targeted locations to extract from, which will yield more of the resource you are looking for.

## Extracting resources

You can extract resources from an asteroid by calling the following endpoint. You'll need an extractor mount installed on the ship. After an extraction, your ship will be on a cooldown. You can still navigate while on a cooldown, but you cannot perform most other ship actions.

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/extract' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

## Siphoning resources

You can siphon from a gas giant by calling the following endpoint. Your ship will need a siphon mount and gas processor module installed.

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/siphon' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

## Surveying

You can survey a waypoint to find better spots to extract from. Surveying a waypoint will yield a list of surveys depending on the strength of your survey mount. Each of these will have a set of resources that can show up in extractions using the survey.

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/survey' \
  -H 'Authorization: Bearer $AGENT_TOKEN'
```

To use a survey result, you must call the extract endpoint with the full survey result. Surveys have a limited lifetime, so you must use the survey result before it expires. Surveys also have a limited deposit size, and will eventually be depleted, which will manifest as an error response to your extract call.

```bash
curl -X POST 'https://api.spacetraders.io/v2/my/ships/:shipSymbol/extract' \
  -H 'Authorization: Bearer $AGENT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"survey":":survey"}'
```
