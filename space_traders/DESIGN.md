# Space Traders Fleet Automation - Design Doc

## Goal
Build a fully autonomous system that:
1. Mines resources efficiently
2. Trades for profit
3. Expands the fleet automatically
4. Maximizes credits with minimal human intervention

---

## Current State (Updated: 2026-04-11)

**Assets:**
- 2 ships:
  - `TEMP1775869657-1`: Frigate (TRADING role, 400 fuel, 40 cargo)
  - `TEMP1775869657-2`: Probe (TRANSPORT role, 0 fuel capacity, 0 cargo)
- ~176,000 credits
- Agent in system X1-V16

**Fleet Composition:**
- No MINING ships (would need to purchase from shipyard)
- No EXPLORATION ships
- No REFINERY ships

**What Works:**
- ✅ FleetBrain auto-starts and runs every 30 seconds
- ✅ Ships are refueled automatically when low
- ✅ WaypointRegistry tracks all waypoints in system
- ✅ ShipNavigator tracks ship movement states
- ✅ Market discovery cycle sends ships to marketplaces
- ✅ System scanning populates waypoint registry
- ✅ Ships auto-position to asteroid fields (mining) or marketplaces (trading)

**What's Implemented:**
- `app/operations/waypoint_registry.py` - Waypoint caching, marketplace tracking
- `app/operations/ship_navigator.py` - Ship movement state management
- `FleetBrain._run_market_discovery()` - Discovers prices at marketplaces
- `FleetBrain._position_ships()` - Auto-navigates ships to appropriate locations
- `FleetBrain._ensure_system_scanned()` - Populates waypoint registry

**What's Broken/Blocked:**
- ❌ Cannot trade (only 1 market with data - need multiple markets to find routes)
- ❌ Cannot mine (no MINING ships, no shipyard to buy them)
- ❌ Cannot expand fleet (no shipyard in X1-V16 system)
- ❌ Trading cycle only FINDS opportunities, doesn't EXECUTE trades

---

## Known Marketplaces in X1-V16

| Waypoint | Type | Trade Goods | Notes |
|----------|------|-------------|-------|
| X1-V16-A1 | PLANET | 0 | Imports FOOD, MEDICINE, CLOTHING, etc. |
| X1-V16-B6 | FUEL_STATION | 0 | Only sells FUEL |
| X1-V16-B7 | ASTEROID_BASE | 18 goods | Main trading hub - exports GOLD, SILVER, PLATINUM |
| X1-V16-FB5C | ENGINEERED_ASTEROID | 0 | Common metal deposits |

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

1. ✅ **WaypointRegistry** - Know where everything is
2. ✅ **Auto-navigation** - Ships go places
3. ✅ **Market Discovery** - Send ships to marketplaces to discover prices
4. ❌ **Mining loop** - Extract resources (no mining ships available)
5. ❌ **Trade execution** - Make actual profits (only 1 market discovered)
6. ❌ **Expansion loop** - Buy more ships (no shipyard in system)
7. 🔄 **Profit tracking** - Basic metrics in FleetBrain

---

## Next Steps to Profitability

### Short Term (Within current system):
1. **Discover more markets** - Send ships to X1-V16-A1, X1-V16-B6 to get price data
2. **Implement trade execution** - Actually buy/sell when routes are found
3. **Find/use jump gate** - Need to find another system with shipyard

### Long Term:
1. **Acquire mining ship** - Need shipyard to buy
2. **Build trade routes** - With multiple markets, can trade ore for profit
3. **Fleet expansion** - Buy more ships once shipyard found

---

## BLOCKED: No Shipyard, No Jump Gate

**Problem:** X1-V16 system has neither a shipyard nor a jump gate. Cannot buy new ships or explore.

**Impact:**
- Cannot buy MINING ships (needed for ALUMINUM_ORE contract)
- Cannot explore other systems (7000 systems exist but unreachable)
- Fleet is stuck at 2 ships indefinitely

**Options to Break Out:**
1. **Find a way to get a ship with JUMP_DRIVE** - maybe via contract reward
2. **Find hidden waypoint** - X1-V16-H53 exists but wasn't in initial scan
3. **Trade within system** - Use existing ships for in-system trading
4. **Register new account** - Might start in different system with shipyard

---

## What We CAN Do (Even Without Shipyard)

### 1. Fulfill Existing Contract
```
Contract: cmntmxxjfo4ugri6xb8a3yxdi
- Deliver 60 ALUMINUM_ORE to X1-V16-H53
- Reward: 11,151 credits (1,449 + 9,702 on fulfillment)
- Progress: 0/60 delivered
```

**Challenge:** Need a mining ship. Frigate can't mine efficiently.

### 2. In-System Trading
X1-V16 has multiple marketplaces with different goods:
- X1-V16-A1: Imports FOOD, MEDICINE, CLOTHING
- X1-V16-B7: Exports GOLD, SILVER, PLATINUM; Imports ores
- X1-V16-B6: Only sells FUEL
- X1-V16-H53: Imports IRON, INDUSTRIAL goods

With 2 ships we could potentially do buy-low-sell-high trades.

### 3. Systematic Market Discovery
X1-V16-H53 wasn't in initial waypoint scan! There may be more hidden waypoints.
- Need to send ships to H53 to discover its market data
- May find other undiscovered waypoints

---

## Next Steps to Profitability

### Short Term:
1. **Navigate to H53** - Discover its market data
2. **Try in-system trading** - Even without mining, can buy/sell
3. **Find more hidden waypoints** - Systematic exploration

### Long Term:
1. **Find shipyard** - Need to discover system with jump gate
2. **Acquire mining ship** - To fulfill contracts and mine ore
3. **Build trade routes** - Multiple markets = profitable routes

---

## Market Data Discovered

### X1-V16-B7 (ASTEROID_BASE) - Main Trading Hub
- **Exports:** GOLD, SILVER, PLATINUM
- **Imports:** GOLD_ORE, SILVER_ORE, PLATINUM_ORE, IRON_ORE, COPPER_ORE, ALUMINUM_ORE, etc.
- **Trade Goods:** ICE_WATER (buy 17/sell 13), AMMONIA_ICE (buy 42/sell 38), QUARTZ_SAND (buy 22/sell 18)

### X1-V16-A1 (PLANET)
- **Imports:** FOOD, MEDICINE, CLOTHING, EQUIPMENT, JEWELRY, CYBER_IMPLANTS
- **Trade Goods:** None visible

### X1-V16-H53 (PLANET - CONTRACT DESTINATION)
- **Exports:** IRON
- **Hidden data:** Unknown (need to visit)

---

## API Endpoints to Add/Fix

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