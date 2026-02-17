# OmniQuant Frontend - Deployment Notes

## ⚠️ CRITICAL: Environment Variables

For the frontend to connect to the backend, you MUST set:

```bash
REACT_APP_API_URL=https://your-backend-url.onrender.com
```

### On Render:
1. Go to Static Site settings
2. Environment tab
3. Add environment variable:
   - Key: `REACT_APP_API_URL`
   - Value: Your backend URL (e.g., `https://omniquant-api.onrender.com`)
4. Trigger redeploy

### Local Development:
```bash
# Create .env.local file:
REACT_APP_API_URL=http://localhost:8000

# Then run:
npm start
```

## Debugging Connection Issues

Open browser console (F12) and look for:
```
OmniQuant API Configuration:
  Environment: production
  API Base URL: https://...
```

If it shows `localhost:8000` in production, the env var is not set correctly.

## Configuration Files

- `.env.production` - Default production API URL (template)
- `src/config.js` - API endpoint configuration with fallbacks
- `src/components/ConnectionStatus.js` - Shows API connection status in UI

## Features

- ✅ Always uses simulated data (fast, reliable)
- ✅ No real-time data toggle (removed for simplicity)
- ✅ Connection status indicator in header
- ✅ Automatic API URL detection
- ✅ Helpful error messages with API URL display
