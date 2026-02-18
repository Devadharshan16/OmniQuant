import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import OpportunityList from './components/OpportunityList';
import RiskPanel from './components/RiskPanel';
import MetricsPanel from './components/MetricsPanel';
import ConnectionStatus from './components/ConnectionStatus';
import PWADebug from './components/PWADebug';
import MarketImpactCalculator from './components/MarketImpactCalculator';
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
  const [hasNativePrompt, setHasNativePrompt] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);
  const [showMobileBanner, setShowMobileBanner] = useState(false);
  const [bannerDismissed, setBannerDismissed] = useState(false);
  const [theme, setTheme] = useState(() => localStorage.getItem('omniquant_theme') || 'dark');
  const timerRef = useRef(null);
  const refreshRef = useRef(null);

  // Theme persistence
  useEffect(() => {
    localStorage.setItem('omniquant_theme', theme);
  }, [theme]);

  // PWA Install Prompt
  useEffect(() => {
    const standalone = window.matchMedia('(display-mode: standalone)').matches ||
                      window.navigator.standalone === true;
    setIsStandalone(standalone);

    if (standalone) {
      console.log('[PWA] Already running as installed app');
      return;
    }

    // Check if the early capture in index.js already got the prompt
    if (window.__deferredPrompt) {
      console.log('[PWA] Found early-captured install prompt!');
      setHasNativePrompt(true);
    }

    // Listen for future prompt captures (custom event from index.js)
    const handlePromptCaptured = () => {
      console.log('[PWA] Prompt captured event received');
      setHasNativePrompt(true);
    };

    const handleAppInstalled = () => {
      console.log('[PWA] App was installed successfully!');
      setIsStandalone(true);
      setShowMobileBanner(false);
    };

    // Also listen for the native event as backup
    const handleBeforeInstallPrompt = (e) => {
      console.log('[PWA] beforeinstallprompt in React - captured!');
      e.preventDefault();
      window.__deferredPrompt = e;
      window.__promptCaptured = true;
      setHasNativePrompt(true);
    };

    window.addEventListener('pwa-prompt-captured', handlePromptCaptured);
    window.addEventListener('pwa-app-installed', handleAppInstalled);
    window.addEventListener('appinstalled', handleAppInstalled);
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // Show mobile install banner after 3 seconds on mobile devices
    const isMobile = /Android|iPhone|iPad|iPod|webOS|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    let mobileTimer;
    if (isMobile && !bannerDismissed) {
      mobileTimer = setTimeout(() => {
        if (!window.matchMedia('(display-mode: standalone)').matches) {
          setShowMobileBanner(true);
        }
      }, 3000);
    }

    return () => {
      if (mobileTimer) clearTimeout(mobileTimer);
      window.removeEventListener('pwa-prompt-captured', handlePromptCaptured);
      window.removeEventListener('pwa-app-installed', handleAppInstalled);
      window.removeEventListener('appinstalled', handleAppInstalled);
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, [bannerDismissed]);

  const handleInstallClick = async () => {
    // Always re-check for the early-captured prompt
    const prompt = window.__deferredPrompt;

    if (prompt) {
      console.log('[PWA] Triggering native install prompt');
      try {
        prompt.prompt();
        const { outcome } = await prompt.userChoice;
        console.log('[PWA] User ' + (outcome === 'accepted' ? 'accepted' : 'dismissed') + ' install');
        if (outcome === 'accepted') {
          setIsStandalone(true);
          setShowMobileBanner(false);
        }
      } catch (err) {
        console.log('[PWA] Prompt error:', err);
      }
      window.__deferredPrompt = null;
      setHasNativePrompt(false);
    } else {
      // No native prompt - guide user to browser's built-in install
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      const isAndroid = /Android/.test(navigator.userAgent);
      const isChrome = /Chrome/.test(navigator.userAgent) && !/Edg/.test(navigator.userAgent);
      const isEdge = /Edg/.test(navigator.userAgent);
      const isSamsung = /SamsungBrowser/.test(navigator.userAgent);

      let message = 'To install OmniQuant as an app:\n\n';

      if (isIOS) {
        message += '1. Tap the Share button at the bottom (square with arrow up)\n';
        message += '2. Scroll down and tap "Add to Home Screen"\n';
        message += '3. Tap "Add" in the top right\n\n';
        message += 'The app will appear on your home screen!';
      } else if (isAndroid && isSamsung) {
        message += '1. Tap the menu icon in the bottom right\n';
        message += '2. Tap "Add page to" then "Home screen"\n';
        message += '3. Tap "Add"';
      } else if (isAndroid) {
        message += '1. Tap the three-dot menu in the top right\n';
        message += '2. Look for "Install app" or "Add to Home screen"\n';
        message += '3. Tap "Install"\n\n';
        message += 'If you don\'t see "Install app", try:\n';
        message += '- Refreshing the page first\n';
        message += '- Waiting 30 seconds then checking the menu again\n';
        message += '- Chrome needs you to browse the site briefly before offering install';
      } else if (isEdge) {
        message += '1. Look for the app install icon in the address bar\n';
        message += '2. Or click ... menu > Apps > Install this site as an app\n';
        message += '3. Click "Install"';
      } else if (isChrome) {
        message += '1. Look for the install icon in the address bar (right side)\n';
        message += '2. Or click ... menu > "Install OmniQuant..."\n';
        message += '3. Click "Install" in the dialog\n\n';
        message += 'If you don\'t see it, try refreshing and waiting a moment.';
      } else {
        message += '1. Look for an install option in your browser\'s menu\n';
        message += '2. Or check the address bar for an install icon';
      }

      alert(message);
    }
  };

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
    setLoading(true);
    setError(null);
    setLoadingTime(0);

    let seconds = 0;
    timerRef.current = setInterval(() => {
      seconds += 1;
      setLoadingTime(seconds);
    }, 1000);

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
      clearInterval(timerRef.current);
      setLoading(false);
    }
  };

  return (
    <div className={`App min-h-screen bg-gray-900 text-gray-100${theme === 'light' ? ' light' : ''}`}>

      <header className="header-accent bg-gray-900/80 backdrop-blur-md shadow-2xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5 sm:py-6">
          <div className="flex justify-between items-center">
            <div className="min-w-0 flex-shrink">
              <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
                OmniQuant
              </h1>
              <p className="text-gray-500 mt-1 text-xs sm:text-sm font-medium tracking-wide truncate">
                Quantitative Market Inefficiency Research Platform
              </p>
              <div className="mt-1"><ConnectionStatus /></div>
            </div>
            <div className="flex items-center gap-2 sm:gap-4 flex-shrink-0 ml-2">
              {/* Theme toggle */}
              <button
                onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
                className="theme-toggle"
                title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
                aria-label="Toggle theme"
              >
                {theme === 'dark' ? (
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
                ) : (
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>
                )}
              </button>
              {/* Install button - always visible when not standalone */}
              {!isStandalone && (
                <button
                  onClick={handleInstallClick}
                  className={`px-3 sm:px-4 py-2 rounded-xl font-semibold shadow-lg transition-all duration-300 flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm whitespace-nowrap border ${
                    hasNativePrompt
                      ? 'bg-emerald-500/90 hover:bg-emerald-400 border-emerald-400/50 shadow-emerald-500/25 animate-pulse'
                      : 'bg-emerald-600/80 hover:bg-emerald-500 border-emerald-500/30 hover:shadow-emerald-500/20'
                  }`}
                  title="Install OmniQuant as an app"
                >
                  <svg className="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  <span className="hidden sm:inline">{hasNativePrompt ? 'Install App' : 'Get App'}</span>
                  <span className="sm:hidden">{hasNativePrompt ? 'Install' : 'Get'}</span>
                </button>
              )}
              <button
                onClick={doScan}
                disabled={loading}
                className={`px-4 sm:px-6 py-2.5 sm:py-3 rounded-xl font-semibold transition-all duration-300 flex items-center gap-2 text-sm sm:text-base border ${
                  loading
                    ? 'bg-gray-700/80 border-gray-600 cursor-not-allowed animate-pulse'
                    : 'bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 border-cyan-500/30 shadow-lg shadow-cyan-500/20 hover:shadow-cyan-400/40 hover:-translate-y-0.5'
                }`}
              >
                {loading && (
                  <svg className="animate-spin h-4 w-4 sm:h-5 sm:w-5" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                )}
                <span className="hidden sm:inline">{loading ? `Fetching Live Data... ${loadingTime}s` : 'Scan Markets'}</span>
                <span className="sm:hidden">{loading ? `${loadingTime}s` : 'Scan'}</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* ======= LOADING INDICATOR ======= */}
        {loading && (
          <div className="border border-cyan-500/30 rounded-2xl p-6 mb-6 bg-gray-800/60 backdrop-blur-sm shadow-lg shadow-cyan-500/10">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="relative">
                  <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin"></div>
                  <div className="absolute inset-0 w-12 h-12 border-4 border-transparent border-b-blue-500/40 rounded-full animate-spin" style={{animationDirection: 'reverse', animationDuration: '1.5s'}}></div>
                </div>
                <div>
                  <h3 className="text-lg sm:text-xl font-bold text-cyan-300">
                    Fetching Real-Time Market Data
                  </h3>
                  <p className="text-gray-400 mt-1 text-sm">
                    Connecting to Coinbase, Kraken, KuCoin...
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-3xl sm:text-4xl font-mono font-bold text-cyan-400 glow-text">{loadingTime}s</div>
                <div className="text-xs text-gray-500 uppercase tracking-wider">Elapsed</div>
              </div>
            </div>
            <div className="mt-4 bg-gray-700/60 rounded-full h-2.5 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-1000 progress-shimmer"
                style={{ width: `${Math.min((loadingTime / 15) * 100, 95)}%`, background: 'linear-gradient(90deg, #06b6d4, #3b82f6, #06b6d4)' }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-2.5 text-center tracking-wide">
              First scan ~25s (initializing) · Subsequent ~11s (cached)
            </p>
          </div>
        )}

        {error && (
          <div className="bg-red-900/30 border border-red-500/40 rounded-xl p-4 mb-6 backdrop-blur-sm">
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-3 gap-4 sm:gap-5 mb-8">
          <MetricsPanel metrics={metrics} userScanCount={scanCount} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 sm:gap-6">
          <div className="lg:col-span-2">
            <OpportunityList opportunities={opportunities} loading={loading} />
          </div>
          <div>
            <RiskPanel opportunities={opportunities} />
          </div>
        </div>

        {/* Market Impact Calculator Section */}
        <div className="mt-8">
          <MarketImpactCalculator theme={theme} />
        </div>
      </main>

      {/* Mobile Install Banner - sticky bottom bar on mobile */}
      {showMobileBanner && !isStandalone && !bannerDismissed && (
        <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-r from-emerald-600/95 to-cyan-600/95 text-white p-4 shadow-2xl z-50 sm:hidden backdrop-blur-md border-t border-white/10">
          <div className="flex items-center justify-between max-w-lg mx-auto">
            <div className="flex items-center gap-3">
              <div className="bg-white/15 rounded-xl p-2.5">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </div>
              <div>
                <div className="font-bold text-sm tracking-tight">Install OmniQuant</div>
                <div className="text-xs opacity-75">Quick access from home screen</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleInstallClick}
                className="bg-white text-emerald-700 px-4 py-2 rounded-xl font-bold text-sm shadow-lg"
              >
                Install
              </button>
              <button
                onClick={() => { setShowMobileBanner(false); setBannerDismissed(true); }}
                className="text-white/70 hover:text-white p-1"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}

      <PWADebug />
    </div>
  );
}

export default App;
