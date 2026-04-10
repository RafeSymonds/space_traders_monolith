# Space Traders Fleet Building Master Plan

## Overview
Build the most powerful Space Traders fleet through systematic fleet expansion and optimization.

## Phases

### Phase 1: Foundation
- Register new agent with a good faction (COSMIC recommended)
- Starting assets: 1 Command Frigate + 1 Probe + 175,000 credits + 1 contract
- Complete initial contracts to build capital

### Phase 2: Economic Engine
- Purchase Heavy Freighter (~50-100k credits) for cargo transport
- Find marketplace waypoints for trade routes
- Monitor supply levels (SCARCE = high value, ABUNDANT = cheap)

### Phase 3: Specialized Fleet
| Role | Ship | Key Equipment |
|------|------|---------------|
| Mining | ORE_HOUND or HEAVY_FREIGHTER | Mining Laser II/III + Ore Refinery |
| Gas Siphoning | SIPHON_DRONE | Gas Siphon II/III + Gas Processor |
| Exploration | EXPLORER | Jump Drive III + Warp Drive III + Sensor Array III |
| Combat | INTERCEPTOR | Laser Cannon + Missile Launcher + Turret |
| Trading | BULK_FREIGHTER | Cargo Hold III modules |

### Phase 4: Power Upgrades
- Best Reactors: ANTIMATTER_I
- Best Engines: HYPER_DRIVE_I
- Combat Modules: Shield Generator II

### Phase 5: Fleet Command
- Carrier ship as mobile base
- Command Frigate as headquarters
- Fleet coordination via cargo transfer

## Key API Endpoints

### Ship Acquisition
- `POST /register` - New agent
- `POST /my/ships` - Purchase ship

### Fleet Management
- `GET /my/ships` - List fleet
- `GET /my/ships/{symbol}` - Ship details
- `POST /my/ships/{symbol}/navigate` - Move
- `POST /my/ships/{symbol}/dock` - Dock
- `POST /my/ships/{symbol}/orbit` - Orbit
- `POST /my/ships/{symbol}/jump` - Jump systems
- `POST /my/ships/{symbol}/warp` - Warp systems

### Operations
- `POST /my/ships/{symbol}/extract` - Mine
- `POST /my/ships/{symbol}/siphon` - Gas harvest
- `POST /my/ships/{symbol}/survey` - Survey deposits
- `POST /my/ships/{symbol}/refine` - Process ore
- `POST /my/ships/{symbol}/purchase` - Buy cargo
- `POST /my/ships/{symbol}/sell` - Sell cargo
- `POST /my/ships/{symbol}/transfer` - Transfer cargo

### Upgrades
- `POST /my/ships/{symbol}/modules/install`
- `POST /my/ships/{symbol}/mounts/install`
- `POST /my/ships/{symbol}/repair`

### Info
- `GET /systems/{symbol}/waypoints/{symbol}/shipyard` - Available ships
- `GET /systems/{symbol}/waypoints/{symbol}/market` - Market prices
- `GET /my/contracts` - Active contracts
