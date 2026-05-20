import { createContext, useContext, useReducer, useCallback, useEffect, ReactNode } from 'react'
import { ApiService } from './api'
import type { AppState, AppAction, Activity, BrainMetrics, Ship, Contract, BrainState, TradeOpportunity, MultiHopRoute, RoleOptimization, ProfitHistory, CycleResult } from './api.types'

const initialState: AppState = {
  connected: false,
  loading: true,
  agent: null,
  ships: [],
  contracts: [],
  selectedShip: null,
  activities: [],
  waypoints: [],
  brainState: 'idle',
  autoMode: false,
  metrics: null,
  tradeOpportunities: [],
  multiHopRoutes: [],
  roleOptimization: null,
  profitHistory: null,
  systemSymbol: '',
}

function reducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_CONNECTED':
      return { ...state, connected: action.payload }
    case 'SET_LOADING':
      return { ...state, loading: action.payload }
    case 'SET_AGENT':
      return { ...state, agent: action.payload }
    case 'SET_SHIPS':
      return { ...state, ships: action.payload }
    case 'SET_CONTRACTS':
      return { ...state, contracts: action.payload }
    case 'SET_SELECTED_SHIP':
      return { ...state, selectedShip: action.payload }
    case 'ADD_ACTIVITY':
      return { ...state, activities: [action.payload, ...state.activities.slice(0, 99)] }
    case 'SET_WAYPOINTS':
      return { ...state, waypoints: action.payload }
    case 'SET_BRAIN_STATE':
      return { ...state, brainState: action.payload }
    case 'SET_AUTO_MODE':
      return { ...state, autoMode: action.payload }
    case 'SET_METRICS':
      return { ...state, metrics: action.payload }
    case 'SET_TRADE_OPPORTUNITIES':
      return { ...state, tradeOpportunities: action.payload }
    case 'SET_MULTI_HOP_ROUTES':
      return { ...state, multiHopRoutes: action.payload }
    case 'SET_ROLE_OPTIMIZATION':
      return { ...state, roleOptimization: action.payload }
    case 'SET_PROFIT_HISTORY':
      return { ...state, profitHistory: action.payload }
    case 'SET_SYSTEM_SYMBOL':
      return { ...state, systemSymbol: action.payload }
    default:
      return state
  }
}

interface GameContextValue {
  state: AppState
  dispatch: React.Dispatch<AppAction>
  addActivity: (type: Activity['type'], text: string) => void
  refreshAll: () => Promise<void>
  startBrain: () => Promise<void>
  pauseBrain: () => Promise<void>
  runCycle: () => Promise<void>
  fetchTradeData: () => Promise<void>
}

const GameContext = createContext<GameContextValue | null>(null)

export function GameProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState)

  const addActivity = useCallback((type: Activity['type'], text: string) => {
    const activity: Activity = {
      id: Date.now().toString(),
      type,
      text,
      time: new Date().toLocaleTimeString(),
    }
    dispatch({ type: 'ADD_ACTIVITY', payload: activity })
  }, [])

  const refreshAll = useCallback(async () => {
    const [fleetRes, agentRes, contractsRes, brainRes] = await Promise.all([
      ApiService.fleet.getShips(),
      ApiService.fleet.getAgent(),
      ApiService.fleet.getContracts(),
      ApiService.brain.getStatus(),
    ])

    if (fleetRes && agentRes) {
      dispatch({ type: 'SET_CONNECTED', payload: true })
      dispatch({ type: 'SET_SHIPS', payload: fleetRes.ships })
      dispatch({ type: 'SET_AGENT', payload: agentRes })
      dispatch({ type: 'SET_CONTRACTS', payload: contractsRes?.data || [] })

      if (!state.selectedShip && fleetRes.ships.length > 0) {
        dispatch({ type: 'SET_SELECTED_SHIP', payload: fleetRes.ships[0] })
      }

      if (!state.systemSymbol && agentRes.headquarters) {
        const sys = agentRes.headquarters.split('-').slice(0, 2).join('-')
        dispatch({ type: 'SET_SYSTEM_SYMBOL', payload: sys })
        const waypointsRes = await ApiService.automation.getSystemWaypoints(sys)
        if (waypointsRes?.waypoints) {
          dispatch({ type: 'SET_WAYPOINTS', payload: waypointsRes.waypoints })
        }
      }
    } else {
      dispatch({ type: 'SET_CONNECTED', payload: false })
    }

    if (brainRes) {
      dispatch({ type: 'SET_BRAIN_STATE', payload: brainRes.state as BrainState })
      dispatch({ type: 'SET_AUTO_MODE', payload: brainRes.auto_mode })
      dispatch({ type: 'SET_METRICS', payload: brainRes.metrics })
    }
  }, [state.selectedShip, state.systemSymbol])

  const fetchTradeData = useCallback(async () => {
    const [oppsRes, routesRes, roleRes, profitRes] = await Promise.all([
      ApiService.trading.getOpportunities(500),
      ApiService.trading.getMultiHopRoutes(state.systemSymbol || undefined, 500, 3),
      ApiService.trading.getRoleOptimization(),
      ApiService.trading.getProfitHistory(20),
    ])

    if (oppsRes?.opportunities) {
      dispatch({ type: 'SET_TRADE_OPPORTUNITIES', payload: oppsRes.opportunities })
    }
    if (routesRes?.routes) {
      dispatch({ type: 'SET_MULTI_HOP_ROUTES', payload: routesRes.routes })
    }
    if (roleRes) {
      dispatch({ type: 'SET_ROLE_OPTIMIZATION', payload: roleRes })
    }
    if (profitRes) {
      dispatch({ type: 'SET_PROFIT_HISTORY', payload: profitRes })
    }
  }, [state.systemSymbol])

  const startBrain = useCallback(async () => {
    await ApiService.brain.start()
    addActivity('automation', 'Fleet brain started')
    const status = await ApiService.brain.getStatus()
    if (status) {
      dispatch({ type: 'SET_BRAIN_STATE', payload: status.state as BrainState })
      dispatch({ type: 'SET_AUTO_MODE', payload: status.auto_mode })
    }
  }, [addActivity])

  const pauseBrain = useCallback(async () => {
    await ApiService.brain.pause()
    addActivity('automation', 'Fleet brain paused')
    const status = await ApiService.brain.getStatus()
    if (status) {
      dispatch({ type: 'SET_BRAIN_STATE', payload: status.state as BrainState })
      dispatch({ type: 'SET_AUTO_MODE', payload: status.auto_mode })
    }
  }, [addActivity])

  const runCycle = useCallback(async () => {
    const result = await ApiService.brain.runCycle() as CycleResult | null
    if (result) {
      if (result.contracts) {
        if (result.contracts.accepted > 0) addActivity('contract', `Accepted ${result.contracts.accepted} contracts`)
        if (result.contracts.fulfilled > 0) addActivity('contract', `Fulfilled ${result.contracts.fulfilled} contracts`)
      }
      if (result.mining?.results) {
        result.mining.results.forEach((r: { ship: string; extracted: number }) => {
          if (r.extracted > 0) addActivity('mining', `${r.ship} extracted ${r.extracted} units`)
        })
      }
      if (result.trading?.executed_trades && result.trading.executed_trades > 0) {
        addActivity('trading', `${result.trading.executed_trades} trades executed for ${result.trading.profit} profit`)
      }
      if (result.multi_hop?.count && result.multi_hop.count > 0) {
        addActivity('trading', `Found ${result.multi_hop.count} multi-hop routes`)
      }
      if (result.expansion?.purchased) {
        addActivity('automation', `Purchased ${result.expansion.purchased} ships`)
      }
    }
    await refreshAll()
  }, [addActivity, refreshAll])

  useEffect(() => {
    dispatch({ type: 'SET_LOADING', payload: true })
    refreshAll().finally(() => {
      dispatch({ type: 'SET_LOADING', payload: false })
    })
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      refreshAll()
    }, 5000)
    return () => clearInterval(interval)
  }, [refreshAll])

  return (
    <GameContext.Provider value={{ state, dispatch, addActivity, refreshAll, startBrain, pauseBrain, runCycle, fetchTradeData }}>
      {children}
    </GameContext.Provider>
  )
}

export function useGame() {
  const context = useContext(GameContext)
  if (!context) throw new Error('useGame must be used within GameProvider')
  return context
}