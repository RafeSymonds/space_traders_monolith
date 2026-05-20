const API_BASE = '/api/v1'

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
  economic_phase?: string
  strategy?: string
  opportunities_count?: number
  refinery_chains?: number
  total_expected_profit?: number
}

export interface BrainStatus {
  state: string
  auto_mode: boolean
  cycle_count: number
  metrics: BrainMetrics
  last_update: string
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

export interface EconomicSummary {
  phase: string
  strategy: string
  opportunities_count: number
  high_priority: number
  total_expected_profit: number
  best_opportunity: string | null
  refinery_chains: number
}

export interface EconomicOpportunity {
  type: string
  score: number
  description: string
  expected_return: number
  risk_factor: number
  time_horizon_minutes: number
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

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T | null> {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, options)
    if (!res.ok) return null
    return await res.json()
  } catch {
    return null
  }
}

export const ApiService = {
  fleet: {
    getShips: () => fetchApi<{ ships: Ship[] }>('/fleet/'),
    getAgent: () => fetchApi<Agent>('/fleet/agent'),
    getContracts: () => fetchApi<{ data: Contract[] }>('/fleet/contracts'),
    dock: (shipSymbol: string) => fetchApi(`/fleet/${shipSymbol}/dock`, { method: 'POST' }),
    orbit: (shipSymbol: string) => fetchApi(`/fleet/${shipSymbol}/orbit`, { method: 'POST' }),
    extract: (shipSymbol: string) => fetchApi(`/fleet/${shipSymbol}/extract`, { method: 'POST' }),
  },

  brain: {
    getStatus: () => fetchApi<BrainStatus>('/automation/brain/status'),
    start: () => fetchApi('/automation/brain/start', { method: 'POST' }),
    pause: () => fetchApi('/automation/brain/pause', { method: 'POST' }),
    runCycle: () => fetchApi('/automation/brain/cycle', { method: 'POST' }),
  },

  trading: {
    getOpportunities: (minProfit = 500) => 
      fetchApi<{ opportunities: TradeOpportunity[] }>(`/automation/trading/opportunities?min_profit=${minProfit}`),
    getMultiHopRoutes: (systemSymbol?: string, minProfit = 500, maxHops = 3) => {
      const params = new URLSearchParams({
        min_profit: String(minProfit),
        max_hops: String(maxHops),
      })
      if (systemSymbol) params.set('system_symbol', systemSymbol)
      return fetchApi<{ routes: MultiHopRoute[]; count: number }>(`/automation/trading/multi-hop-routes?${params}`)
    },
    getRoleOptimization: () => fetchApi<RoleOptimization>('/automation/trading/role-optimization'),
    getActiveTrades: () => fetchApi('/automation/trading/active-trades'),
    getProfitHistory: (limit = 50) => fetchApi<ProfitHistory>(`/automation/trading/profit-history?limit=${limit}`),
  },

  automation: {
    assignRole: (shipSymbol: string, role: string) =>
      fetchApi('/automation/fleet/assign-role', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ship_symbol: shipSymbol, role }),
      }),
    createMiningFleet: (numShips = 3) =>
      fetchApi(`/automation/fleet/create-mining-fleet?num_ships=${numShips}`, { method: 'POST' }),
    createTradingFleet: (numShips = 2) =>
      fetchApi(`/automation/fleet/create-trading-fleet?num_ships=${numShips}`, { method: 'POST' }),
    getSystemWaypoints: (systemSymbol: string) =>
      fetchApi<{ waypoints: Waypoint[] }>(`/automation/systems/waypoints?system_symbol=${systemSymbol}`),
    getPendingContracts: () => fetchApi('/automation/contracts/pending'),
    getExpansionStats: () => fetchApi('/automation/expansion/stats'),
  },

  economic: {
    getSummary: () => fetchApi<EconomicSummary>('/automation/economic/summary'),
    getOpportunities: () => fetchApi<{ opportunities: EconomicOpportunity[]; count: number }>('/automation/economic/opportunities'),
  },

  contracts: {
    getPrioritized: () => fetchApi<{ contracts: ScoredContract[] }>('/automation/contracts/prioritized'),
  },
}