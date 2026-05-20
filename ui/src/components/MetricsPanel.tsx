import { useGame } from '../services/GameContext'

const formatNumber = (n: number) => n.toLocaleString()

const phaseColors: Record<string, string> = {
  expansion: '#4ade80',
  contraction: '#f87171',
  peak: '#fbbf24',
  trough: '#60a5fa',
}

const strategyColors: Record<string, string> = {
  scalping: '#f97316',
  swing: '#8b5cf6',
  arbitrage: '#06b6d4',
  speculative: '#ec4899',
}

export function MetricsPanel() {
  const { state } = useGame()
  const { metrics } = state

  if (!metrics) return null

  return (
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
            <div className="metric-value mining">{metrics.ships_mining || metrics.total_extracted || 0}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Trading</div>
            <div className="metric-value trading">{metrics.active_traders || metrics.ships_trading || 0}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Trades Done</div>
            <div className="metric-value">{metrics.trades_executed || 0}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Total Profit</div>
            <div className="metric-value profit">{formatNumber(metrics.total_profit || 0)}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Cargo</div>
            <div className="metric-value">{formatNumber(metrics.total_cargo_units || 0)}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Contracts</div>
            <div className="metric-value">{metrics.contracts_completed || 0}</div>
          </div>
        </div>
        
        {(metrics as any).economic_phase && (
          <div className="economic-metrics">
            <div className="economic-header">Economic Intelligence</div>
            <div className="economic-row">
              <span className="economic-label">Phase:</span>
              <span className="economic-value" style={{ color: phaseColors[(metrics as any).economic_phase] || '#fff' }}>
                {(metrics as any).economic_phase?.toUpperCase()}
              </span>
            </div>
            <div className="economic-row">
              <span className="economic-label">Strategy:</span>
              <span className="economic-value" style={{ color: strategyColors[(metrics as any).strategy] || '#fff' }}>
                {(metrics as any).strategy?.toUpperCase()}
              </span>
            </div>
            <div className="economic-row">
              <span className="economic-label">Opportunities:</span>
              <span className="economic-value">{(metrics as any).opportunities_count || 0}</span>
            </div>
            <div className="economic-row">
              <span className="economic-label">Refinery Chains:</span>
              <span className="economic-value">{(metrics as any).refinery_chains || 0}</span>
            </div>
            <div className="economic-row">
              <span className="economic-label">Expected Profit:</span>
              <span className="economic-value profit">+{formatNumber((metrics as any).total_expected_profit || 0)}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}