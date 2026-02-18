import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_ENDPOINTS } from '../config';

function LatencySensitivityAnalysis({ theme }) {
  const [baseReturn, setBaseReturn] = useState(2.5);
  const [pathLength, setPathLength] = useState(3);
  const [liquidity, setLiquidity] = useState(50000);
  const [volatility, setVolatility] = useState(0.01);
  const [initialCapital, setInitialCapital] = useState(1000);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [autoUpdate, setAutoUpdate] = useState(true);

  const analyzeLatency = async () => {
    setLoading(true);
    try {
      const response = await axios.post(API_ENDPOINTS.LATENCY_ANALYSIS, {
        base_return: parseFloat(baseReturn) / 100,
        path_length: parseInt(pathLength),
        liquidity: parseFloat(liquidity),
        volatility: parseFloat(volatility),
        fee_per_hop: 0.001,
        initial_capital: parseFloat(initialCapital)
      });

      if (response.data.success) {
        setResult(response.data);
      }
    } catch (error) {
      console.error('Error analyzing latency:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (autoUpdate) {
      analyzeLatency();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [baseReturn, pathLength, liquidity, volatility, initialCapital, autoUpdate]);

  const isDark = theme === 'dark';
  const bgClass = isDark ? 'bg-gray-800' : 'bg-white';
  const textClass = isDark ? 'text-gray-100' : 'text-gray-900';
  const borderClass = isDark ? 'border-gray-700' : 'border-gray-300';
  const inputBg = isDark ? 'bg-gray-700' : 'bg-gray-50';

  const getReliabilityColor = (color) => {
    const colors = {
      'red': isDark ? 'text-red-400' : 'text-red-600',
      'orange': isDark ? 'text-orange-400' : 'text-orange-600',
      'yellow': isDark ? 'text-yellow-400' : 'text-yellow-600',
      'green': isDark ? 'text-green-400' : 'text-green-600',
      'darkgreen': isDark ? 'text-emerald-400' : 'text-emerald-600'
    };
    return colors[color] || colors['green'];
  };

  return (
    <div className={`${bgClass} ${textClass} rounded-lg shadow-lg p-4 sm:p-6 border ${borderClass}`}>
      <div className="mb-4 sm:mb-6">
        <h2 className="text-xl sm:text-2xl font-bold mb-2 flex flex-wrap items-center gap-2">
          ⚡ Latency Sensitivity Analysis
          <span className="text-xs sm:text-sm font-normal px-2 sm:px-3 py-1 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 text-white">
            ELITE
          </span>
        </h2>
        <p className={`text-xs sm:text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'} mb-3`}>
          Analyze how arbitrage returns decay with execution latency
        </p>
        <div className={`${isDark ? 'bg-gray-900' : 'bg-purple-50'} border ${isDark ? 'border-gray-700' : 'border-purple-200'} rounded-lg p-4`}>
          <div className="text-center">
            <div className="text-lg font-semibold mb-1">🔹 Arbitrage Half-Life Metric</div>
            <div className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              Time until expected return reaches zero — the critical execution window
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4 mb-4 sm:mb-6">
        <div>
          <label className="block text-sm font-medium mb-2">
            Base Return (%)
          </label>
          <input
            type="number"
            value={baseReturn}
            onChange={(e) => setBaseReturn(e.target.value)}
            className={`w-full px-3 py-2 ${inputBg} border ${borderClass} rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent`}
            min="0"
            max="10"
            step="0.1"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Path Length (hops)
          </label>
          <input
            type="number"
            value={pathLength}
            onChange={(e) => setPathLength(e.target.value)}
            className={`w-full px-3 py-2 ${inputBg} border ${borderClass} rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent`}
            min="2"
            max="10"
            step="1"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Initial Capital ($)
          </label>
          <input
            type="number"
            value={initialCapital}
            onChange={(e) => setInitialCapital(e.target.value)}
            className={`w-full px-3 py-2 ${inputBg} border ${borderClass} rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent`}
            min="100"
            step="100"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 mb-4 sm:mb-6">
        <div>
          <label className="block text-sm font-medium mb-2">
            Liquidity ($)
          </label>
          <input
            type="range"
            value={liquidity}
            onChange={(e) => setLiquidity(e.target.value)}
            className="w-full"
            min="10000"
            max="500000"
            step="10000"
          />
          <div className="text-center text-sm font-mono">${liquidity.toLocaleString()}</div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Volatility
          </label>
          <input
            type="range"
            value={volatility}
            onChange={(e) => setVolatility(e.target.value)}
            className="w-full"
            min="0.001"
            max="0.05"
            step="0.001"
          />
          <div className="text-center text-sm font-mono">{(volatility * 100).toFixed(2)}%</div>
        </div>
      </div>

      <div className="flex items-center justify-between mb-6">
        <label className="flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={autoUpdate}
            onChange={(e) => setAutoUpdate(e.target.checked)}
            className="mr-2"
          />
          <span className="text-sm">Auto-calculate</span>
        </label>

        {!autoUpdate && (
          <button
            onClick={analyzeLatency}
            disabled={loading}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400"
          >
            {loading ? 'Analyzing...' : 'Analyze Latency'}
          </button>
        )}
      </div>

      {result && result.half_life_ms && (
        <div className="space-y-4">
          {/* Half-Life Display - ELITE METRIC */}
          <div className={`${isDark ? 'bg-gradient-to-br from-purple-900/50 to-pink-900/50' : 'bg-gradient-to-br from-purple-100 to-pink-100'} border-2 ${isDark ? 'border-purple-500/50' : 'border-purple-300'} rounded-xl p-4 sm:p-5 md:p-6 shadow-xl`}>
            <div className="text-center">
              <div className="text-xs sm:text-sm font-semibold mb-2 uppercase tracking-wider opacity-75">
                🔹 Arbitrage Half-Life
              </div>
              <div className="text-3xl sm:text-4xl md:text-5xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                {typeof result.half_life_ms === 'number' ? `${result.half_life_ms.toFixed(0)}ms` : result.half_life_ms}
              </div>
              <div className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'} mb-4`}>
                {result.insights.half_life_interpretation}
              </div>
              <div className={`inline-block px-4 py-2 rounded-full font-semibold ${getReliabilityColor(result.reliability.color)} bg-opacity-20`}>
                Reliability: {result.reliability.level}
              </div>
            </div>
          </div>

          {/* Key Latency Points */}
          <div className={`grid grid-cols-3 gap-3 sm:gap-5 p-4 sm:p-5 ${isDark ? 'bg-gray-900' : 'bg-gray-50'} rounded-lg`}>
            <div className="text-center">
              <div className={`text-lg sm:text-xl md:text-2xl font-bold ${isDark ? 'text-green-400' : 'text-green-600'}`}>
                {result.key_metrics.return_at_0ms.toFixed(3)}%
              </div>
              <div className="text-[11px] sm:text-xs mt-1">Return at 0ms</div>
              <div className={`text-[10px] sm:text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>(Instant)</div>
            </div>

            <div className="text-center">
              <div className={`text-lg sm:text-xl md:text-2xl font-bold ${isDark ? 'text-yellow-400' : 'text-yellow-600'}`}>
                {result.key_metrics.return_at_50ms.toFixed(3)}%
              </div>
              <div className="text-[11px] sm:text-xs mt-1">Return at 50ms</div>
              <div className={`text-[10px] sm:text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>(Fast)</div>
            </div>

            <div className="text-center">
              <div className={`text-lg sm:text-xl md:text-2xl font-bold ${isDark ? 'text-red-400' : 'text-red-600'}`}>
                {result.key_metrics.return_at_200ms.toFixed(3)}%
              </div>
              <div className="text-[11px] sm:text-xs mt-1">Return at 200ms</div>
              <div className={`text-[10px] sm:text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>(Slow)</div>
            </div>
          </div>

          {/* Insights */}
          <div className={`${isDark ? 'bg-gray-900' : 'bg-purple-50'} border ${isDark ? 'border-gray-700' : 'border-purple-200'} rounded-lg p-4`}>
            <h3 className="font-semibold mb-3">💡 Elite Insights</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-start gap-2">
                <span className="text-purple-500 font-bold">•</span>
                <span><strong>Competitive Pressure:</strong> {result.insights.competitive_pressure}</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-purple-500 font-bold">•</span>
                <span><strong>Execution Window:</strong> {result.insights.execution_window}</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-purple-500 font-bold">•</span>
                <span><strong>Return Decay (50ms):</strong> {result.insights.return_degradation_50ms}</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-purple-500 font-bold">•</span>
                <span><strong>Return Decay (200ms):</strong> {result.insights.return_degradation_200ms}</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-purple-500 font-bold">•</span>
                <span><strong>Expected @ 100ms:</strong> {result.key_metrics.expected_return_100ms.toFixed(3)}% 
                  (${result.key_metrics.expected_profit_100ms.toFixed(2)} profit)
                </span>
              </div>
            </div>
          </div>

          {/* Speed Requirements */}
          <div className={`${isDark ? 'bg-gray-900' : 'bg-blue-50'} border ${isDark ? 'border-gray-700' : 'border-blue-200'} rounded-lg p-4`}>
            <h3 className="font-semibold mb-2">⚡ Speed Requirements</h3>
            <p className="text-sm mb-2">{result.reliability.speed_requirement}</p>
            <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              {result.reliability.description}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default LatencySensitivityAnalysis;
