import { useState } from 'react'
import { useGame } from '../services/GameContext'
import { ApiService } from '../services/api'

export function TradePanel() {
  const { state } = useGame()
  const { tradeOpportunities, multiHopRoutes, roleOptimization, profitHistory } = state
  const [activeSubTab, setActiveSubTab] = useState<'opportunities' | 'routes' | 'history'>('opportunities')

  return (
    <div className="panel trades-panel">
      <div className="panel-header">
        <div className="panel-title">
          <svg className="panel-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
          </svg>
          Trading
        </div>
      </div>
      <div className="panel-body">
        <div className="trade-tabs">
          <div 
            className={`trade-tab ${activeSubTab === 'opportunities' ? 'active' : ''}`}
            onClick={() => setActiveSubTab('opportunities')}
          >
            Opportunities ({tradeOpportunities.length})
          </div>
          <div 
            className={`trade-tab ${activeSubTab === 'routes' ? 'active' : ''}`}
            onClick={() => setActiveSubTab('routes')}
          >
            Multi-Hop ({multiHopRoutes.length})
          </div>
          <div 
            className={`trade-tab ${activeSubTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveSubTab('history')}
          >
            History
          </div>
        </div>

        {activeSubTab === 'opportunities' && (
          <div className="trade-list">
            {tradeOpportunities.slice(0, 5).map((opp, i) => (
              <div key={i} className="trade-card">
                <div className="trade-route">
                  <span className="trade-location">{opp.buy_location}</span>
                  <span className="trade-arrow">→</span>
                  <span className="trade-location">{opp.sell_location}</span>
                </div>
                <div className="trade-good">{opp.trade_good}</div>
                <div className="trade-stats">
                  <span className="trade-profit">+{opp.profit_per_unit.toLocaleString()}/unit</span>
                  <span className="trade-volume">Vol: {opp.volume}</span>
                </div>
                <div className="trade-total">Total: {opp.total_profit.toLocaleString()}</div>
              </div>
            ))}
            {tradeOpportunities.length === 0 && (
              <div className="empty-state">
                <div className="empty-state-icon">📊</div>
                <h4>No Opportunities</h4>
                <p>Auto-scanning markets...</p>
              </div>
            )}
          </div>
        )}

        {activeSubTab === 'routes' && (
          <div className="trade-list">
            {multiHopRoutes.slice(0, 5).map((route, i) => (
              <div key={i} className="trade-card multi-hop">
                <div className="trade-route">
                  {route.stops.map((stop, j) => (
                    <span key={j}>
                      {stop}
                      {j < route.stops.length - 1 && <span className="trade-arrow"> → </span>}
                    </span>
                  ))}
                </div>
                <div className="trade-goods">
                  {route.goods.map((g, j) => <span key={j} className="good-tag">{g}</span>)}
                </div>
                <div className="trade-profit">+{route.total_profit.toLocaleString()}</div>
                <div className="trade-time">~{route.estimated_time_minutes}min</div>
              </div>
            ))}
            {multiHopRoutes.length === 0 && (
              <div className="empty-state">
                <div className="empty-state-icon">🔄</div>
                <h4>No Routes</h4>
                <p>Exploring more systems...</p>
              </div>
            )}
          </div>
        )}

        {activeSubTab === 'history' && (
          <div className="trade-list">
            {profitHistory?.trades.slice(0, 10).map((trade, i) => (
              <div key={i} className="trade-card history">
                <span className="trade-ship">{trade.ship}</span>
                <span className="trade-good">{trade.good}</span>
                <span className="trade-profit positive">+{trade.profit.toLocaleString()}</span>
              </div>
            ))}
            {(!profitHistory || profitHistory.trades.length === 0) && (
              <div className="empty-state">
                <div className="empty-state-icon">📈</div>
                <h4>No History</h4>
                <p>Execute trades to see history</p>
              </div>
            )}
            {profitHistory && profitHistory.total_profit > 0 && (
              <div className="profit-summary">
                Total Profit: <span className="positive">{profitHistory.total_profit.toLocaleString()}</span>
              </div>
            )}
          </div>
        )}

        {roleOptimization && (
          <div className="role-info">
            <span className="role-condition">Market: {roleOptimization.market_condition}</span>
            <span>Mining Score: {(roleOptimization.mining_score * 100).toFixed(0)}%</span>
            <span>Trading Score: {(roleOptimization.trading_score * 100).toFixed(0)}%</span>
          </div>
        )}
      </div>
    </div>
  )
}