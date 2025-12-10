# 🚀 Render Deployment - Quick Start

## Step 1: Push to GitHub (5 minutes)

```powershell
# 1. Add all files to git
cd "d:\clean india"
git add .

# 2. Commit your code
git commit -m "Production ready - MongoDB + ML features"

# 3. Create GitHub repository at: https://github.com/new
# Name it: urban-issue-reporter

# 4. Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/urban-issue-reporter.git

# 5. Push to GitHub
git push -u origin main
```

**If authentication fails:**
```powershell
# Generate Personal Access Token at: https://github.com/settings/tokens
# Then use:
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/urban-issue-reporter.git
git push -u origin main
```

## Step 2: Deploy on Render (5 minutes)

### 2.1 Create Web Service

1. Go to: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repository: `urban-issue-reporter`
4. Click **"Connect"**

### 2.2 Configure Service

**Basic Settings:**
- Name: `urban-issue-reporter`
- Branch: `main`
- Build Command: `pip install -r requirements-prod.txt`
- Start Command: `gunicorn --config deployment/gunicorn_config.py wsgi:app`

**Environment Variables:**

Add these in Render dashboard:

```
FLASK_ENV = production
SECRET_KEY = [Click Generate]
MONGO_URI = mongodb+srv://satishchandala834_db_user:0MivD44lzk3kCcqk@cluster0.izh4its.mongodb.net/
MONGO_DB_NAME = urban_issues_db
MAIL_SERVER = smtp.gmail.com
MAIL_PORT = 587
MAIL_USE_TLS = true
MAIL_USERNAME = satishchandala834@gmail.com
MAIL_PASSWORD = oqqv jvjk byzf kbhn
```

**Advanced:**
- Health Check Path: `/health`
- Auto-Deploy: ✅ Enabled

### 2.3 Deploy

Click **"Create Web Service"** and wait 5-10 minutes.

## Step 3: Verify Deployment

Your app will be live at: `https://urban-issue-reporter.onrender.com`

Test:
1. Open URL in browser
2. Login with: `admin@example.com` / `admin123`
3. Change admin password immediately!

## ⚠️ Important Notes

### Free Tier Limitations
- Service spins down after 15 min inactivity
- First request takes 30-60 seconds (cold start)
- Limited to 750 hours/month

### Security Checklist
- [ ] Change admin password after first login
- [ ] Use generated SECRET_KEY (never commit)
- [ ] Verify MongoDB Atlas network access allows Render (0.0.0.0/0)
- [ ] Test all features: login, issue reporting, file upload, email

### Continuous Deployment

Every time you push to GitHub, Render auto-deploys:

```powershell
git add .
git commit -m "Your changes"
git push origin main
```

## 📚 Full Documentation

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for:
- Custom domain setup
- Troubleshooting guide
- Production best practices
- Monitoring and logging
- Cost optimization

## 🆘 Quick Troubleshooting

**Build fails?**
- Check requirements-prod.txt is complete
- Review build logs in Render dashboard

**App won't start?**
- Verify all environment variables are set
- Check MongoDB connection string
- Review application logs

**MongoDB connection failed?**
- Add `0.0.0.0/0` to MongoDB Atlas Network Access
- Verify MONGO_URI is correct

**502 Bad Gateway?**
- Check if health endpoint responds: `/health`
- Review gunicorn logs
- Restart service in Render dashboard

## 💡 Pro Tips

1. **Enable Auto-Deploy** - Code changes deploy automatically
2. **Use Render Disk** - For persistent file storage (paid plans)
3. **Monitor Logs** - Check regularly for errors
4. **Set Up Alerts** - Get notified of issues
5. **Use CDN** - For static files (Cloudflare, etc.)

## 🎉 Success!

Once deployed, your application is production-ready with:
- ✅ MongoDB Atlas cloud database
- ✅ ML-powered issue categorization
- ✅ Email notifications
- ✅ Admin dashboard
- ✅ Automatic deployments
- ✅ HTTPS/SSL included

---

**Need help?** See full guide: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
