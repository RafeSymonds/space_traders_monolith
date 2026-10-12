<!-- Mirrored from https://docs.spacetraders.io/game-concepts/outfitting -->

# Outfitting

Ship in spacetraders consist of several different components:

- **Frame**: The frame that makes up the bulk of your ship. Determines the number of module and mount slots, as well as base fuel storage.
- **Reactor**: The reactor that powers your ship. Determines how much power your modules and mounts can consume.
- **Engine**: The engine that propels your ship. Determines speed.
- **Modules**: Things that you keep on the inside of your ship
- **Mounts**: Things that you hang on the outside of your ship

When you purchase a ship, the frame, reactor and engine cannot be taken out or swapped, but the modules and mounts are completely up to you to fill in. There are endpoints to [install mounts](https://spacetraders.io/openapi#tag/fleet/POST/my/ships/%7BshipSymbol%7D/mounts/install), and [modules](https://spacetraders.io/openapi#tag/fleet/POST/my/ships/%7BshipSymbol%7D/modules/install), as well as remove them.

All frames, reactors, engines, mounts and modules have requirements in terms of power and crew. If the combined requirement of your power and crew are lower than the combined values provided by your components, your ship is valid, and you can switch mounts and modules to your hearts content.

Note that to switch out a mount or module, you need to have it available in the cargo hold of the ship doing the switching. We may simplify this in the future when you are docked at a shipyard that sells mounts or modules.

**Future**: Increasing your reputation with a faction will unlock more modules and mounts for purchase. Base modules and mounts will get modifies based on what faction sold them.
