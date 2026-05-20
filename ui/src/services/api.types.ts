export interface Agent {
  symbol: string
  headquarters: string
  credits: number
  startingFaction: string
  shipCount: number
}

export interface Ship {
  symbol: string
  role: string
  system: string | null
  waypoint: string | null
  status: string
  busy: boolean
  cargo: { used: number; capacity: number }
  last_action?: string | null
}

export interface Contract {
  id: string
  factionSymbol: string
  type: string
  terms: {
    deadline: string
    payment: { onAccepted: number; onFulfilled: number }
    deliver: Array<{ tradeSymbol: string; unitsRequired: number; unitsFulfilled: number }>
  }
  accepted: boolean
  fulfilled: boolean
}

export interface Waypoint {
  symbol: string
  type: string
  x: number
  y: number
  traits: string[]
}

export interface BrainMetrics {
  total_ships: number
  total_credits: number
  ships_mining: number
  ships_trading: number
  ships_exploring: number
  ships_refining: number
  ships_available: number
  total_cargo_units: number
  total_extracted: number
  total_trades: number
  total_profit: number
  contracts_completed: number
  ships_purchased: number
  credits_spent: number
  fuel_produced: number
  markets_scanned: number
  trades_executed: number
  best_trade_profit: number
  market_condition: string
  active_traders: number
}

export interface TradeOpportunity {
  buy_location: string
  sell_location: string
  trade_good: string
  profit_per_unit: number
  volume: number
  total_profit: number
  efficiency: number
}

export interface MultiHopRoute {
  stops: string[]
  goods: string[]
  total_profit: number
  estimated_time_minutes: number
  legs: Array<{ from: string; to: string; good: string; profit: number }>
}

export interface RoleOptimization {
  total_assignments: number
  market_condition: string
  mining_score: number
  trading_score: number
  recent_assignments: Array<{
    ship: string
    from: string
    to: string
    reason: string
    timestamp: string
  }>
}

export interface ProfitHistory {
  total_profit: number
  trades: Array<{
    ship: string
    good: string
    profit: number
    completed_at: string | null
  }>
}

export interface EconomicOpportunity {
  type: string
  score: number
  description: string
  expected_return: number
  risk_factor: number
  time_horizon_minutes: number
}

export interface EconomicSummary {
  phase: string
  strategy: string
  opportunities_count: number
  high_priority: number
  total_expected_profit: number
  best_opportunity: string | null
  refinery_chains: number
}

export interface ScoredContract {
  contract_id: string
  score: number
  total_payment: number
  time_remaining_hours: number
  total_units: number
  payment_per_unit: number
  market_efficiency: number
  recommended: boolean
}

export type BrainState = 'idle' | 'running' | 'paused' | 'error'
export type MarketCondition = 'bull' | 'bear' | 'volatile' | 'stable'
export type ShipRole = 'mining' | 'trading' | 'exploration' | 'combat' | 'transport' | 'gas_siphoning' | 'refining' | 'command' | 'carrier'
export type ActivityType = 'mining' | 'trading' | 'navigation' | 'extraction' | 'automation' | 'contract'

export interface Activity {
  id: string
  type: ActivityType
  text: string
  time: string
}

export interface CycleResult {
  cycle: number
  contracts?: { accepted: number; fulfilled: number }
  mining?: { active_miners: number; total_extracted: number; results: Array<{ ship: string; extracted: number }> }
  refining?: { active_refiners: number; total_fuel_produced: number }
  trading?: { active_traders: number; opportunities_found: number; executed_trades: number; profit: number }
  trade_execution?: { executed: number }
  multi_hop?: { routes: Array<{ stops: string[]; goods: string[]; total_profit: number }>; count: number }
  exploration?: { active_explorers: number; scans_completed: number }
  fuel?: { ships_needing_fuel: number; refueled: number }
  expansion?: { purchased: number | null; price?: number }
  market_scan?: { scanned: number; system: string }
  market_discovery?: { discovered: number }
  role_optimization?: { total_assignments: number; market_condition: string }
}

export type AppAction =
  | { type: 'SET_CONNECTED'; payload: boolean }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_AGENT'; payload: Agent | null }
  | { type: 'SET_SHIPS'; payload: Ship[] }
  | { type: 'SET_CONTRACTS'; payload: Contract[] }
  | { type: 'SET_SELECTED_SHIP'; payload: Ship | null }
  | { type: 'ADD_ACTIVITY'; payload: Activity }
  | { type: 'SET_WAYPOINTS'; payload: Waypoint[] }
  | { type: 'SET_BRAIN_STATE'; payload: BrainState }
  | { type: 'SET_AUTO_MODE'; payload: boolean }
  | { type: 'SET_METRICS'; payload: BrainMetrics | null }
  | { type: 'SET_TRADE_OPPORTUNITIES'; payload: TradeOpportunity[] }
  | { type: 'SET_MULTI_HOP_ROUTES'; payload: MultiHopRoute[] }
  | { type: 'SET_ROLE_OPTIMIZATION'; payload: RoleOptimization | null }
  | { type: 'SET_PROFIT_HISTORY'; payload: ProfitHistory | null }
  | { type: 'SET_SYSTEM_SYMBOL'; payload: string }

export interface AppState {
  connected: boolean
  loading: boolean
  agent: Agent | null
  ships: Ship[]
  contracts: Contract[]
  selectedShip: Ship | null
  activities: Activity[]
  waypoints: Waypoint[]
  brainState: BrainState
  autoMode: boolean
  metrics: BrainMetrics | null
  tradeOpportunities: TradeOpportunity[]
  multiHopRoutes: MultiHopRoute[]
  roleOptimization: RoleOptimization | null
  profitHistory: ProfitHistory | null
  systemSymbol: string
}