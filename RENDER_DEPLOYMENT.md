# 🚀 Deploying OmniQuant to Render

Complete guide to deploy OmniQuant v2 on Render's free tier.

---

## 📋 Prerequisites

1. **GitHub Account** - Your code needs to be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com) (free)
3. **Git** - Installed on your machine

---

## 🔧 Step-by-Step Deployment

### **Step 1: Push Code to GitHub**

```powershell
# Initialize git (if not already done)
cd D:\OmniQuant
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - OmniQuant v2 ready for deployment"

# Create GitHub repository (go to github.com and create new repo)
# Then link and push:
git remote add origin https://github.com/YOUR_USERNAME/omniquant.git
git branch -M main
git push -u origin main
```

---

### **Step 2: Deploy Backend (FastAPI)**

1. **Go to Render Dashboard**: https://dashboard.render.com

2. **Click "New +" → "Web Service"**

3. **Connect GitHub Repository**:
   - Select your `omniquant` repository
   - Click "Connect"

4. **Configure Web Service**:
   ```
   Name: omniquant-api
   Region: Oregon (US West)
   Branch: main
   Root Directory: (leave empty)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
   Plan: Free
   ```

5. **Add Environment Variables**:
   Click "Advanced" → "Add Environment Variable"
   
   Add these:
   ```
   PYTHONPATH = /opt/render/project/src
   ENVIRONMENT = production
   DEBUG = false
   USE_REAL_DATA = false
   CORS_ORIGINS = *
   ```

6. **Click "Create Web Service"**

7. **Wait for deployment** (5-10 minutes first time)

8. **Copy the API URL** - will be something like:
   ```
   https://omniquant-api.onrender.com
   ```

---

### **Step 3: Deploy Frontend (React)**

1. **Go to Render Dashboard** again

2. **Click "New +" → "Static Site"**

3. **Connect Same Repository**

4. **Configure Static Site**:
   ```
   Name: omniquant-frontend
   Region: Oregon (US West)
   Branch: main
   Root Directory: (leave empty)
   Build Command: cd frontend && npm install && npm run build
   Publish Directory: frontend/build
   ```

5. **⚠️ CRITICAL: Add Environment Variable**:
   Click "Advanced" → "Add Environment Variable"
   
   **Add this REQUIRED variable:**
   ```
   REACT_APP_API_URL = https://omniquant-api.onrender.com
   ```
   
   ⚠️ **IMPORTANT:** 
   - Replace with YOUR actual backend URL from Step 2
   - This MUST be set or frontend won't connect to backend
   - No trailing slash
   - Must be HTTPS

6. **Auto-Deploy**: Enable "Auto-Deploy" for automatic updates

7. **Click "Create Static Site"**

8. **Wait for build** (3-5 minutes)

9. **Your app is live!** URL will be:
   ```
   https://omniquant-frontend.onrender.com
   ```

---

### **Step 4: Update CORS (Important!)**

1. **Go back to Backend Service** (omniquant-api)

2. **Click "Environment" tab**

3. **Edit `CORS_ORIGINS`**:
   ```
   CORS_ORIGINS = https://omniquant-frontend.onrender.com
   ```

4. **Click "Save Changes"** - service will redeploy

---

## ✅ Verification

### **Test Backend:**
```bash
# Health check
curl https://omniquant-api.onrender.com/health

# Should return:
# {"status":"healthy","timestamp":...}
```

### **Test Frontend:**
1. Open `https://omniquant-frontend.onrender.com`
2. Click "Scan Markets"
3. Check if opportunities are detected

---

## ⚙️ Using Blueprint (Alternative - One-Click Deploy)

If you have `render.yaml` in your repo:

1. **Go to Render Dashboard**
2. **Click "New +" → "Blueprint"**
3. **Connect Repository**
4. **Click "Apply"** - Render creates both services automatically!

---

## 🔄 Automatic Updates

Once deployed, any push to `main` branch triggers auto-deploy:

```powershell
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Render automatically:
# - Detects changes
# - Rebuilds services
# - Deploys new version
```

---

## 🌐 Custom Domain (Optional)

### **For Frontend:**
1. Go to Static Site settings
2. Click "Custom Domains"
3. Add your domain: `omniquant.yourdomain.com`
4. Update DNS records as shown

### **For Backend:**
1. Go to Web Service settings
2. Add custom domain: `api.omniquant.yourdomain.com`
3. Update DNS

---

## 💰 Cost Breakdown

### **Free Tier Limits:**
- **Backend**: 750 hours/month (enough for 24/7)
- **Frontend**: Unlimited static hosting
- **Bandwidth**: 100 GB/month
- **Build Minutes**: 500 minutes/month

### **Free Tier Sleep:**
- Backend sleeps after 15 min inactivity
- First request wakes it (30-60 seconds cold start)
- Keep-alive: Use cron-job.org to ping every 14 min

### **Upgrade to Paid ($7/month):**
- No sleep
- Faster builds
- Custom domains included
- More resources

---

## 🐛 Troubleshooting

### **Backend won't start:**
```bash
# Check logs in Render dashboard
# Common issues:
1. PYTHONPATH not set → Add: PYTHONPATH=/opt/render/project/src
2. Port not binding → Ensure: --port $PORT in start command
3. Module not found → Check requirements.txt has all dependencies
```

### **Frontend can't reach backend / Scanning doesn't work:**
```bash
# MOST COMMON ISSUE: REACT_APP_API_URL not set correctly

Step 1: Check browser console (F12)
- Look for: "OmniQuant API Configuration: API Base URL: ..."
- If it shows "http://localhost:8000" → Environment variable NOT SET

Step 2: Fix the environment variable
- Go to: Render Dashboard → omniquant-frontend → Environment
- Add/Update: REACT_APP_API_URL = https://omniquant-api-XXXX.onrender.com
- Use YOUR actual backend URL (copy from backend service)
- ⚠️ NO trailing slash!

Step 3: Rebuild frontend
- Render Dashboard → omniquant-frontend
- Click "Manual Deploy" → "Clear build cache & deploy"
- Wait 3-5 minutes for rebuild

Step 4: Verify
- Open frontend URL
- Check header for "API Connected" green indicator
- Click "Scan Markets" - should work in ~5 seconds
```

### **Backend is sleeping (free tier):**
```bash
# Symptoms:
- First scan takes 30-60 seconds
- "API Disconnected" shows in red

# This is normal for free tier
# Backend wakes up on first request
# Subsequent scans are fast

# Keep-alive solution (optional):
- Use cron-job.org to ping /health every 14 minutes
- Prevents sleep (uses your 750 free hours)
```

### **Real-time data removed:**
```bash
# NOTE: Real-time data checkbox has been REMOVED
# App now ALWAYS uses simulated data for:
# ✅ Faster scanning (~5 seconds vs 30+ seconds)
# ✅ More reliable (no exchange API dependencies)  
# ✅ Always finds opportunities (better for demos)
# ✅ No rate limits or network issues

````

### **Build fails:**
```bash
# Frontend build:
- Check Node version: Render uses Node 18
- npm install errors: Clear cache and retry

# Backend build:
- Python version mismatch: Render uses Python 3.11
- C++ dependencies: Skip (use Python fallback)
```

---

## 📊 Monitoring

### **View Logs:**
1. Go to service dashboard
2. Click "Logs" tab
3. Real-time log streaming

### **Metrics:**
- CPU usage
- Memory usage
- Request count
- Response times

---

## 🔒 Security Best Practices

1. **Never commit `.env` files**
   ```bash
   # Already in .gitignore
   ```

2. **Use Render environment variables** for secrets

3. **Set specific CORS origins** in production:
   ```
   CORS_ORIGINS=https://omniquant-frontend.onrender.com
   ```

4. **Disable DEBUG mode**:
   ```
   DEBUG=false
   ```

5. **Add rate limiting** (future enhancement)

---

## 🎯 Production Checklist

Before going live:

- [ ] Code pushed to GitHub
- [ ] Backend deployed on Render
- [ ] Frontend deployed on Render
- [ ] CORS configured correctly
- [ ] Environment variables set
- [ ] Health check passes
- [ ] Frontend loads successfully
- [ ] API calls work
- [ ] Scan functionality works
- [ ] Disclaimer visible
- [ ] Test on mobile
- [ ] Share URL with team/judges

---

## 🚀 Quick Deploy Commands

```powershell
# From your project root
cd D:\OmniQuant

# Commit latest changes
git add .
git commit -m "Deploy to Render"
git push origin main

# Done! Render auto-deploys in ~5 minutes
```

---

## 📱 Your Live URLs

After deployment, you'll have:

- **Frontend**: `https://omniquant-frontend.onrender.com`
- **Backend**: `https://omniquant-api.onrender.com`
- **API Docs**: `https://omniquant-api.onrender.com/docs` (if DEBUG=true)
- **Health**: `https://omniquant-api.onrender.com/health`

---

## 🎉 Success!

Your OmniQuant v2 is now:
- ✅ Live on the internet
- ✅ Accessible from anywhere
- ✅ Auto-deploying on updates
- ✅ Running on free tier
- ✅ Ready for demo/hackathon!

Share your live URL and impress the judges! 🏆

---

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **OmniQuant Issues**: GitHub Issues in your repo

---

**Built with ❤️ for MIT/IIT Hackathon 2026**
