# PWA Deployment Troubleshooting for Render

## Why PWA Install Prompt Works on Localhost but Not on Render

### Common Issues and Solutions

#### 1. **Service Worker Not at Root Level**
**Problem:** Service worker must be served from the root of your domain (`/service-worker.js`), not from a subdirectory.

**Solution:** ✅ Fixed with `postbuild.js` script that copies `service-worker.js` to the build folder root during build.

#### 2. **Incorrect Caching Headers**
**Problem:** Service workers should have `Cache-Control: no-cache` to ensure updates are detected immediately.

**Solution:** ✅ Added to `render.yaml`:
```yaml
- path: /service-worker.js
  name: Cache-Control
  value: no-cache, no-store, must-revalidate
```

#### 3. **Missing PWA Criteria**
**Problem:** Browser requires all PWA criteria to be met before showing install prompt:
- ✅ HTTPS (Render provides this automatically)
- ✅ Valid manifest.json with icons
- ✅ Service worker registered
- ✅ Service worker has fetch event handler
- ✅ Not already installed

#### 4. **Icons Not Found**
**Problem:** PNG icons (192x192 and 512x512) are required for install prompt.

**Solution:** Make sure you generated and added:
- `frontend/public/icon-192.png`
- `frontend/public/icon-512.png`

These are automatically included in the build.

## Deployment Checklist

Before deploying to Render, ensure:

- [ ] Icons generated (`icon-192.png` and `icon-512.png` in `public/` folder)
- [ ] Build command includes postbuild script: `npm run build` (runs `postbuild.js` automatically)
- [ ] `render.yaml` has correct headers for service worker
- [ ] REACT_APP_API_URL environment variable is set correctly on Render

## Testing PWA on Render

### 1. Deploy to Render
```bash
git add -A
git commit -m "Add PWA support"
git push origin main
```

### 2. Check Service Worker Registration
1. Open your Render URL (e.g., `https://omniquant-frontend.onrender.com`)
2. Open DevTools → Console
3. Look for: `[PWA] Service Worker registered: https://omniquant-frontend.onrender.com/`

### 3. Verify PWA Criteria
Open DevTools → Lighthouse → Progressive Web App
- Run audit
- Should score 100% or close to it
- Check "Installable" section

### 4. Check Manifest
Open DevTools → Application → Manifest
- Should show OmniQuant manifest data
- Icons should be visible
- No errors

### 5. Check Service Worker
Open DevTools → Application → Service Workers
- Should show "activated and running"
- Source should be `/service-worker.js`

### 6. Test Install Prompt
**Chrome/Edge Desktop:**
- Look for "Install App" button in header
- Or look for install icon (⊕) in address bar

**Chrome Mobile:**
- Should show banner or "Add to Home Screen" option
- Or use "Install App" button in header

## Common Deployment Issues

### Install Button Still Not Showing

**Check 1: Is Service Worker Active?**
```
DevTools → Application → Service Workers
Status should be "activated and running"
```

**Check 2: Are Icons Loading?**
```
DevTools → Network → Filter by "icon"
Both icon-192.png and icon-512.png should return 200 OK
```

**Check 3: Is Manifest Valid?**
```
DevTools → Application → Manifest
Should show no errors
```

**Check 4: Already Installed?**
If you previously installed the app, uninstall it first:
- Chrome: chrome://apps → Right-click OmniQuant → Remove
- Desktop: Uninstall from OS app list

**Check 5: Browser Support**
The install prompt works best on:
- Chrome/Edge (Desktop & Mobile) ✅
- Safari iOS 16.4+ ✅
- Firefox Android ✅

Safari Desktop (macOS) doesn't show install prompts but the app still works as PWA.

### Service Worker Not Updating

If you make changes to the service worker:
1. Increment version in `CACHE_NAME` (e.g., `v1` → `v2`)
2. Deploy
3. Hard refresh (Ctrl+Shift+R) or clear site data
4. The new service worker should take over

### Icons Not Loading (404)

If icons return 404:
1. Check they exist: `frontend/public/icon-192.png` and `icon-512.png`
2. Rebuild: `cd frontend && npm run build`
3. Check build output: Icons should be in `frontend/build/`
4. Redeploy to Render

## Render-Specific Configuration

### Environment Variables
Render should have:
```
REACT_APP_API_URL = https://omniquant-api.onrender.com
```

### Build Command
```
cd frontend && npm install && npm run build
```

The `npm run build` automatically runs `postbuild.js` which copies PWA files.

### Static Publish Path
```
./frontend/build
```

## Viewing Logs on Render

To debug build issues:
1. Go to Render dashboard
2. Select `omniquant-frontend` service
3. Click "Logs"
4. Look for `postbuild.js` output:
   ```
   ✓ Copied public/service-worker.js to build/service-worker.js
   ✓ Copied public/manifest.json to build/manifest.json
   ✓ PWA files copied to build folder
   ```

## Success Indicators

When PWA is working correctly on Render:

✅ Service worker shows in DevTools as "activated"
✅ Lighthouse PWA score >90
✅ Install button appears in header (if not already installed)
✅ Can install app using browser's install option
✅ Installed app opens in standalone window
✅ App icon appears on desktop/home screen

## Still Having Issues?

1. Check browser console for errors
2. Run Lighthouse PWA audit
3. Verify all files are being served correctly (Network tab)
4. Try in different browser (Chrome works best for testing)
5. Clear browser cache and try again

## Alternative: Force Install Prompt

If automatic detection isn't working, the "Install App" button in the header will always work when:
- PWA criteria are met
- App is not already installed
- Browser supports PWA installation

The button uses the `beforeinstallprompt` event which has wider support than automatic prompts.
