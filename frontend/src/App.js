import React, { useState, useEffect } from 'react';
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

  useEffect(() => {
    fetchMetrics();
    // Refresh metrics every 30 seconds
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Auto-refresh opportunities every 60 seconds if we have any
    if (opportunities.length > 0) {
      const interval = setInterval(() => {
        handleScan(true); // silent refresh (no loading state)
      }, 60000);
      return () => clearInterval(interval);
    }
  }, [opportunities.length]);

  const fetchMetrics = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.METRICS);
      const data = await response.json();
      if (data.success) {
        setMetrics(data);
      }
    } catch (err) {
      console.error('Failed to fetch metrics:', err);
    }
  };

  const handleScan = async (silentRefresh = false) => {
    if (!silentRefresh) {
      setLoading(true);
      setError(null);
      
      // Increment user's personal scan count
      const newCount = userScanCount + 1;
      setUserScanCount(newCount);
      localStorage.setItem('omniquant_scan_count', newCount.toString());
    }
    
    try {
      // Always use simulated data (fast and reliable)
      const apiUrl = `${API_ENDPOINTS.QUICK_SCAN}?use_real_data=false`;
      if (!silentRefresh) {
        console.log('Scanning with API:', apiUrl);
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
              {/* Scan Button */}
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
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
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
