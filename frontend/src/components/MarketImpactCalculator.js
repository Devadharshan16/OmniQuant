import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_ENDPOINTS } from '../config';

function MarketImpactCalculator({ theme }) {
  const [volume, setVolume] = useState(10000);
  const [liquidity, setLiquidity] = useState(100000);
  const [k, setK] = useState(0.5);
  const [alpha, setAlpha] = useState(1.5);
  const [basePrice, setBasePrice] = useState(100);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [autoUpdate, setAutoUpdate] = useState(true);

  const calculateImpact = async () => {
    setLoading(true);
    try {
      const response = await axios.post(API_ENDPOINTS.MARKET_IMPACT, {
        volume: parseFloat(volume),
        liquidity: parseFloat(liquidity),
        base_price: parseFloat(basePrice),
        k: parseFloat(k),
        alpha: parseFloat(alpha),
        volatility: 0.01
      });

      if (response.data.success) {
        setResult(response.data);
      }
    } catch (error) {
      console.error('Error calculating market impact:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (autoUpdate) {
      calculateImpact();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [volume, liquidity, k, alpha, basePrice, autoUpdate]);

  const isDark = theme === 'dark';
  const bgClass = isDark ? 'bg-gray-800' : 'bg-white';
  const textClass = isDark ? 'text-gray-100' : 'text-gray-900';
  const borderClass = isDark ? 'border-gray-700' : 'border-gray-300';
  const inputBg = isDark ? 'bg-gray-700' : 'bg-gray-50';

  return (
    <div className={`${bgClass} ${textClass} rounded-lg shadow-lg p-4 sm:p-6 border ${borderClass}`}>
      <div className="mb-4 sm:mb-6">
        <h2 className="text-xl sm:text-2xl font-bold mb-2">
          🎯 Nonlinear Market Impact Calculator
        </h2>
        <p className={`text-xs sm:text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'} mb-3`}>
          Institutional-grade slippage model with convex impact
        </p>
        <div className={`${isDark ? 'bg-gray-900' : 'bg-blue-50'} border ${isDark ? 'border-gray-700' : 'border-blue-200'} rounded-lg p-4`}>
          <div className="font-mono text-lg text-center">
            <span className={isDark ? 'text-blue-400' : 'text-blue-600'}>impact</span>
            {' = '}
            <span className={isDark ? 'text-green-400' : 'text-green-600'}>k</span>
            {' × ('}
            <span className={isDark ? 'text-yellow-400' : 'text-yellow-600'}>volume</span>
            {' / '}
            <span className={isDark ? 'text-purple-400' : 'text-purple-600'}>liquidity</span>
            {')'}
            <sup className={isDark ? 'text-pink-400' : 'text-pink-600'}>α</sup>
          </div>
          <p className={`text-xs text-center mt-2 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            α &gt; 1 creates convex impact (larger trades have disproportionate impact)
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 mb-4 sm:mb-6">
        <div>
          <label className="block text-sm font-medium mb-2">
            Trade Volume
          </label>
          <input
            type="number"
            value={volume}
            onChange={(e) => setVolume(e.target.value)}
            className={`w-full px-3 py-2 ${inputBg} border ${borderClass} rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
            min="0"
            step="1000"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Available Liquidity
          </label>
          <input
            type="number"
            value={liquidity}
            onChange={(e) => setLiquidity(e.target.value)}
            className={`w-full px-3 py-2 ${inputBg} border ${borderClass} rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
            min="0"
            step="10000"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Base Price ($)
          </label>
          <input
            type="number"
            value={basePrice}
            onChange={(e) => setBasePrice(e.target.value)}
            className={`w-full px-3 py-2 ${inputBg} border ${borderClass} rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
            min="0"
            step="10"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Utilization: {((volume / liquidity) * 100).toFixed(2)}%
          </label>
          <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
            <div
              className={`h-2.5 rounded-full ${
                (volume / liquidity) > 0.5 ? 'bg-red-600' :
                (volume / liquidity) > 0.2 ? 'bg-yellow-500' : 'bg-green-600'
              }`}
              style={{ width: `${Math.min((volume / liquidity) * 100, 100)}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 mb-4 sm:mb-6">
        <div>
          <label className="block text-sm font-medium mb-2">
            k (Sensitivity Constant)
          </label>
          <input
            type="range"
            value={k}
            onChange={(e) => setK(e.target.value)}
            className="w-full"
            min="0.1"
            max="2"
            step="0.1"
          />
          <div className="text-center text-sm font-mono">{k}</div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            α (Impact Exponent)
          </label>
          <input
            type="range"
            value={alpha}
            onChange={(e) => setAlpha(e.target.value)}
            className="w-full"
            min="1.0"
            max="3.0"
            step="0.1"
          />
          <div className="text-center text-sm font-mono">{alpha}</div>
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
            onClick={calculateImpact}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Calculating...' : 'Calculate Impact'}
          </button>
        )}
      </div>

      {result && result.results && (
        <div className="space-y-4 sm:space-y-5">
          <div className={`grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-5 p-4 sm:p-5 ${isDark ? 'bg-gray-900' : 'bg-gray-50'} rounded-lg`}>
            <div className="text-center">
              <div className={`text-lg sm:text-xl md:text-2xl font-bold ${isDark ? 'text-blue-400' : 'text-blue-600'}`}>
                {result.results.impact_pct.toFixed(4)}%
              </div>
              <div className="text-[11px] sm:text-xs mt-1">Market Impact</div>
            </div>

            <div className="text-center">
              <div className={`text-lg sm:text-xl md:text-2xl font-bold ${isDark ? 'text-green-400' : 'text-green-600'}`}>
                {result.results.impact_bps.toFixed(2)}
              </div>
              <div className="text-[11px] sm:text-xs mt-1">Basis Points</div>
            </div>

            <div className="text-center">
              <div className={`text-lg sm:text-xl md:text-2xl font-bold ${isDark ? 'text-yellow-400' : 'text-yellow-600'}`}>
                ${result.results.impacted_price.toFixed(4)}
              </div>
              <div className="text-[11px] sm:text-xs mt-1">Effective Price</div>
            </div>

            <div className="text-center">
              <div className={`text-lg sm:text-xl md:text-2xl font-bold ${isDark ? 'text-red-400' : 'text-red-600'}`}>
                +${result.results.price_increase.toFixed(4)}
              </div>
              <div className="text-[11px] sm:text-xs mt-1">Price Increase</div>
            </div>
          </div>

          <div className={`${isDark ? 'bg-gray-900' : 'bg-blue-50'} border ${isDark ? 'border-gray-700' : 'border-blue-200'} rounded-lg p-4`}>
            <h3 className="font-semibold mb-2">💡 Institutional Insights</h3>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>{result.interpretation.convexity}</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>{result.interpretation.institutional_insight}</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>{result.interpretation.execution_cost}</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Liquidity Utilization: {result.results.liquidity_utilization_pct.toFixed(2)}%</span>
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default MarketImpactCalculator;
