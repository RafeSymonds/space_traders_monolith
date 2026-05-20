import { useGame } from '../services/GameContext'
import type { Ship } from '../services/api.types'

export function FleetPanel() {
  const { state, dispatch } = useGame()
  const { ships, selectedShip } = state

  const selectShip = (ship: Ship) => {
    dispatch({ type: 'SET_SELECTED_SHIP', payload: ship })
  }

  const getCargoPercent = (ship: Ship) => {
    if (!ship.cargo?.capacity) return 0
    return Math.round((ship.cargo.used / ship.cargo.capacity) * 100)
  }

  return (
    <div className="panel fleet-panel">
      <div className="panel-header">
        <div className="panel-title">
          <svg className="panel-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2L4 7v10l8 5 8-5V7l-8-5z" />
          </svg>
          Fleet ({ships.length})
        </div>
      </div>
      <div className="panel-body">
        <div className="ship-list">
          {ships.map(ship => (
            <div
              key={ship.symbol}
              className={`ship-card ${selectedShip?.symbol === ship.symbol ? 'selected' : ''} ${ship.busy ? 'busy' : ''}`}
              onClick={() => selectShip(ship)}
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
              <p>System auto-purchases ships</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}