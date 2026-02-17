import React, { useState, useEffect } from 'react';

function PWADebug() {
  const [pwaStatus, setPwaStatus] = useState({
    https: false,
    serviceWorker: false,
    manifest: false,
    standalone: false,
    beforeInstallPrompt: false
  });
  const [showDebug, setShowDebug] = useState(false);

  useEffect(() => {
    const checkPWAStatus = async () => {
      const status = {
        https: window.location.protocol === 'https:' || window.location.hostname === 'localhost',
        serviceWorker: 'serviceWorker' in navigator,
        manifest: document.querySelector('link[rel="manifest"]') !== null,
        standalone: window.matchMedia('(display-mode: standalone)').matches,
        beforeInstallPrompt: window.__promptCaptured === true
      };

      // Check service worker registration
      if (status.serviceWorker) {
        try {
          const registration = await navigator.serviceWorker.getRegistration();
          status.serviceWorkerActive = registration && registration.active !== null;
        } catch (e) {
          status.serviceWorkerActive = false;
        }
      }

      setPwaStatus(status);
    };

    checkPWAStatus();

    // Re-check when prompt is captured
    const handlePromptCaptured = () => {
      setPwaStatus(prev => ({ ...prev, beforeInstallPrompt: true }));
    };

    const handleBeforeInstallPrompt = () => {
      setPwaStatus(prev => ({ ...prev, beforeInstallPrompt: true }));
    };

    window.addEventListener('pwa-prompt-captured', handlePromptCaptured);
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // Periodically re-check (prompt may arrive later due to engagement heuristics)
    const interval = setInterval(() => {
      if (window.__promptCaptured) {
        setPwaStatus(prev => ({ ...prev, beforeInstallPrompt: true }));
      }
    }, 5000);

    return () => {
      window.removeEventListener('pwa-prompt-captured', handlePromptCaptured);
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      clearInterval(interval);
    };
  }, []);

  // Only show in development or when debugging
  if (!showDebug && process.env.NODE_ENV === 'production') {
    return (
      <button
        onClick={() => setShowDebug(true)}
        className="fixed bottom-4 right-4 bg-gray-700 text-gray-300 px-3 py-1 rounded text-xs opacity-50 hover:opacity-100"
        title="Show PWA Debug Info"
      >
        PWA
      </button>
    );
  }

  if (!showDebug) return null;

  return (
    <div className="fixed bottom-4 right-4 bg-gray-800 border border-cyan-500 rounded-lg p-4 text-sm shadow-2xl max-w-sm z-50">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-bold text-cyan-400">PWA Status</h3>
        <button
          onClick={() => setShowDebug(false)}
          className="text-gray-400 hover:text-white"
        >
          ✕
        </button>
      </div>
      
      <div className="space-y-2">
        <StatusItem label="HTTPS" status={pwaStatus.https} />
        <StatusItem label="Service Worker API" status={pwaStatus.serviceWorker} />
        <StatusItem label="Service Worker Active" status={pwaStatus.serviceWorkerActive} />
        <StatusItem label="Manifest Linked" status={pwaStatus.manifest} />
        <StatusItem label="Running Standalone" status={pwaStatus.standalone} />
        <StatusItem label="Install Prompt Ready" status={pwaStatus.beforeInstallPrompt} />
      </div>

      <div className="mt-4 pt-3 border-t border-gray-700">
        <div className="text-xs text-gray-400">
          <div>Protocol: {window.location.protocol}</div>
          <div>Host: {window.location.hostname}</div>
          <div>
            Display Mode: {window.matchMedia('(display-mode: standalone)').matches ? 'Standalone' : 'Browser'}
          </div>
        </div>
      </div>

      {!pwaStatus.https && (
        <div className="mt-3 text-xs text-yellow-400">
          ⚠️ PWA requires HTTPS (or localhost)
        </div>
      )}
      
      {pwaStatus.https && !pwaStatus.beforeInstallPrompt && (
        <div className="mt-3 text-xs text-gray-400">
          ℹ️ Install prompt may be blocked if:
          <ul className="list-disc ml-4 mt-1">
            <li>App already installed</li>
            <li>Service worker not registered</li>
            <li>Manifest invalid</li>
            <li>Browser doesn't support PWA</li>
          </ul>
        </div>
      )}
    </div>
  );
}

function StatusItem({ label, status }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-gray-300">{label}</span>
      <span className={`${status ? 'text-green-400' : 'text-red-400'} font-mono`}>
        {status ? '✓' : '✗'}
      </span>
    </div>
  );
}

export default PWADebug;
