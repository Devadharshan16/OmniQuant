import React from 'react';
import GradientCounter from './GradientCounter';

function MetricsPanel({ metrics, userScanCount }) {
  if (!metrics) {
    return (
      <div className="lg:col-span-3">
        <div className="metric-card">
          <p className="text-gray-400">Loading metrics...</p>
        </div>
      </div>
    );
  }

  const systemMetrics = metrics.system_metrics || {};
  const persistenceMetrics = metrics.persistence_metrics || {};

  return (
    <>
      <div className="metric-card">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-gray-500 text-xs uppercase tracking-wider font-medium">Your Scans</div>
            <div className="text-3xl font-bold mt-1.5">
              <GradientCounter
                value={userScanCount || 0}
                gradient="linear-gradient(135deg, #22d3ee 0%, #a78bfa 100%)"
              />
            </div>
          </div>
          <div className="text-3xl opacity-50">🔍</div>
        </div>
      </div>

      <div className="metric-card">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-gray-500 text-xs uppercase tracking-wider font-medium">Cycles Found</div>
            <div className="text-3xl font-bold mt-1.5">
              <GradientCounter
                value={systemMetrics.total_cycles_found || 0}
                gradient="linear-gradient(135deg, #34d399 0%, #a78bfa 100%)"
              />
            </div>
          </div>
          <div className="text-3xl opacity-50">🔄</div>
        </div>
      </div>

      <div className="metric-card">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-gray-500 text-xs uppercase tracking-wider font-medium">Avg Detection</div>
            <div className="text-3xl font-bold mt-1.5">
              <GradientCounter
                value={systemMetrics.avg_detection_time_ms || 0}
                decimals={1}
                gradient="linear-gradient(135deg, #c084fc 0%, #818cf8 100%)"
                suffix="ms"
              />
            </div>
          </div>
          <div className="text-3xl opacity-50">⚡</div>
        </div>
      </div>

      {persistenceMetrics.total_opportunities > 0 && (
        <>
          <div className="metric-card">
            <div className="text-gray-500 text-xs uppercase tracking-wider font-medium">Avg Lifespan</div>
            <div className="text-2xl font-bold mt-1.5">
              <GradientCounter
                value={Math.floor((persistenceMetrics.avg_lifespan_ms || 0) / Math.pow(10, Math.max(0, String(Math.floor(persistenceMetrics.avg_lifespan_ms || 0)).length - 4)))}
                gradient="linear-gradient(135deg, #fbbf24 0%, #c084fc 100%)"
                suffix="ms"
              />
            </div>
          </div>

          <div className="metric-card">
            <div className="text-gray-500 text-xs uppercase tracking-wider font-medium">Sharpe Ratio</div>
            <div className="text-2xl font-bold mt-1.5">
              <GradientCounter
                value={persistenceMetrics.sharpe_ratio || 0}
                decimals={3}
                gradient="linear-gradient(135deg, #fb923c 0%, #c084fc 100%)"
              />
            </div>
          </div>

          <div className="metric-card">
            <div className="text-gray-500 text-xs uppercase tracking-wider font-medium">Engine Status</div>
            <div className="flex items-center mt-2.5">
              <div className={`w-2.5 h-2.5 rounded-full mr-2 ${
                systemMetrics.cpp_engine_active ? 'bg-emerald-500 shadow-lg shadow-emerald-500/50' : 'bg-amber-500 shadow-lg shadow-amber-500/50'
              }`}></div>
              <div className="text-xs text-gray-400 font-medium">
                {systemMetrics.cpp_engine_active ? 'C++ Engine' : 'Python Fallback'}
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}

export default MetricsPanel;
