# Space Traders Fleet Management System

A self-evolving fleet management system with FastAPI backend and React frontend.

## Quick Start

```bash
# First time setup
./scripts/run.sh install

# Run everything (local)
./scripts/run.sh local

# Run everything (LAN accessible)
./scripts/run.sh lan

# Run tests
./scripts/run.sh test

# Check status
./scripts/status.sh

# Stop servers
./scripts/run.sh stop

# Build UI for production
./scripts/run.sh build
```

## Project Structure

```
space_traders/
├── space_traders/     # Python FastAPI backend
│   ├── app/
│   │   ├── api/       # FastAPI routes
│   │   ├── core/      # Config, fleet manager
│   │   └── operations/# Bots (mining, trading, etc)
│   ├── space_traders_api/  # Generated OpenAPI client
│   ├── tests/         # Unit tests (82 passing)
│   └── bin/           # Backend scripts
│
├── ui/                # React TypeScript frontend
│   ├── src/
│   │   ├── api/       # Generated TypeScript client
│   │   ├── App.tsx    # Dashboard
│   │   └── index.css   # Dark theme styling
│   └── dist/          # Production build
│
└── scripts/           # Top-level helpers
    ├── run.sh         # Main runner (local/lan/test/build/stop)
    └── status.sh      # Quick status check
```

## Features

### Backend Operations
- **MiningBot** - Extract resources, survey deposits
- **TradingBot** - Find arbitrage opportunities
- **ExplorationBot** - Scan systems and waypoints
- **MarketScanner** - Scan markets, track prices, find trade routes
- **RefineryBot** - Convert ore to metals, produce fuel
- **FuelManager** - Auto-refuel ships
- **ShipPurchaser** - Auto-buy new ships
- **ContractCoordinator** - Accept and fulfill contracts
- **FleetBrain** - Orchestrates all bots in automated cycles

### Fleet Brain Automation
Run cycles to let the fleet:
1. Mine resources
2. Refine ore into metals/fuel
3. Trade for profit
4. Accept and fulfill contracts
5. Auto-expand (buy new ships)
6. Scan markets for opportunities

### API Endpoints
- `GET /api/v1/fleet/` - List all ships
- `GET /api/v1/fleet/agent` - Agent info
- `GET /api/v1/fleet/contracts` - List contracts
- `POST /api/v1/fleet/{ship}/dock` - Dock ship
- `POST /api/v1/fleet/{ship}/orbit` - Orbit waypoint
- `POST /api/v1/fleet/{ship}/extract` - Extract resources
- `POST /api/v1/fleet/{ship}/navigate` - Navigate to waypoint
- `GET /api/v1/automation/brain/status` - Fleet brain status
- `POST /api/v1/automation/brain/start` - Start automation
- `POST /api/v1/automation/brain/cycle` - Run one cycle
- `GET /api/v1/automation/trading/opportunities` - Trade routes
- `GET /api/v1/automation/systems/waypoints` - Waypoints in system

## Environment Variables

```bash
# Required for real API access
SPACE_TRADERS_TOKEN=your_token_here

# Optional - defaults shown
SPACE_TRADERS_API_URL=https://api.spacetraders.io/v2
```

Create `space_traders/.env` with your token to use real API.

## Development

```bash
# Backend only
cd space_traders
./bin/run local   # Start backend

# Frontend only
cd ui
npm run dev       # Start dev server

# Run tests
cd space_traders && ./bin/test
```

## Architecture

```
User → React UI → FastAPI → Space Traders API
         ↑           ↓
         ←─────── Bots ───────←
         mining, trading, exploration, etc
```