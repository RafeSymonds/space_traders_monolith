# Space Traders Fleet Automation - Design Doc

## Goal
Build a fully autonomous system that:
1. Mines resources efficiently
2. Trades for profit
3. Expands the fleet automatically
4. Maximizes credits with minimal human intervention

---

## Current State

**Assets:**
- 2 ships (need role assignment + navigation)
- 175,000 credits
- Agent in system X1-V16

**Infrastructure:**
- `FleetBrain` - runs every 30 seconds
- `MarketScanner` - scans markets for trade routes
- `MiningBot` - extracts resources
- `TradingBot` - finds arbitrage opportunities
- `FleetExpansionManager` - buys new ships

---

## Key Constraint: Market Visibility

**IMPORTANT:** Market data (prices, supply, trade goods) is only visible when a ship is physically present at the waypoint. This has major implications:

```
CAN SEE:                              CANNOT SEE:
- Prices at current location           - Prices at distant markets
- Local supply/demand                  - System-wide trade routes without traveling
- Available trade goods               - Best routes without exploration
```

**Implication:** We must strategically position ships to "discover" market data. This is a fog-of-war model.

**Solution Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                    Market Knowledge Graph                    │
├─────────────────────────────────────────────────────────────┤
│  KNOWN MARKETS (ship visited)     UNKNOWN MARKETS           │
│  ┌────────────────────────┐       ┌───────────────────┐    │
│  │ X1-V16-A: prices,       │       │ X1-V18-B: ???     │    │
│  │       supply, trades    │       │ X1-DF-55-C: ???   │    │
│  └────────────────────────┘       └───────────────────┘    │
│                                                              │
│  Waypoints marked as "MARKETPLACE" but no ship data =       │
│  must send ship there to scan                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FleetBrain                             │
│                   (runs every 30s)                          │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│   MINING    │   TRADING    │ EXPLORATION │    EXPANSION     │
│   CYCLE     │   CYCLE      │   CYCLE     │     CYCLE        │
├─────────────┴─────────────┴─────────────┴──────────────────┤
│                    Navigation Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ JumpGateNav │  │ WaypointDB  │  │ ShipRouter  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    Market Knowledge Layer                    │
│  ┌─────────────────────────────────────────────────┐       │
│  │ WaypointRegistry: All known waypoints + types   │       │
│  │ MarketDB: Price data (only at visited waypoints) │       │
│  │ TradeRoutes: Profitable paths we've discovered  │       │
│  └─────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Ship Positioning (Priority: HIGH)

**Problem:** Ships don't go anywhere.

**Solution:**
1. Build `WaypointRegistry` - caches all waypoints in a system
2. Add `ship_state` to track: `IDLE`, `TRAVELING`, `MINING`, `TRADING`, `REFINING`
3. Create `NavigateToWaypoint(ship, waypoint)` action
4. Auto-navigate ships to appropriate locations each cycle

**Ship Assignment Logic:**
```
MINING ships → Asteroid fields (type: ASTEROID_FIELD)
TRADING ships → Marketplace waypoints
REFINING ships → Shipyards with refinery modules
EXPLORATION ships → Unvisited systems
```

**Implementation:**
```python
class ShipState(Enum):
    IDLE = "idle"
    TRAVELING = "traveling"
    MINING = "mining"
    TRADING = "trading"
    REFINING = "refining"

def navigate_to_waypoint(ship, target_waypoint):
    # Check if warp drive available
    # If in same system: warp to waypoint
    # If different system: jump or navigate via gate
    # Update ship_state to TRAVELING
    pass

def ensure_ship_at_location(ship, waypoint_type):
    # Check current waypoint type
    # If wrong type, find nearest waypoint of correct type
    # Navigate there
    pass
```

---

## Phase 2: Market Discovery (Priority: HIGH)

**Problem:** We can only see market data at waypoints where we have ships.

**Solution:**
1. Systematically send ships to explore marketplace waypoints
2. When ship visits waypoint, pull market data immediately
3. Cache discovered data in `MarketDB`
4. Track which waypoints have been "scanned"

**Market Data Storage:**
```python
@dataclass
class MarketSnapshot:
    waypoint: str           # X1-V16-A
    system: str             # X1-V16
    discovered_at: datetime # When we got this data
    discovered_by: str      # Which ship scanned it
    
    # Only populated if ship was present:
    exports: list[str]      # What this system exports
    imports: list[str]      # What it imports
    exchange: list[str]     # What's traded here
    
    goods: list[MarketGoods] # Only visible at this waypoint!
    
    # Reliability:
    data_age_seconds: int   # How stale is this?
    is_stale: bool          # True if > 5 minutes old

@dataclass
class MarketGoods:
    symbol: str             # e.g., "IRON_ORE"
    name: str               # "Iron Ore"
    purchase_price: int      # 0 if not available
    sell_price: int          # 0 if not available
    supply: str             # SCARCE, LIMITED, MODERATE, ABUNDANT
    trade_volume: int       # Units traded recently
    activity: str           # WEAK, GROWING, STRONG
```

**Staleness Rules:**
- Market data older than 5 minutes is "stale"
- Stale data is still useful for trends but prices may be wrong
- Must send ship back to refresh if we want accurate prices

**Exploration Priority:**
```
1. Nearby systems (same jump gate distance)
2. Waypoints with MARKETPLACE trait we haven't visited
3. High-trade-volume routes other players use
```

---

## Phase 3: Mining Operations (Priority: HIGH)

**Problem:** Mining ships don't know where to mine.

**Solution:**
1. Scan current system for `ASTEROID_FIELD` waypoints
2. Cache mining locations in `MiningSite` registry
3. Each cycle: assign idle mining ships to sites
4. Execute: Dock → Extract → Loop

**Mining Flow:**
```
FOR each MINING ship:
    IF ship.is_busy OR ship.state != MINING:
        CONTINUE
    
    IF not at_asteroid_field:
        find_nearest_asteroid()
        navigate_to(ship, asteroid)
        mark ship TRAVELING
        CONTINUE
    
    # At asteroid - start mining
    dock_ship(ship)
    WHILE cargo_not_full:
        extract_resources(ship)
        wait_cooldown()
    
    mark ship IDLE (cargo full)
```

---

## Phase 4: Trading Operations (Priority: HIGH)

**Problem:** We find opportunities but don't execute trades.

**Important:** We can only trade goods we have in cargo. Mining produces goods that trading ships then sell.

**Solution:**
1. Keep `MarketScanner` for finding routes (but only for KNOWN markets)
2. Add `TradeExecutor` that actually does buy/sell
3. Each cycle: find best route, execute if ship has capacity

**Trade Execution Flow:**
```
FOR each TRADING ship:
    IF cargo_available < minimum_trade_size:
        CONTINUE
    
    opportunity = find_best_trade_opportunity()  # Uses known markets only!
    IF opportunity IS None:
        CONTINUE
    
    # Navigate to buy location (if not already there)
    IF not at(buy_location):
        navigate_to(ship, opportunity.buy_location)
        mark TRAVELING, CONTINUE
    
    # At buy location - check if we have market data
    IF not have_market_data(buy_location):
        scan_market()  # This is where we discover prices!
    
    dock(ship)
    purchase_cargo(ship, opportunity.good, max_affordable)
    
    # Navigate to sell location  
    navigate_to(ship, opportunity.sell_location)
    
    # At sell location - check market data
    IF not have_market_data(sell_location):
        scan_market()
    
    dock(ship)
    sell_cargo(ship, opportunity.good)
    
    record_profit()
```

---

## Phase 5: Fleet Expansion (Priority: MEDIUM)

**Already Implemented:** `FleetExpansionManager`

**Enhancements Needed:**
- Only expand when credits > 2x ship price (safety)
- Target fleet composition: 40% Mining, 30% Trading, 20% Exploration, 10% Support
- Auto-assign roles to new ships based on purchase ship type
- Use expansion to scout NEW systems for market discovery

---

## Data Structures

```python
@dataclass
class Waypoint:
    symbol: str              # X1-V16-A
    type: WaypointType       # ASTEROID_FIELD, MARKETPLACE, SHIPYARD, etc.
    system: str              # X1-V16
    x: int
    y: int
    traits: list[str]
    has_been_visited: bool   # Have we been here?
    market_data: MarketSnapshot | None  # Only if ship visited!

@dataclass
class MiningSite:
    waypoint: str            # X1-V16-A (asteroid field)
    system: str              # X1-V16
    good: str                # What to mine (IRON_ORE, etc.)
    last_scanned: datetime
    times_mined: int

@dataclass
class TradeRoute:
    buy_waypoint: str         # Where to buy
    sell_waypoint: str       # Where to sell
    good: str                 # What to trade
    profit_per_unit: int
    volume: int
    
    # Only usable if BOTH markets are known!
    buy_market_known: bool    # Do we have price data?
    sell_market_known: bool  # Do we have price data?
    
    # Tracking
    times_used: int
    success_rate: float
    last_profit: int

@dataclass
class FleetComposition:
    mining_ships: int = 0
    trading_ships: int = 0
    exploration_ships: int = 0
    support_ships: int = 0
```

---

## Implementation Order

1. **WaypointRegistry** - Know where everything is
2. **Auto-navigation** - Ships go places
3. **Market Discovery** - Send ships to marketplaces to discover prices
4. **Mining loop** - Extract resources
5. **Trade execution** - Make actual profits (using known markets)
6. **Expansion loop** - Buy more ships
7. **Profit tracking** - Monitor success

---

## Market Discovery Strategy

Since market data requires physical presence, we need a systematic approach:

```
Priority 1: Same-system exploration
  - Send ships to ALL marketplace waypoints in current system
  - Build complete price map of X1-V16
  
Priority 2: Adjacent system scouting
  - Use JumpGateNavigator to visit neighboring systems
  - Each new system = new market discovery
  
Priority 3: Trade route refinement
  - Once we know 2 markets, we can trade between them
  - Re-scan markets periodically to get fresh prices
```

**Exploration Ship Assignment:**
- Exploration ships should prioritize UNVISITED marketplace waypoints
- When arriving at new waypoint: ALWAYS scan market before leaving
- This builds our knowledge graph over time

---

## API Endpoints to Add/Fix

| Endpoint | Purpose |
|----------|---------|
| `GET /systems/{symbol}/waypoints` | Populate waypoint cache |
| `GET /mining/sites` | List known mining locations |
| `GET /markets/known` | List waypoints with discovered market data |
| `GET /markets/unknown` | List marketplace waypoints we haven't visited |
| `POST /ship/{symbol}/explore-market` | Go to marketplace and scan |
| `POST /ship/{symbol}/mine` | Start mining at current location |
| `POST /ship/{symbol}/trade` | Execute best trade route |
| `GET /routes` | List active trade routes |
| `GET /fleet/composition` | Current fleet by role |
| `POST /ship/{symbol}/go-to` | Navigate to specific waypoint |

---

## Success Metrics

1. **Market Coverage** - % of marketplace waypoints we've scanned
2. **Profit per cycle** - Credits earned minus credits spent
3. **Fleet size growth** - Net ships over time
4. **Cargo utilization** - How full are our ships when trading
5. **Mining efficiency** - Resources extracted per hour

---

## Self-Improvement Ideas (Priority: LOW)

- Track which routes are most profitable → favor those
- Learn which systems have best mining → prioritize
- Adjust fleet size based on profit rate
- Save/restore state so brain survives restarts
- Predict optimal trade routes based on historical data