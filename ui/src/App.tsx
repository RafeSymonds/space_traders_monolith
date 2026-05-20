import { useGame } from './services/GameContext'
import { MetricsPanel } from './components/MetricsPanel'
import { FleetPanel } from './components/FleetPanel'
import { TradePanel } from './components/TradePanel'
import './index.css'

function Header() {
  const { state, startBrain, pauseBrain, runCycle } = useGame()
  const { brainState, autoMode, connected } = state

  return (
    <header className="header">
      <div className="header-left">
        <div className="logo">
          <div className="logo-icon">🚀</div>
          <span>Space Traders</span>
        </div>
        <div className="brain-controls">
          <button
            className={`btn ${autoMode ? 'btn-primary' : 'btn-secondary'} btn-sm`}
            onClick={autoMode ? pauseBrain : startBrain}
          >
            {autoMode ? '⏸️ Brain' : '▶️ Brain'}
          </button>
          <button className="btn btn-secondary btn-sm" onClick={runCycle}>
            🔄 Cycle
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
  )
}

function ActivityFeed() {
  const { state } = useGame()
  const { activities } = state

  const getIcon = (type: string) => {
    switch (type) {
      case 'mining': return '⛏️'
      case 'trading': return '📦'
      case 'navigation': return '🚀'
      case 'extraction': return '💎'
      case 'automation': return '🤖'
      case 'contract': return '📋'
      default: return '•'
    }
  }

  return (
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
                {getIcon(activity.type)}
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
              <p>System running automatically</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function ContractsPanel() {
  const { state } = useGame()
  const { contracts } = state

  return (
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
              <p>Auto-accepting contracts...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function ShipDetailPanel() {
  const { state, dispatch } = useGame()
  const { selectedShip } = state

  if (!selectedShip) {
    return (
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
        <div className="no-selection">
          <div className="no-selection-icon">🚀</div>
          <h3>No Ship Selected</h3>
          <p>Click a ship in the fleet panel</p>
        </div>
      </div>
    )
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'mining': return '⛏️'
      case 'trading': return '📦'
      case 'exploration': return '🔭'
      default: return '🚀'
    }
  }

  return (
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
        <div className="ship-detail-header">
          <div className="ship-detail-icon">{getRoleIcon(selectedShip.role)}</div>
          <div className="ship-detail-info">
            <h2>{selectedShip.symbol}</h2>
            <p>{selectedShip.role} • {selectedShip.status}</p>
          </div>
        </div>
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
        {selectedShip.last_action && (
          <div className="info-card full-width">
            <div className="info-card-label">Last Action</div>
            <div className="info-card-value">{selectedShip.last_action}</div>
          </div>
        )}
      </div>
    </div>
  )
}

function SystemMap() {
  const { state } = useGame()
  const { waypoints, selectedShip, systemSymbol } = state

  return (
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
            <div className="ship-marker" style={{ left: '50%', top: '50%' }} title="Your ship">
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
  )
}

function App() {
  const { state } = useGame()
  const { loading } = state

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
      <Header />
      <main className="main-content">
        <MetricsPanel />
        <FleetPanel />
        <ShipDetailPanel />
        <TradePanel />
        <ContractsPanel />
        <ActivityFeed />
        <SystemMap />
      </main>
    </div>
  )
}

export default App