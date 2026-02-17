import React from 'react';

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
            <div className="text-gray-400 text-sm">Your Scans</div>
            <div className="text-3xl font-bold text-cyan-400 mt-1">
              {userScanCount || 0}
            </div>
          </div>
          <div className="text-4xl">🔍</div>
        </div>
      </div>

      <div className="metric-card">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-gray-400 text-sm">Cycles Found</div>
            <div className="text-3xl font-bold text-green-400 mt-1">
              {systemMetrics.total_cycles_found || 0}
            </div>
          </div>
          <div className="text-4xl">🔄</div>
        </div>
      </div>

      <div className="metric-card">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-gray-400 text-sm">Avg Detection Time</div>
            <div className="text-3xl font-bold text-purple-400 mt-1">
              {systemMetrics.avg_detection_time_ms 
                ? systemMetrics.avg_detection_time_ms.toFixed(1) 
                : '0.0'}ms
            </div>
          </div>
          <div className="text-4xl">⚡</div>
        </div>
      </div>

      {persistenceMetrics.total_opportunities > 0 && (
        <>
          <div className="metric-card">
            <div className="text-gray-400 text-sm">Avg Lifespan</div>
            <div className="text-2xl font-bold text-yellow-400 mt-1">
              {persistenceMetrics.avg_lifespan_ms.toFixed(0)}ms
            </div>
          </div>

          <div className="metric-card">
            <div className="text-gray-400 text-sm">Sharpe Ratio</div>
            <div className="text-2xl font-bold text-orange-400 mt-1">
              {persistenceMetrics.sharpe_ratio.toFixed(3)}
            </div>
          </div>

          <div className="metric-card">
            <div className="text-gray-400 text-sm">Engine Status</div>
            <div className="flex items-center mt-2">
              <div className={`w-3 h-3 rounded-full mr-2 ${
                systemMetrics.cpp_engine_active ? 'bg-green-500' : 'bg-yellow-500'
              }`}></div>
              <div className="text-sm text-gray-300">
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
