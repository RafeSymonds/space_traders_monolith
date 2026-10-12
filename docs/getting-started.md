<!-- Mirrored from https://docs.spacetraders.io/getting-started -->

# Getting started

Learn how to use the SpaceTraders API with the resources below or join our
Discord for help and to collaborate with other developers.

- [Quickstart](quickstart/new-game.md): Test API endpoints directly in your browser with our Quickstart guide.
- [Playground](https://docs.spacetraders.io/playground): Use the playground to see your ships and inspect the network tab.
- [API Docs](../openapi.json): Interactive Open API documentation powered by Scalar.
- [Support Us](https://my.spacetraders.io/subscribe): Support us and reserve your call sign between resets.

## Overview

SpaceTraders is an open-universe space-themed game that offers a set of HTTP
endpoints to control a fleet of ships. All players operate their fleet in the same universe, and the game is currently in
alpha.

The API is fully documented using [OpenAPI](https://spacetraders.io/openapi). You can send your first request right here in your browser to check the status of the game server, or try our [Quickstart Guide](quickstart/new-game.md) to learn the basics in under five minutes.

```bash
curl -X GET 'https://api.spacetraders.io/v2/'
```

Unlike a traditional game, SpaceTraders is headless and does not have a first-party client to play the game.

Instead, you as the player are responsible for building your own client to interact with the API. This allows you to build your own UI, automate your trade routes, or just play the game from the comfort of your terminal.

We have a [Discord channel](https://discord.gg/UpEfRRjsCT) where you can share your projects, ask questions, or give feedback on what others are building.

## Gameplay

SpaceTraders is a space-themed universe where you can explore star systems, trade goods, mine
asteroids, and take on faction contracts to earn credits and reputation.

Ships are the primary vehicle for interacting with the game world. You can buy
and sell ships, navigate them between waypoints, upgrade them with new mounts, and send them on trade routes to
earn credits.

The economy of the game is simulated and significantly influenced by player
actions. Prices of goods fluctuate based on supply and demand, and players can
influence the market by buying and selling goods in different systems.

All players operate in the same universe, so you can compete with others to earn
the most credits or chart the most systems.

To learn more about the game, check out our [gameplay
concepts](game-concepts/agents-and-factions.md) guide, or try the
[quickstart](quickstart/new-game.md) to start a new game and test various API endpoints from your
browser.

The game is currently in alpha and
under active development, so we are always adding new features and content.

## Donations

We are a small self-funded team dedicated to keeping the SpaceTraders platform alive and accessible for everyone, and free for as long as we can support it.

You can donate to the project using the [dashboard](https://my.spacetraders.io/subscribe). Contributions will go directly towards maintaining server costs for the community. As we fund everything out of pocket, every donation, no matter the size, makes a big difference.

We're grateful for your support and excited to see what you build with the SpaceTraders API!

## Next steps

The SpaceTraders API is an excellent platform to learn a new programming language, test a new framework, or stretch your skills in a fun and meaningful way.

If you are new to SpaceTraders, you should try our interactive [quickstart guide](quickstart/new-game.md) which will walk you through basic API requests in just a few minutes.

If you're looking for some project inspiration, here are some ideas to get you started:

- create a script to mine asteroids and automate trade routes
- build a web or mobile app to manage your fleet of ships
- track and share market price data with other players
- generate an SDK from the OpenAPI spec and publish it
- create a Discord bot for others players to use

And finally, if you find an issue and want to report it, please open an issue on our [GitHub repository](https://github.com/SpaceTradersAPI/api-docs) or share it in our [Discord channel](https://discord.gg/UpEfRRjsCT).
