# SpaceTraders

SpaceTraders is a multiplayer space trading game played entirely through an HTTP API. There is no first-party game client. Players write their own code to control a fleet of ships: explore systems, mine and siphon resources, trade goods, and fulfill faction contracts for credits. All players share one universe, and the simulated economy reacts to player activity. The game is in alpha and the API is v2.3.0.

## Where to find information

- `openapi.json`: the full API spec (OpenAPI 3.0.1, v2.3.0). It is the authority for endpoints, request bodies, response schemas and enums. Refresh with `curl -sSL https://api.spacetraders.io/v2/documentation/json -o openapi.json`.
- `docs/`: a local mirror of https://docs.spacetraders.io. Request examples are rendered as `curl` commands with `$AGENT_TOKEN` or `$ACCOUNT_TOKEN`.
  - `docs/index.md`: homepage and community projects
  - `docs/getting-started.md`: game overview
  - `docs/server-resets.md`: reset schedule and what is wiped
  - `docs/roadmap.md`: planned features. Anything marked **Future** in the docs is not implemented yet.
  - `docs/funding.md`: donations and reserved call signs
  - `docs/quickstart/`: step-by-step first session: `new-game`, `first-mission`, `purchase-ship`, `mine-asteroids`, `sell-cargo`, `last-steps`
  - `docs/game-concepts/`: mechanics: `agents-and-factions`, `systems-waypoints`, `ship-navigation`, `extracting-resources`, `outfitting`, `maintenance`, `crew-morale`, `exploration`, `markets`
  - `docs/api-guide/`: `authorization`, `open-api-spec`, `rate-limits`, `response-errors`
  - `docs/resources/changelog.md`: every game change since 2023. It describes mechanics the concept pages do not cover (jump gate construction, asteroid stability, activity levels, module endpoints).
- `.env.example`: the token variables. Real tokens go in `.env`, which is git-ignored.

## Accounts, agents and tokens

- An **account** is tied to an email and is managed at https://my.spacetraders.io. It survives resets.
- An **agent** is the in-game player identity: a unique 3-14 character call sign, credits, a headquarters, a starting faction, ships and contracts.
- Two bearer tokens (JWT) exist:
  - **Account token**: generated in the dashboard under Settings. It is only used for `POST /register` to create an agent.
  - **Agent token**: returned by `POST /register` or generated in the dashboard. It is used for everything else. Every `/my/...` endpoint requires it.
- Header format is `Authorization: Bearer <token>`. Public endpoints (`/systems`, `/factions`, `/agents`, `GET /`) work without a token.
- A new agent starts with 175,000 credits, a command ship, a probe ship, and one starter contract from its faction. The command ship begins docked at the faction headquarters.

## Server resets

- The universe resets every 7 or 14 days, usually on a weekend at 10pm JST. `GET /v2/` returns `resetDate` and `serverResets.next`.
- A reset wipes all agents, ships, cargo and generated systems. Agent tokens from before the reset fail with error 4113. Register a new agent after every reset.
- Waypoint traits are static within a reset. Universe layout changes between resets.

## Universe

- Symbols are hierarchical: sector `X1`, system `X1-DF55`, waypoint `X1-DF55-A1`.
- About 8,500 systems and 200,000 waypoints. Systems have absolute galactic x, y coordinates. Waypoints have x, y relative to their system center (0, 0).
- Waypoint types: `PLANET`, `GAS_GIANT`, `MOON`, `ORBITAL_STATION`, `JUMP_GATE`, `ASTEROID_FIELD`, `ASTEROID`, `ENGINEERED_ASTEROID`, `ASTEROID_BASE`, `NEBULA`, `DEBRIS_FIELD`, `GRAVITY_WELL`, `ARTIFICIAL_GRAVITY_WELL`, `FUEL_STATION`.
- Orbitals share their parent's coordinates and carry a `parentSymbol`.
- **Traits** describe a waypoint. `MARKETPLACE` and `SHIPYARD` are the important ones. `GET /systems/{system}/waypoints` filters by `type` and `traits`.
- **Modifiers** are temporary waypoint states. `CRITICAL_LIMIT` marks an asteroid close to over-extraction.
- Most waypoints start `UNCHARTED` with hidden traits. Charting (`POST /my/ships/{ship}/chart`) reveals them to everyone and pays a one-time credit reward. A sensor array can scan uncharted waypoints without charting them.
- 19 factions (`COSMIC`, `VOID`, `GALACTIC`, `QUANTUM`, `DOMINION`, and others). The starting faction picks the starting system. Reputation is tracked per faction (`GET /my/factions`). Most reputation effects are marked Future.

## Ships

- Components: **frame** (module and mount slots, base fuel), **reactor** (power), **engine** (speed), **modules** (internal: cargo, crew, refinery, processors), **mounts** (external: mining lasers, siphons, surveyors, sensors). Frame, reactor and engine are fixed. Modules and mounts can be installed and removed at a shipyard if the part is in the ship's cargo and power, crew and slot limits are met.
- Purchasable types: `SHIP_PROBE`, `SHIP_MINING_DRONE`, `SHIP_SIPHON_DRONE`, `SHIP_INTERCEPTOR`, `SHIP_LIGHT_HAULER`, `SHIP_COMMAND_FRIGATE`, `SHIP_EXPLORER`, `SHIP_HEAVY_FREIGHTER`, `SHIP_LIGHT_SHUTTLE`, `SHIP_ORE_HOUND`, `SHIP_REFINING_FREIGHTER`, `SHIP_SURVEYOR`, `SHIP_BULK_FREIGHTER`. Buying requires one of your ships at the shipyard (`POST /my/ships`).
- Nav status is `DOCKED`, `IN_ORBIT` or `IN_TRANSIT`. Travel, extraction and siphoning require orbit. Trading, refueling, repair and outfitting require docking. Orbit and dock are idempotent.
- While `IN_TRANSIT`, most actions on that ship fail (4214). The nav `route.arrival` timestamp says when it lands.
- Many actions (extract, siphon, survey, scan, jump, refine) put the ship on a **cooldown**. A ship can still navigate during a cooldown but cannot do most other actions. `GET /my/ships/{ship}/cooldown` returns it.
- Non-GET ship requests lock the ship while they run, so mutating requests to one ship are processed one at a time.
- Drones have no crew requirement. Crewed ships get crew from crew modules. Morale effects are mostly Future.

## Travel and fuel

- **Navigate** moves within a system. Fuel cost scales with distance and flight mode.
- Flight modes: `CRUISE` (default), `BURN` (faster, more fuel), `DRIFT` (very slow, minimal fuel), `STEALTH` (reduced speed, hard to detect). Changing to a faster mode mid-flight costs extra fuel and speeds arrival. Changing to a slower mode mid-flight is rejected.
- **Warp** moves between systems with a warp drive. It takes time and fuel like navigation.
- **Jump** moves between connected jump gates instantly, costs one unit of antimatter bought from the gate's market, and triggers a cooldown scaled by distance. Gates connect only to specific other gates. Some gates are under construction and cannot be used until players supply them.
- Refuel while docked at a market that sells `FUEL`. One market unit fills 100 tank units. Ships can also refuel from fuel in their own cargo.

## Economy

- Each market lists goods as `EXPORT` (produced here, cheaper to buy), `IMPORT` (consumed here, better sell price) or `EXCHANGE` (neither produced nor consumed, priced by player supply and demand). The basic profit loop is buy at exporters and sell at importers.
- Each listing has a `supply` level (`SCARCE`, `LIMITED`, `MODERATE`, `HIGH`, `ABUNDANT`), an `activity` level (`WEAK`, `GROWING`, `STRONG`, `RESTRICTED`) and a `tradeVolume` (max units per transaction, and a volatility indicator).
- Export production depends on the market's imports being supplied. Sustained trading grows a market's volume over time.
- Prices, trade volume and transaction history are only visible while one of your ships is at the waypoint. Shipyard prices are hidden the same way. Parking probes at markets is the standard way to watch prices.
- `GET /market/supply-chain` maps which imports feed which exports.
- 145 trade goods exist (`TradeSymbol` enum in `openapi.json`), from raw ores to ship parts, antimatter and fuel.

## Resource gathering

- **Extract** (`POST /my/ships/{ship}/extract`) mines asteroids. Requires a mining laser mount. Yields are random within what the waypoint offers.
- **Survey** (requires a surveyor mount) produces surveys that bias extraction toward specific goods. Send the unmodified survey object to `POST /my/ships/{ship}/extract/survey`. Surveys are signed, expire, and their deposits deplete.
- Asteroids destabilize when over-extracted (roughly 10 extractions per minute per asteroid). This reduces yields. Resources are otherwise unlimited for now.
- **Siphon** pulls hydrocarbons and gases from gas giants. Requires a gas siphon mount and a gas processor module.
- **Refine** converts 100 raw units into 10 processed units. Requires a refinery module.
- **Jettison** dumps cargo. **Transfer** moves cargo between your ships at the same waypoint.

## Contracts

- Factions offer contracts (`PROCUREMENT`, `TRANSPORT`, `SHUTTLE`) with credits on accept and on fulfillment.
- Flow: accept, deliver goods with a ship at the delivery waypoint, then fulfill once terms are met.
- Contracts have an acceptance deadline and a fulfillment deadline. Missing the fulfillment deadline loses reputation and the advance.
- Negotiate a new contract with a ship at a waypoint where the faction is present (`POST /my/ships/{ship}/negotiate/contract`). An agent can hold at most one ongoing or offered contract at a time.

## Construction

- Some jump gates start `UNDER_CONSTRUCTION`. Players deliver required materials with `POST /systems/{system}/waypoints/{waypoint}/construction/supply`. A finished gate opens jumps to its connected systems.

## Maintenance

- Frame, reactor and engine each have a **condition** (repairable to 1) and an **integrity** (long-term wear that every repair reduces).
- Navigating and extracting can randomly degrade condition. Better ships degrade more slowly.
- Repair and scrap happen at a shipyard. A GET on the same endpoints returns a cost or value estimate. Scrapping destroys cargo.

## API behavior

- Base URL: `https://api.spacetraders.io/v2`. Responses wrap the payload in `data`. List endpoints add `meta: {total, page, limit}`.
- Pagination uses `page` (from 1) and `limit` (1 to 20, default 10).
- Rate limits: 2 requests per second, with a burst of 30 requests per 60 seconds. They apply per IP and per account. Exceeding them returns 429 with `retry-after` and `x-ratelimit-*` headers. Infrastructure can also return 429 without those headers, so back off exponentially in that case. A 502 means DDoS protection kicked in, so wait a few minutes.
- Errors return `{"error": {"code", "message", "data"}}`. Codes are grouped: 4000s general, 4100s account and token, 4200s ship, 4500s contract, 4600s market, 4700s faction, 4800s construction. `GET /error-codes` returns the complete list. `docs/api-guide/response-errors.md` lists most of them by name.
- `GET /` returns server status, version, reset dates, stats, leaderboards and announcements.
- `GET /my/agent/events` returns recent agent events. `GET /my/socket.io` is an experimental websocket that streams ship departures for a subscribed system.

## Development

- Backend: Go 1.25, standard library `net/http`. Entry point `cmd/server`. Listens on `127.0.0.1:8080` (override with `ADDR`).
- SpaceTraders client: `internal/spacetraders/client.gen.go`, generated by oapi-codegen from `openapi.json`. Do not edit it by hand. Run `make gen` after changing `openapi.json`.
- Frontend: `web/`, Vite + React 19 + TypeScript, TanStack Query for server state, Tailwind CSS v4, oxlint. The Vite dev server proxies `/api` to the Go server.
- The Makefile loads `.env` and exports it to every command.

| Command | Does |
| --- | --- |
| `make install` | Download Go modules and npm packages |
| `make dev` | Run the Go server and Vite dev server (http://localhost:5173) together |
| `make gen` | Regenerate the Go client |
| `make build` | Build `bin/server` and `web/dist` |
| `make lint` | `go vet`, `gofmt` check, oxlint |
| `make test` | `go test ./...` |
