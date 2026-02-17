# ✅ OmniQuant Deployment Checklist

Follow this checklist to deploy OmniQuant to Render.

---

## 📋 Pre-Deployment

- [ ] All code working locally
- [ ] Backend starts successfully (`python api/main.py`)
- [ ] Frontend starts successfully (`cd frontend && npm start`)
- [ ] Test scan functionality works
- [ ] Git repository initialized
- [ ] All changes committed

---

## 🔧 GitHub Setup

- [ ] Created GitHub repository
- [ ] Added remote: `git remote add origin <url>`
- [ ] Pushed code: `git push -u origin main`
- [ ] Repository is public (or private with Render connected)

---

## 🚀 Render Backend Deployment

- [ ] Signed up at render.com
- [ ] Created new Web Service
- [ ] Connected GitHub repository
- [ ] Configured build settings:
  - [ ] Runtime: Python 3
  - [ ] Build: `pip install -r requirements.txt`
  - [ ] Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- [ ] Added environment variables:
  - [ ] `PYTHONPATH=/opt/render/project/src`
  - [ ] `ENVIRONMENT=production`
  - [ ] `DEBUG=false`
  - [ ] `USE_REAL_DATA=false`
  - [ ] `CORS_ORIGINS=*`
- [ ] Deployed successfully
- [ ] Copied backend URL: `____________________________`
- [ ] Tested health endpoint: `/health`

---

## 🎨 Render Frontend Deployment

- [ ] Created new Static Site
- [ ] Connected same GitHub repository
- [ ] Configured build settings:
  - [ ] Build: `cd frontend && npm install && npm run build`
  - [ ] Publish: `frontend/build`
- [ ] Added environment variable:
  - [ ] `REACT_APP_API_URL=<backend-url>`
- [ ] Deployed successfully
- [ ] Copied frontend URL: `____________________________`
- [ ] Site loads in browser

---

## 🔗 Final Configuration

- [ ] Updated backend CORS with frontend URL
- [ ] Tested API from frontend
- [ ] Scan functionality works
- [ ] Opportunities display correctly
- [ ] Metrics panel updates
- [ ] Real-time data toggle works (if enabled)
- [ ] Mobile responsive
- [ ] Disclaimer visible

---

## ✅ Testing & Verification

- [ ] Health check passes: `<backend-url>/health`
- [ ] Metrics endpoint works: `<backend-url>/metrics`
- [ ] Frontend loads: `<frontend-url>`
- [ ] Can click "Scan Markets"
- [ ] Opportunities appear
- [ ] No console errors
- [ ] Works on different devices
- [ ] Works on different browsers

---

## 📱 Share & Demo

- [ ] Saved deployment URLs
- [ ] Tested with team members
- [ ] Prepared demo script
- [ ] Screenshots taken
- [ ] Shared with judges/reviewers

---

## 🎯 Optional Enhancements

- [ ] Custom domain configured
- [ ] SSL certificate active (auto with Render)
- [ ] Monitoring dashboards viewed
- [ ] Logs reviewed for errors
- [ ] Performance tested
- [ ] SEO meta tags added
- [ ] Analytics integrated

---

## 📝 Your Deployment Info

**Fill this out when deployed:**

```
Backend URL:  https://_________________________________.onrender.com
Frontend URL: https://_________________________________.onrender.com
Deployed On:  ______________ (date)
Status:       ☐ Development  ☐ Staging  ☐ Production
```

---

## 🐛 If Something Fails

**Backend Issues:**
1. Check Render logs
2. Verify environment variables
3. Check PYTHONPATH is set
4. Ensure requirements.txt is complete

**Frontend Issues:**
1. Check build logs
2. Verify REACT_APP_API_URL is set
3. Test API endpoint directly
4. Check CORS settings

**Connection Issues:**
1. Verify backend is running (not sleeping)
2. Check CORS origins match
3. Test API with curl/Postman
4. Check browser console for errors

---

## 📞 Help & Support

- **Render Docs**: https://render.com/docs
- **OmniQuant Guide**: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
- **Test Script**: `./test-api.ps1 -ApiUrl <url>`

---

**Once all boxes are checked, you're live! 🎉**
