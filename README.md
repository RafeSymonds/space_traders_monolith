# Space Traders

Client for the [SpaceTraders](https://spacetraders.io) API. Go backend, React frontend.

## Quick start

```bash
cp .env.example .env   # fill in tokens
make install
make dev               # http://localhost:5173
```

See `AGENTS.md` for the game reference, project layout and all `make` targets.

## Spec

`openapi.json` is the SpaceTraders OpenAPI 3.0.1 spec, v2.3.0. Refresh it with:

```bash
curl -sSL https://api.spacetraders.io/v2/documentation/json -o openapi.json
```

## Auth

1. Create an account at https://my.spacetraders.io and generate an account token.
2. `POST /register` with the account token to create an agent. The response contains an agent token.
3. Use the agent token for every other call.

The server resets weekly (`GET /v2/` returns `serverResets.next`). A reset invalidates agent tokens, so re-register after each one.

Copy `.env.example` to `.env` and fill in the tokens.
