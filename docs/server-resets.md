<!-- Mirrored from https://docs.spacetraders.io/server-resets -->

# Server Resets

Server resets are a normal part of the SpaceTraders game during the alpha release, and very likely after. Each reset provides players an opportunity to start fresh and improve their code and strategies.

The game currently resets every 7 or 14 calendar days. The reset day changes depending on when the last reset was initiated, but we aim to keep it in the weekend, at 10pm JST (because that's when I'm free to resolve any issues). The exact time of the reset is announced in the status endpoint,
under the `serverResets` field.

```bash
curl -X GET 'https://api.spacetraders.io/v2/'
```

When the game resets, all players' agents are wiped and all game data is reset. This includes all systems, ships and cargo. Players will need to re-register their agents and start over from scratch, the final status of your previous agent is saved under your account, but you'll have to make a new agent for the next reset (either through the [account dashboard](https://my.spacetraders.io/) or the [register](https://api.spacetraders.io/v2/register) endpoint).

In the future, we aim to have different servers with varied reset intervals, or seasonal gameplay with different rulesets. For now, there is only one server and one reset schedule because the playerbase is limited. The most likely next addition will be a development instance, to test changes on before they make their way to the main server.
