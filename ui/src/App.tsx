import { useState, useEffect, useCallback } from 'react'
import './index.css'

const API_BASE = 'http://localhost:8000/api/v1'

interface Agent {
  symbol: string
  headquarters: string
  credits: number
  startingFaction: string
  shipCount: number
}

interface Ship {
  symbol: string
  role: string
  system: string | null
  waypoint: string | null
  status: string
  busy: boolean
  cargo: { used: number; capacity: number }
  last_action?: string | null
}

interface Contract {
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

interface Activity {
  id: string
  type: 'mining' | 'trading' | 'navigation' | 'extraction' | 'automation' | 'contract'
  text: string
  time: string
}

interface Waypoint {
  symbol: string
  type: string
  x: number
  y: number
  traits: string[]
}

interface BrainMetrics {
  total_ships: number
  total_credits: number
  ships_mining: number
  ships_trading: number
  ships_exploring: number
  ships_available: number
  total_cargo_units: number
  contracts_completed: number
  ships_purchased: number
  credits_spent: number
}

interface TradeOpportunity {
  buy_location: string
  sell_location: string
  profit_per_unit: number
  volume: number
  total_profit: number
}

function App() {
  const [connected, setConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [agent, setAgent] = useState<Agent | null>(null)
  const [ships, setShips] = useState<Ship[]>([])
  const [contracts, setContracts] = useState<Contract[]>([])
  const [selectedShip, setSelectedShip] = useState<Ship | null>(null)
  const [activities, setActivities] = useState<Activity[]>([])
  const [waypoints, setWaypoints] = useState<Waypoint[]>([])
  const [activeTab, setActiveTab] = useState<'overview' | 'cargo' | 'nav' | 'automation'>('overview')
  const [brainState, setBrainState] = useState<string>('idle')
  const [autoMode, setAutoMode] = useState(false)
  const [metrics, setMetrics] = useState<BrainMetrics | null>(null)
  const [tradeOpportunities, setTradeOpportunities] = useState<TradeOpportunity[]>([])
  const [systemSymbol, setSystemSymbol] = useState<string>('')

  const addActivity = useCallback((type: Activity['type'], text: string) => {
    const newActivity: Activity = {
      id: Date.now().toString(),
      type,
      text,
      time: new Date().toLocaleTimeString(),
    }
    setActivities(prev => [newActivity, ...prev.slice(0, 99)])
  }, [])

  const fetchBrainStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/automation/brain/status`)
      if (res.ok) {
        const data = await res.json()
        setBrainState(data.state)
        setAutoMode(data.auto_mode)
        setMetrics(data.metrics)
      }
    } catch {
      // brain not available
    }
  }, [])

  const fetchData = useCallback(async () => {
    try {
      const [fleetRes, agentRes, contractsRes] = await Promise.all([
        fetch(`${API_BASE}/fleet/`),
        fetch(`${API_BASE}/fleet/agent`),
        fetch(`${API_BASE}/fleet/contracts`),
      ])

      if (fleetRes.ok && agentRes.ok) {
        setConnected(true)
        const fleetData = await fleetRes.json()
        const agentData = await agentRes.json()
        const contractsData = await contractsRes.json()
        
        setShips(fleetData.ships || [])
        setAgent(agentData)
        setContracts(contractsData.data || [])

        if (!systemSymbol && agentData.headquarters) {
          const sys = agentData.headquarters.split('-').slice(0, 2).join('-')
          setSystemSymbol(sys)
          fetchWaypoints(sys)
        }
        
        if (fleetData.ships?.length > 0 && !selectedShip) {
          setSelectedShip(fleetData.ships[0])
        }
      } else {
        setConnected(false)
      }
    } catch {
      setConnected(false)
    } finally {
      setLoading(false)
    }
  }, [selectedShip, systemSymbol])

  const fetchWaypoints = async (sys: string) => {
    try {
      const res = await fetch(`${API_BASE}/automation/systems/waypoints?system_symbol=${sys}`)
      if (res.ok) {
        const data = await res.json()
        setWaypoints(data.waypoints || [])
      }
    } catch {
      // ignore
    }
  }

  const fetchTradeOpportunities = async () => {
    try {
      const res = await fetch(`${API_BASE}/automation/trading/opportunities?min_profit=500`)
      if (res.ok) {
        const data = await res.json()
        setTradeOpportunities(data.opportunities || [])
      }
    } catch {
      // ignore
    }
  }

  useEffect(() => {
    fetchData()
    fetchBrainStatus()
    const interval = setInterval(() => {
      fetchData()
      fetchBrainStatus()
    }, 5000)
    return () => clearInterval(interval)
  }, [fetchData, fetchBrainStatus])

  const handleDock = async () => {
    if (!selectedShip) return
    try {
      await fetch(`${API_BASE}/fleet/${selectedShip.symbol}/dock`, { method: 'POST' })
      addActivity('navigation', `${selectedShip.symbol} docked`)
      fetchData()
    } catch (err) {
      console.error('Dock failed:', err)
    }
  }

  const handleOrbit = async () => {
    if (!selectedShip) return
    try {
      await fetch(`${API_BASE}/fleet/${selectedShip.symbol}/orbit`, { method: 'POST' })
      addActivity('navigation', `${selectedShip.symbol} entered orbit`)
      fetchData()
    } catch (err) {
      console.error('Orbit failed:', err)
    }
  }

  const handleExtract = async () => {
    if (!selectedShip) return
    try {
      const res = await fetch(`${API_BASE}/fleet/${selectedShip.symbol}/extract`, { method: 'POST' })
      const data = await res.json()
      addActivity('extraction', `${selectedShip.symbol} extracted ${data.extracts?.[0]?.units || 0} units`)
      fetchData()
    } catch (err) {
      console.error('Extract failed:', err)
    }
  }

  const handleStartBrain = async () => {
    try {
      await fetch(`${API_BASE}/automation/brain/start`, { method: 'POST' })
      addActivity('automation', 'Fleet brain started')
      fetchBrainStatus()
    } catch (err) {
      console.error('Start brain failed:', err)
    }
  }

  const handlePauseBrain = async () => {
    try {
      await fetch(`${API_BASE}/automation/brain/pause`, { method: 'POST' })
      addActivity('automation', 'Fleet brain paused')
      fetchBrainStatus()
    } catch (err) {
      console.error('Pause brain failed:', err)
    }
  }

  const handleRunCycle = async () => {
    try {
      const res = await fetch(`${API_BASE}/automation/brain/cycle`, { method: 'POST' })
      const data = await res.json()
      if (data.contracts) {
        if (data.contracts.accepted > 0) addActivity('contract', `Accepted ${data.contracts.accepted} contracts`)
        if (data.contracts.fulfilled > 0) addActivity('contract', `Fulfilled ${data.contracts.fulfilled} contracts`)
      }
      if (data.mining?.results) {
        data.mining.results.forEach((r: any) => {
          if (r.extracted > 0) addActivity('mining', `${r.ship} extracted ${r.extracted} units`)
        })
      }
      if (data.expansion?.purchased) {
        addActivity('automation', `Purchased ${data.expansion.purchased} for ${data.expansion.price} credits`)
      }
      fetchData()
      fetchBrainStatus()
    } catch (err) {
      console.error('Run cycle failed:', err)
    }
  }

  const handleCreateMiningFleet = async () => {
    try {
      await fetch(`${API_BASE}/automation/fleet/create-mining-fleet?num_ships=3`, { method: 'POST' })
      addActivity('automation', 'Mining fleet created')
      fetchData()
    } catch (err) {
      console.error('Create mining fleet failed:', err)
    }
  }

  const handleAssignRole = async (shipSymbol: string, role: string) => {
    try {
      await fetch(`${API_BASE}/automation/fleet/assign-role`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ship_symbol: shipSymbol, role }),
      })
      addActivity('automation', `${shipSymbol} assigned to ${role}`)
      fetchData()
    } catch (err) {
      console.error('Assign role failed:', err)
    }
  }

  const handlePurchaseShip = async () => {
    if (!agent?.headquarters) return
    handleRunCycle()
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'mining': return '⛏️'
      case 'trading': return '📦'
      case 'exploration': return '🔭'
      case 'combat': return '⚔️'
      default: return '🚀'
    }
  }

  const getCargoPercent = (ship: Ship) => {
    if (!ship.cargo?.capacity) return 0
    return Math.round((ship.cargo.used / ship.cargo.capacity) * 100)
  }

  const formatNumber = (n: number) => n.toLocaleString()

  if (loading) {
    return (
      <div className="app">
        <div className="loading" style={{ height: '100vh' }}>
          <div className="spinner" />
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <div className="logo">
            <div className="logo-icon">🚀</div>
            <span>Space Traders</span>
          </div>
          <div className="brain-controls">
            <button
              className={`btn ${autoMode ? 'btn-primary' : 'btn-secondary'} btn-sm`}
              onClick={autoMode ? handlePauseBrain : handleStartBrain}
            >
              {autoMode ? '⏸️ Brain' : '▶️ Brain'}
            </button>
            <button className="btn btn-secondary btn-sm" onClick={handleRunCycle}>
              🔄 Cycle
            </button>
            <button className="btn btn-secondary btn-sm" onClick={fetchTradeOpportunities}>
              📊 Scan
            </button>
          </div>
        </div>
        <div className="header-right">
          <div className={`brain-status ${brainState}`}>
            <span className="brain-dot" />
            <span>{brainState.toUpperCase()}</span>
          </div>
          <div className="status-badge">
            <div className={`status-dot ${connected ? '' : 'error'}`} />
            <span>{connected ? 'Connected' : 'Offline'}</span>
          </div>
        </div>
      </header>

      <main className="main-content">
        {/* Metrics Panel */}
        <div className="panel metrics-panel">
          <div className="panel-header">
            <div className="panel-title">
              <svg className="panel-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
              </svg>
              Fleet Metrics
            </div>
          </div>
          <div className="panel-body">
            {metrics && (
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-label">Credits</div>
                  <div className="metric-value credits">{formatNumber(metrics.total_credits)}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Ships</div>
                  <div className="metric-value">{metrics.total_ships}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Mining</div>
                  <div className="metric-value mining">{metrics.ships_mining}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Trading</div>
                  <div className="metric-value trading">{metrics.ships_trading}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Exploring</div>
                  <div className="metric-value exploration">{metrics.ships_exploring}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Available</div>
                  <div className="metric-value">{metrics.ships_available}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Cargo Units</div>
                  <div className="metric-value">{formatNumber(metrics.total_cargo_units)}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Purchased</div>
                  <div className="metric-value">{metrics.ships_purchased}</div>
                </div>
              </div>
            )}
            <div className="quick-actions">
              <button className="btn btn-secondary btn-sm" onClick={handleCreateMiningFleet}>
                ⛏️ Create Mining Fleet
              </button>
              <button className="btn btn-secondary btn-sm" onClick={handlePurchaseShip}>
                🛒 Auto Purchase Ship
              </button>
            </div>
          </div>
        </div>

        {/* Fleet Panel */}
        <div className="panel fleet-panel">
          <div className="panel-header">
            <div className="panel-title">
              <svg className="panel-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L4 7v10l8 5 8-5V7l-8-5z" />
              </svg>
              Fleet ({ships.length})
            </div>
            <div className="panel-actions">
              <button className="btn btn-icon btn-sm" onClick={fetchData}>↻</button>
            </div>
          </div>
          <div className="panel-body">
            <div className="ship-list">
              {ships.map(ship => (
                <div
                  key={ship.symbol}
                  className={`ship-card ${selectedShip?.symbol === ship.symbol ? 'selected' : ''} ${ship.busy ? 'busy' : ''}`}
                  onClick={() => setSelectedShip(ship)}
                >
                  <div className="ship-header">
                    <span className="ship-name">{ship.symbol}</span>
                    <div className="ship-badges">
                      <span className={`ship-role ${ship.role}`}>{ship.role}</span>
                      {ship.busy && <span className="busy-badge">⏳</span>}
                    </div>
                  </div>
                  <div className="ship-stats">
                    <span className="ship-stat">📍 {ship.waypoint || 'Unknown'}</span>
                    {ship.last_action && <span className="ship-action">→ {ship.last_action}</span>}
                  </div>
                  <div className="progress-bar">
                    <div
                      className={`progress-fill ${ship.role}`}
                      style={{ width: `${getCargoPercent(ship)}%` }}
                    />
                  </div>
                </div>
              ))}
              {ships.length === 0 && (
                <div className="empty-state">
                  <div className="empty-state-icon">🚀</div>
                  <h4>No Ships</h4>
                  <p>Run a cycle to auto-purchase ships</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Detail Panel */}
        <div className="panel detail-panel">
          <div className="panel-header">
            <div className="panel-title">
              <svg className="panel-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 16v-4M12 8h.01" />
              </svg>
              Ship Details
            </div>
          </div>
          <div className="detail-view">
            <div className="detail-tabs">
              <div className={`detail-tab ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>Overview</div>
              <div className={`detail-tab ${activeTab === 'cargo' ? 'active' : ''}`} onClick={() => setActiveTab('cargo')}>Cargo</div>
              <div className={`detail-tab ${activeTab === 'nav' ? 'active' : ''}`} onClick={() => setActiveTab('nav')}>Nav</div>
              <div className={`detail-tab ${activeTab === 'automation' ? 'active' : ''}`} onClick={() => setActiveTab('automation')}>Auto</div>
            </div>
            <div className="detail-content">
              {selectedShip ? (
                <>
                  <div className="ship-detail-header">
                    <div className="ship-detail-icon">{getRoleIcon(selectedShip.role)}</div>
                    <div className="ship-detail-info">
                      <h2>{selectedShip.symbol}</h2>
                      <p>{selectedShip.role} • {selectedShip.status}</p>
                    </div>
                  </div>
                  {activeTab === 'overview' && (
                    <>
                      <div className="info-grid">
                        <div className="info-card">
                          <div className="info-card-label">System</div>
                          <div className="info-card-value">{selectedShip.system || 'Unknown'}</div>
                        </div>
                        <div className="info-card">
                          <div className="info-card-label">Waypoint</div>
                          <div className="info-card-value">{selectedShip.waypoint || 'Unknown'}</div>
                        </div>
                        <div className="info-card">
                          <div className="info-card-label">Status</div>
                          <div className="info-card-value">{selectedShip.status}</div>
                        </div>
                        <div className="info-card">
                          <div className="info-card-label">Cargo</div>
                          <div className="info-card-value">{selectedShip.cargo.used} / {selectedShip.cargo.capacity}</div>
                        </div>
                      </div>
                      <div className="action-buttons">
                        <button className="btn btn-secondary" onClick={handleDock}>Dock</button>
                        <button className="btn btn-secondary" onClick={handleOrbit}>Orbit</button>
                        <button className="btn btn-primary" onClick={handleExtract}>Extract</button>
                      </div>
                    </>
                  )}
                  {activeTab === 'automation' && (
                    <div className="role-assignment">
                      <p className="role-label">Assign Role:</p>
                      <div className="role-buttons">
                        {['mining', 'trading', 'exploration', 'transport'].map(role => (
                          <button
                            key={role}
                            className={`btn btn-sm ${selectedShip.role === role ? 'btn-primary' : 'btn-secondary'}`}
                            onClick={() => handleAssignRole(selectedShip.symbol, role)}
                          >
                            {getRoleIcon(role)} {role}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="no-selection">
                  <div className="no-selection-icon">🚀</div>
                  <h3>No Ship Selected</h3>
                  <p>Select a ship from the fleet panel</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Trade Opportunities Panel */}
        <div className="panel trades-panel">
          <div className="panel-header">
            <div className="panel-title">
              <svg className="panel-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
              </svg>
              Trade Opportunities
            </div>
          </div>
          <div className="panel-body">
            <div className="trade-list">
              {tradeOpportunities.slice(0, 5).map((opp, i) => (
                <div key={i} className="trade-card">
                  <div className="trade-route">
                    <span className="trade-location">{opp.buy_location}</span>
                    <span className="trade-arrow">→</span>
                    <span className="trade-location">{opp.sell_location}</span>
                  </div>
                  <div className="trade-stats">
                    <span className="trade-profit">+{formatNumber(opp.profit_per_unit)}/unit</span>
                    <span className="trade-volume">Vol: {opp.volume}</span>
                  </div>
                  <div className="trade-total">Total: {formatNumber(opp.total_profit)}</div>
                </div>
              ))}
              {tradeOpportunities.length === 0 && (
                <div className="empty-state">
                  <div className="empty-state-icon">📊</div>
                  <h4>No Opportunities</h4>
                  <p>Click Scan to find trade routes</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Contracts Panel */}
        <div className="panel contracts-panel">
          <div className="panel-header">
            <div className="panel-title">
              <svg className="panel-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" />
              </svg>
              Contracts ({contracts.filter(c => !c.fulfilled).length})
            </div>
          </div>
          <div className="panel-body">
            <div className="contract-list">
              {contracts.filter(c => !c.fulfilled).map(contract => (
                <div key={contract.id} className="contract-card">
                  <div className="contract-header">
                    <span className="contract-id">{contract.id.slice(0, 8)}</span>
                    <span className="contract-type">{contract.type}</span>
                  </div>
                  <div className="contract-description">
                    Deliver {contract.terms.deliver?.[0]?.unitsRequired || 0} units of {contract.terms.deliver?.[0]?.tradeSymbol || 'Unknown'}
                  </div>
                  <div className="contract-progress">
                    <div className="contract-progress-bar">
                      <div
                        className="contract-progress-fill"
                        style={{
                          width: `${((contract.terms.deliver?.[0]?.unitsFulfilled || 0) / (contract.terms.deliver?.[0]?.unitsRequired || 1)) * 100}%`
                        }}
                      />
                    </div>
                    <span>{contract.terms.deliver?.[0]?.unitsFulfilled || 0}/{contract.terms.deliver?.[0]?.unitsRequired || 0}</span>
                  </div>
                </div>
              ))}
              {contracts.filter(c => !c.fulfilled).length === 0 && (
                <div className="empty-state">
                  <div className="empty-state-icon">📋</div>
                  <h4>No Active Contracts</h4>
                  <p>Run cycles to accept contracts</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Activity Panel */}
        <div className="panel activity-panel">
          <div className="panel-header">
            <div className="panel-title">
              <svg className="panel-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
              </svg>
              Activity
            </div>
          </div>
          <div className="panel-body">
            <div className="activity-feed">
              {activities.map(activity => (
                <div key={activity.id} className="activity-item">
                  <div className={`activity-icon ${activity.type}`}>
                    {activity.type === 'mining' && '⛏️'}
                    {activity.type === 'trading' && '📦'}
                    {activity.type === 'navigation' && '🚀'}
                    {activity.type === 'extraction' && '💎'}
                    {activity.type === 'automation' && '🤖'}
                    {activity.type === 'contract' && '📋'}
                  </div>
                  <div className="activity-content">
                    <div className="activity-text">{activity.text}</div>
                    <div className="activity-time">{activity.time}</div>
                  </div>
                </div>
              ))}
              {activities.length === 0 && (
                <div className="empty-state">
                  <div className="empty-state-icon">📊</div>
                  <h4>No Activity</h4>
                  <p>Run cycles to see activity</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* System Map Panel */}
        <div className="panel system-panel">
          <div className="panel-header">
            <div className="panel-title">
              <svg className="panel-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v4M12 18v4M2 12h4M18 12h4" />
              </svg>
              System Map {systemSymbol && `(${systemSymbol})`}
            </div>
          </div>
          <div className="panel-body">
            <div className="system-map">
              <div className="map-grid" />
              {waypoints.map(wp => (
                <div
                  key={wp.symbol}
                  className={`waypoint ${wp.type.toLowerCase().replace('_', '-')}`}
                  style={{ left: `${50 + wp.x * 0.8}%`, top: `${50 - wp.y * 0.8}%` }}
                  title={`${wp.symbol} (${wp.type})`}
                />
              ))}
              {selectedShip && (
                <div
                  className="ship-marker"
                  style={{
                    left: '50%',
                    top: '50%',
                  }}
                  title="Your ship"
                >
                  🚀
                </div>
              )}
            </div>
            <div className="waypoint-legend">
              <span className="legend-item"><span className="legend-dot planet" />Planet</span>
              <span className="legend-item"><span className="legend-dot station" />Station</span>
              <span className="legend-item"><span className="legend-dot asteroid" />Asteroid</span>
              <span className="legend-item"><span className="legend-dot gas-giant" />Gas Giant</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App