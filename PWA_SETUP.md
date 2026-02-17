# OmniQuant PWA Setup

## Progressive Web App Features

OmniQuant is now installable as a Progressive Web App (PWA)! This allows users to:

- 📱 Install on mobile home screen (iOS/Android)
- 💻 Install as desktop app (Chrome, Edge, Safari)
- 🚀 Faster loading with service worker caching
- 📡 Offline support (view cached data when offline)
- 🔔 Native app-like experience

## Quick Setup Instructions

### 1. Generate Icons

The icons need to be generated once. Follow these steps:

**Option A: Using the Browser Generator (Recommended)**
1. Open `public/generate-icons.html` in your browser
2. Click "Download 192x192 Icon" and save as `icon-192.png` in the `public/` folder
3. Click "Download 512x512 Icon" and save as `icon-512.png` in the `public/` folder

**Option B: Use the SVG temporarily**
The app will work with the SVG icon (`icon.svg`) for testing, but PNG icons are recommended for better compatibility.

### 2. Start the App

```bash
cd frontend
npm start
```

### 3. Test PWA Installation

**Desktop (Chrome/Edge):**
- Click the "Install App" button in the header (appears automatically)
- Or click the install icon in the address bar
- App will open in its own window

**Mobile (Chrome/Safari):**
- Open the site on your phone
- Android Chrome: Tap "Install App" button or "Add to Home Screen" from menu
- iOS Safari: Tap Share → "Add to Home Screen"

**Deployed (Production):**
PWA requires HTTPS in production. On Render.com, this is automatic:
- Deploy to Render
- Visit the HTTPS URL
- Install prompt will appear automatically

## Files Created

```
frontend/
├── public/
│   ├── manifest.json          # PWA manifest (app metadata)
│   ├── service-worker.js      # Service worker (caching & offline)
│   ├── icon.svg              # Vector icon source
│   ├── icon-192.png          # App icon 192x192 (generate this)
│   ├── icon-512.png          # App icon 512x512 (generate this)
│   └── generate-icons.html   # Icon generator tool
└── src/
    ├── index.js              # Service worker registration
    └── App.js                # Install prompt UI

```

## How It Works

### Service Worker
- Caches app assets for instant loading
- Caches API responses for offline viewing
- Network-first strategy for API calls
- Cache-first strategy for static assets

### Install Prompt
- Shows "Install App" button when available
- Hides automatically if already installed
- Detects standalone mode (running as installed app)

### Offline Support
- View previously loaded data when offline
- App shell loads instantly from cache
- Shows "offline" indicator when API unavailable

## Testing

### Check Service Worker
1. Open DevTools → Application tab
2. Service Workers section should show "activated and running"
3. Cache Storage should show `omniquant-v2-cache-v1`

### Test Offline
1. Open DevTools → Network tab
2. Change throttling to "Offline"
3. Refresh page - should still load
4. Previously scanned data should be visible

### Test Installation
1. Look for "Install App" button in header
2. Click to install
3. App opens in standalone window
4. Check if it appears in your OS app list

## Deployment Notes

**Render.com:**
- Automatic HTTPS ✅
- Service worker works automatically ✅
- Users will see install prompt on first visit

**Requirements:**
- HTTPS (localhost or production)
- Valid manifest.json
- Service worker registered
- Icons in correct sizes

## Troubleshooting

**Install button not showing:**
- Check if already installed (standalone mode)
- PWA requires HTTPS (except localhost)
- Try in Chrome/Edge (best PWA support)

**Service worker not registering:**
- Check browser console for errors
- Ensure service-worker.js is in public/ folder
- Clear browser cache and reload

**Icons not loading:**
- Generate icon-192.png and icon-512.png
- Place in public/ folder
- Clear cache and reload

## Browser Support

✅ Chrome/Edge (Desktop & Mobile) - Full support
✅ Safari (iOS 11.3+) - Full support
✅ Firefox (Desktop & Mobile) - Partial support
⚠️ Safari (Desktop macOS) - Limited (no install, but service worker works)

## Next Steps

1. Generate the PNG icons using `generate-icons.html`
2. Test locally at http://localhost:3000
3. Deploy to Render.com for HTTPS
4. Share with users - they can install with one click!

---

**Note:** The app is fully functional as a regular web app. PWA installation is optional but provides a better user experience.
