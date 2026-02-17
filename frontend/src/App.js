import React, { useState, useEffect, useRef } from 'react';
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
  const [loadingTime, setLoadingTime] = useState(0);
  const [scanCount, setScanCount] = useState(() => {
    return parseInt(localStorage.getItem('omniquant_scan_count') || '0', 10);
  });
  const [hasScanned, setHasScanned] = useState(false);
  const timerRef = useRef(null);
  const refreshRef = useRef(null);

  // Fetch metrics
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch(API_ENDPOINTS.METRICS);
        const data = await res.json();
        if (data.success) setMetrics(data);
      } catch (e) { /* ignore */ }
    };
    fetchMetrics();
    const id = setInterval(fetchMetrics, 30000);
    return () => clearInterval(id);
  }, []);

  // Auto-refresh every 15 seconds after first scan
  useEffect(() => {
    if (hasScanned) {
      refreshRef.current = setInterval(async () => {
        try {
          const res = await fetch(`${API_ENDPOINTS.QUICK_SCAN}?use_real_data=true`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
          });
          const data = await res.json();
          if (data.success) {
            setOpportunities(data.opportunities || []);
          }
        } catch (e) { /* silent */ }
      }, 15000);
      return () => clearInterval(refreshRef.current);
    }
  }, [hasScanned]);

  // Manual scan with full loading UI
  const doScan = async () => {
    // START LOADING
    setLoading(true);
    setError(null);
    setLoadingTime(0);

    // Start timer
    let seconds = 0;
    timerRef.current = setInterval(() => {
      seconds += 1;
      setLoadingTime(seconds);
    }, 1000);

    // Update scan count
    const newCount = scanCount + 1;
    setScanCount(newCount);
    localStorage.setItem('omniquant_scan_count', String(newCount));

    try {
      const res = await fetch(`${API_ENDPOINTS.QUICK_SCAN}?use_real_data=true`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!res.ok) throw new Error(`API error: ${res.status}`);

      const data = await res.json();
      if (data.success) {
        setOpportunities(data.opportunities || []);
        setHasScanned(true);
      } else {
        setError(data.error || 'Scan failed');
      }
    } catch (err) {
      setError(`Failed to scan: ${err.message}`);
    } finally {
      // STOP LOADING
      clearInterval(timerRef.current);
      setLoading(false);
    }
  };

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
              <button
                onClick={doScan}
                disabled={loading}
                className={`px-6 py-3 rounded-lg font-semibold transition-all flex items-center gap-2 ${
                  loading
                    ? 'bg-gray-600 cursor-not-allowed animate-pulse'
                    : 'bg-cyan-600 hover:bg-cyan-700 shadow-lg hover:shadow-cyan-500/50'
                }`}
              >
                {loading && (
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                )}
                {loading ? `Fetching Live Data... ${loadingTime}s` : 'Scan Markets'}
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* ======= LOADING INDICATOR ======= */}
        {loading && (
          <div className="border-2 border-cyan-500 rounded-lg p-6 mb-6 bg-gray-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="relative">
                  <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-cyan-400">
                    🌐 Fetching Real-Time Market Data
                  </h3>
                  <p className="text-gray-300 mt-1">
                    Connecting to Binance, Coinbase, Kraken, KuCoin...
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-4xl font-mono font-bold text-cyan-400">{loadingTime}s</div>
                <div className="text-sm text-gray-400">Elapsed</div>
              </div>
            </div>
            <div className="mt-4 bg-gray-700 rounded-full h-3 overflow-hidden">
              <div 
                className="bg-cyan-500 h-full rounded-full transition-all duration-1000"
                style={{ width: `${Math.min((loadingTime / 15) * 100, 95)}%` }}
              />
            </div>
            <p className="text-xs text-gray-400 mt-2 text-center">
              First scan ~25s (initializing) • Subsequent ~11s (cached)
            </p>
          </div>
        )}

        {error && (
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 mb-6">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <MetricsPanel metrics={metrics} userScanCount={scanCount} />
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
