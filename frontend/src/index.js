import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// ============================================================
// CAPTURE beforeinstallprompt EARLY - before React even mounts
// Chrome fires this event ONCE after meeting engagement criteria.
// If React hasn't mounted its listener yet, we'd miss it forever.
// ============================================================
window.__deferredPrompt = null;
window.__promptCaptured = false;

window.addEventListener('beforeinstallprompt', (e) => {
  console.log('[PWA-EARLY] beforeinstallprompt captured before React mount!');
  e.preventDefault();
  window.__deferredPrompt = e;
  window.__promptCaptured = true;
  // Dispatch custom event so React components can react
  window.dispatchEvent(new CustomEvent('pwa-prompt-captured'));
});

window.addEventListener('appinstalled', () => {
  console.log('[PWA-EARLY] App installed!');
  window.__deferredPrompt = null;
  window.__promptCaptured = false;
  window.dispatchEvent(new CustomEvent('pwa-app-installed'));
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Register Service Worker for PWA functionality - PRODUCTION ONLY
// In dev mode, webpack dev server serves a new SW on every rebuild, causing reload loops
if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/service-worker.js')
      .then((registration) => {
        console.log('[PWA] Service Worker registered:', registration.scope);
        
        // Check for updates every 5 minutes (not too aggressive)
        setInterval(() => {
          registration.update();
        }, 300000);
      })
      .catch((error) => {
        console.error('[PWA] Service Worker registration failed:', error);
      });
  });
} else if ('serviceWorker' in navigator && process.env.NODE_ENV !== 'production') {
  // In development, unregister any existing service workers to prevent issues
  navigator.serviceWorker.getRegistrations().then((registrations) => {
    registrations.forEach((reg) => {
      reg.unregister();
      console.log('[PWA-DEV] Unregistered service worker to prevent reload loops');
    });
  });
}
