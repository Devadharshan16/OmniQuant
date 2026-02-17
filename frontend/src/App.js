import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import OpportunityList from './components/OpportunityList';
import RiskPanel from './components/RiskPanel';
import MetricsPanel from './components/MetricsPanel';
import DisclaimerBanner from './components/DisclaimerBanner';
import ConnectionStatus from './components/ConnectionStatus';
import { API_ENDPOINTS } from './config';

function App() {
  const [opportunities, setOpportunities] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [userScanCount, setUserScanCount] = useState(() => {
    // Load user's personal scan count from localStorage
    return parseInt(localStorage.getItem('omniquant_scan_count') || '0', 10);
  });
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(false);
  const [loadingTime, setLoadingTime] = useState(0);

  // Timer for loading indicator
  useEffect(() => {
    let interval;
    if (loading) {
      setLoadingTime(0);
      interval = setInterval(() => {
        setLoadingTime(prev => prev + 1);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [loading]);

  const fetchMetrics = useCallback(async () => {
    try {
      const response = await fetch(API_ENDPOINTS.METRICS);
      const data = await response.json();
      if (data.success) {
        setMetrics(data);
      }
    } catch (err) {
      console.error('Failed to fetch metrics:', err);
    }
  }, []);

  const handleScan = useCallback(async (silentRefresh = false) => {
    if (!silentRefresh) {
      setLoading(true);
      setError(null);
      
      // Increment user's personal scan count
      const currentCount = parseInt(localStorage.getItem('omniquant_scan_count') || '0', 10);
      const newCount = currentCount + 1;
      setUserScanCount(newCount);
      localStorage.setItem('omniquant_scan_count', newCount.toString());
      
      // Enable auto-refresh after first manual scan
      setAutoRefreshEnabled(true);
    }
    
    try {
      // Fetch REAL-TIME data from cryptocurrency exchanges
      const apiUrl = `${API_ENDPOINTS.QUICK_SCAN}?use_real_data=true`;
      if (!silentRefresh) {
        console.log('🌐 Fetching real-time data from exchanges:', apiUrl);
      }
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      if (!silentRefresh) {
        console.log('Scan response:', data);
      }
      
      if (data.success) {
        setOpportunities(data.opportunities || []);
        if (!silentRefresh) {
          await fetchMetrics();
        }
      } else {
        if (!silentRefresh) {
          setError(data.error || 'Scan failed');
        }
      }
    } catch (err) {
      console.error('Scan error:', err);
      if (!silentRefresh) {
        setError(`Failed to scan: ${err.message}. Check if backend is running at ${API_ENDPOINTS.ROOT}`);
      }
    } finally {
      if (!silentRefresh) {
        setLoading(false);
      }
    }
  }, [fetchMetrics]);

  useEffect(() => {
    fetchMetrics();
    // Refresh metrics every 30 seconds
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, [fetchMetrics]);

  useEffect(() => {
    // Auto-refresh opportunities every 10 seconds after first scan
    if (autoRefreshEnabled) {
      console.log('🔄 Auto-refresh enabled: updating every 10 seconds');
      const interval = setInterval(() => {
        handleScan(true); // silent refresh
      }, 10000); // 10 seconds for real-time feel
      return () => clearInterval(interval);
    }
  }, [autoRefreshEnabled, handleScan]);

  return (
    <div className="App min-h-screen bg-gray-900 text-gray-100">
      <DisclaimerBanner />
      
      <header className="bg-gray-800 shadow-lg border-b border-cyan-500">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold text-cyan-400">
                OmniQuant <span className="text-gray-400">v2</span>
              </h1>
              <p className="text-gray-400 mt-1">
                Quantitative Market Inefficiency Research Platform
              </p>
              <ConnectionStatus />
            </div>
            <div className="flex items-center gap-4">
              {/* Scan Button */}
              <button
                onClick={handleScan}
                disabled={loading}
                className={`px-6 py-3 rounded-lg font-semibold transition-all flex items-center gap-2 ${
                  loading
                    ? 'bg-gray-600 cursor-not-allowed'
                    : 'bg-cyan-600 hover:bg-cyan-700 shadow-lg hover:shadow-cyan-500/50'
                }`}
              >
                {loading && (
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                )}
                {loading ? 'Fetching Real-Time Data...' : 'Scan Markets'}
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Loading Indicator */}
        {loading && (
          <div className="bg-gradient-to-r from-cyan-900/50 to-blue-900/50 border-2 border-cyan-500 rounded-lg p-6 mb-6 animate-pulse">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <svg className="animate-spin h-8 w-8 text-cyan-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <div>
                  <h3 className="text-xl font-bold text-cyan-400">🌐 Fetching Real-Time Market Data</h3>
                  <p className="text-gray-300 mt-1">
                    Connecting to Binance, Coinbase, Kraken, KuCoin...
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-cyan-400">{loadingTime}s</div>
                <div className="text-sm text-gray-400">Elapsed Time</div>
              </div>
            </div>
            <div className="mt-4 bg-gray-800 rounded-full h-2 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-cyan-500 to-blue-500 h-full transition-all duration-1000 ease-out"
                style={{ width: `${Math.min((loadingTime / 12) * 100, 100)}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-400 mt-2 text-center">
              First scan: ~25s (initializing connections) • Subsequent scans: ~11s (cached connections)
            </p>
          </div>
        )}
        
        {error && (
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 mb-6">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <MetricsPanel metrics={metrics} userScanCount={userScanCount} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <OpportunityList opportunities={opportunities} loading={loading} />
          </div>
          <div>
            <RiskPanel opportunities={opportunities} />
          </div>
        </div>
      </main>

      <footer className="bg-gray-800 border-t border-gray-700 mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-400">
          <p className="text-sm">
            Built for MIT/IIT Hackathon - Quantitative Finance Track
          </p>
          <p className="text-xs mt-2">
            Research tool. No trades executed. Not financial advice.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
