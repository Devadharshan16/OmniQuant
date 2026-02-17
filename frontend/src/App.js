import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import OpportunityList from './components/OpportunityList';
import RiskPanel from './components/RiskPanel';
import MetricsPanel from './components/MetricsPanel';
import DisclaimerBanner from './components/DisclaimerBanner';

function App() {
  const [opportunities, setOpportunities] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMetrics();
    // Refresh metrics every 30 seconds
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8000/metrics');
      const data = await response.json();
      if (data.success) {
        setMetrics(data);
      }
    } catch (err) {
      console.error('Failed to fetch metrics:', err);
    }
  };

  const handleScan = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Example market data
      const scanData = {
        market_data: [
          { from_token: "BTC", to_token: "ETH", rate: 15.5, fee: 0.001, liquidity: 10000, exchange: "Exchange1" },
          { from_token: "ETH", to_token: "USDT", rate: 2500, fee: 0.001, liquidity: 50000, exchange: "Exchange2" },
          { from_token: "USDT", to_token: "BTC", rate: 0.000025, fee: 0.001, liquidity: 100000, exchange: "Exchange3" }
        ],
        capital: 1000.0,
        max_cycles: 10,
        run_monte_carlo: true,
        mc_simulations: 500
      };

      const response = await fetch('http://localhost:8000/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scanData)
      });

      const data = await response.json();
      
      if (data.success) {
        setOpportunities(data.opportunities || []);
        await fetchMetrics();
      } else {
        setError('Scan failed');
      }
    } catch (err) {
      setError('Failed to scan: ' + err.message);
    } finally {
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
            </div>
            <button
              onClick={handleScan}
              disabled={loading}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                loading
                  ? 'bg-gray-600 cursor-not-allowed'
                  : 'bg-cyan-600 hover:bg-cyan-700 shadow-lg hover:shadow-cyan-500/50'
              }`}
            >
              {loading ? 'Scanning...' : 'Scan Markets'}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 mb-6">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <MetricsPanel metrics={metrics} />
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
