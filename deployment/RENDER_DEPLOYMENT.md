# Deploy to Render - Step by Step Guide

## Prerequisites

1. **GitHub Account** - Create at https://github.com
2. **Render Account** - Sign up at https://render.com (use GitHub to sign in)
3. **MongoDB Atlas** - Already configured ✅

## Step 1: Prepare Your GitHub Repository

### 1.1 Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `urban-issue-reporter` (or your choice)
3. Description: "Urban Issue Reporting System with ML capabilities"
4. Set to **Public** or **Private**
5. **Don't** initialize with README (you already have one)
6. Click **Create repository**

### 1.2 Push Your Code to GitHub

Open PowerShell in your project directory and run:

```powershell
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Production ready structure"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/urban-issue-reporter.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Note:** If you get authentication errors, you may need to:
- Generate a Personal Access Token at: https://github.com/settings/tokens
- Use: `git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/urban-issue-reporter.git`

## Step 2: Deploy on Render

### 2.1 Create New Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** button → Select **"Web Service"**
3. Connect your GitHub account (if not already connected)
4. Select your repository: `urban-issue-reporter`
5. Click **"Connect"**

### 2.2 Configure Web Service

Fill in the following settings:

**Basic Settings:**
- **Name:** `urban-issue-reporter` (or your choice)
- **Region:** Choose closest to you (e.g., Oregon, Frankfurt, Singapore)
- **Branch:** `main`
- **Root Directory:** Leave blank
- **Runtime:** `Python 3`
- **Build Command:** 
  ```bash
  pip install -r requirements-prod.txt
  ```
- **Start Command:** 
  ```bash
  gunicorn --config deployment/gunicorn_config.py wsgi:app
  ```

**Instance Type:**
- Select **"Free"** (or paid plan for better performance)

**Advanced Settings (click "Advanced"):**

Add Environment Variables:

| Key | Value | Notes |
|-----|-------|-------|
| `FLASK_ENV` | `production` | Required |
| `SECRET_KEY` | Click "Generate" | Auto-generated secure key |
| `MONGO_URI` | `mongodb+srv://satishchandala834_db_user:0MivD44lzk3kCcqk@cluster0.izh4its.mongodb.net/` | Your MongoDB Atlas URI |
| `MONGO_DB_NAME` | `urban_issues_db` | Your database name |
| `MAIL_SERVER` | `smtp.gmail.com` | Email server |
| `MAIL_PORT` | `587` | SMTP port |
| `MAIL_USE_TLS` | `true` | Enable TLS |
| `MAIL_USERNAME` | `satishchandala834@gmail.com` | Your email |
| `MAIL_PASSWORD` | `oqqv jvjk byzf kbhn` | Your app password |

**Health Check Path:**
- Set to: `/health`

**Auto-Deploy:**
- ✅ Enable "Auto-Deploy" (deploys automatically on git push)

### 2.3 Create Web Service

1. Click **"Create Web Service"** button
2. Wait for deployment (5-10 minutes for first deploy)
3. Watch the build logs in real-time

## Step 3: Verify Deployment

### 3.1 Check Build Logs

Monitor the logs for:
- ✅ Dependencies installation
- ✅ Build completion
- ✅ Service starting
- ✅ Health check passing

### 3.2 Access Your Application

Once deployed, you'll get a URL like:
```
https://urban-issue-reporter.onrender.com
```

Test the following:
1. Open the URL in browser
2. Try to register a new account
3. Login with admin credentials:
   - Email: `admin@example.com`
   - Password: `admin123`
4. Report a test issue
5. Check admin dashboard

## Step 4: Configure Custom Domain (Optional)

### 4.1 Add Custom Domain in Render

1. Go to your service dashboard
2. Click **"Settings"** tab
3. Scroll to **"Custom Domain"**
4. Click **"Add Custom Domain"**
5. Enter your domain (e.g., `issues.yourdomain.com`)

### 4.2 Update DNS Records

Add these records to your domain DNS:

**For subdomain (e.g., issues.yourdomain.com):**
```
Type: CNAME
Name: issues
Value: urban-issue-reporter.onrender.com
```

**For root domain (e.g., yourdomain.com):**
```
Type: A
Name: @
Value: [IP provided by Render]
```

SSL certificate will be automatically provisioned.

## Step 5: Set Up Persistent Storage (Optional)

Render's free tier has ephemeral storage. To persist uploads:

### Option 1: Use Cloud Storage (Recommended)

Update your code to use AWS S3 or Azure Blob Storage for file uploads.

### Option 2: Use Render Disks (Paid Plans Only)

1. Go to service **"Settings"**
2. Scroll to **"Disks"**
3. Click **"Add Disk"**
4. Mount path: `/opt/render/project/src/uploads`
5. Size: 1GB or more

## Step 6: Monitor Your Application

### 6.1 View Logs

- Go to **"Logs"** tab in Render dashboard
- Use filters to find specific issues
- Download logs if needed

### 6.2 Set Up Alerts (Optional)

1. Go to **"Settings"**
2. Scroll to **"Notifications"**
3. Add email or Slack webhook
4. Get notified on:
   - Build failures
   - Service downtime
   - High error rates

## Step 7: Continuous Deployment

Every time you push to GitHub:

```powershell
git add .
git commit -m "Your commit message"
git push origin main
```

Render will automatically:
1. Pull latest code
2. Run build command
3. Deploy new version
4. Run health checks

## Troubleshooting

### Build Fails

**Issue:** `ModuleNotFoundError`
- **Fix:** Check `requirements-prod.txt` has all dependencies

**Issue:** `Build command failed`
- **Fix:** Check build logs for specific error

### Application Won't Start

**Issue:** `Address already in use`
- **Fix:** Render uses PORT environment variable automatically

**Issue:** `MongoDB connection failed`
- **Fix:** Verify MONGO_URI is correct and MongoDB Atlas allows Render's IP

### 502 Bad Gateway

**Issue:** Service not responding
- **Fix:** Check if app binds to `0.0.0.0` and uses `PORT` env variable
- **Fix:** Verify gunicorn config is correct

### Free Tier Limitations

Render Free tier:
- ⚠️ Service spins down after 15 minutes of inactivity
- ⚠️ Cold start takes 30-60 seconds
- ⚠️ Limited to 750 hours/month
- ⚠️ No persistent storage

**Solutions:**
1. Upgrade to paid plan ($7/month)
2. Use external ping service to keep alive
3. Warn users about cold starts

## Security Best Practices

### Before Going Live:

1. **Change Default Admin Password**
   ```python
   # Login as admin and change password immediately
   ```

2. **Use Strong Secret Key**
   ```python
   # Render auto-generates this - keep it secret!
   ```

3. **Enable HTTPS Only**
   - Render provides free SSL
   - Update config to force HTTPS

4. **Whitelist MongoDB IPs**
   - Add `0.0.0.0/0` in MongoDB Atlas Network Access
   - Or add specific Render IPs

5. **Use App-Specific Passwords**
   - For Gmail, use App Passwords instead of account password
   - Generate at: https://myaccount.google.com/apppasswords

## Updating Your Application

### Deploy New Features

```powershell
# Make changes to your code
# Test locally
python run.py

# Commit and push
git add .
git commit -m "Add new feature"
git push origin main

# Render auto-deploys!
```

### Rollback to Previous Version

1. Go to **"Events"** tab
2. Find successful deployment
3. Click **"Rollback"** button

## Cost Estimation

### Free Tier
- **Web Service:** Free (with limitations)
- **Total:** $0/month

### Starter Plan (Recommended)
- **Web Service:** $7/month
- **Benefits:**
  - Always-on (no spin down)
  - Better performance
  - 400 build minutes/month
  - Custom domains with SSL
- **Total:** $7/month

### Database Options
- **MongoDB Atlas:** Free tier (512MB)
- **Render PostgreSQL:** $7/month (not needed - using Atlas)

## Support Resources

- **Render Documentation:** https://render.com/docs
- **Render Community:** https://community.render.com
- **GitHub Issues:** Create issue in your repo
- **MongoDB Atlas Support:** https://www.mongodb.com/cloud/atlas/support

## Quick Reference Commands

```powershell
# Push updates
git add . && git commit -m "Update" && git push origin main

# View local logs
Get-Content logs\app.log -Tail 50

# Test production build locally
pip install -r requirements-prod.txt
gunicorn --config deployment/gunicorn_config.py wsgi:app

# Generate new secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

## Success Checklist

- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] Environment variables configured
- [ ] Build successful
- [ ] Application accessible via URL
- [ ] Admin login working
- [ ] Issue reporting functional
- [ ] File uploads working
- [ ] Email notifications working
- [ ] MongoDB connection stable
- [ ] Health check passing
- [ ] Auto-deploy enabled
- [ ] Admin password changed
- [ ] Custom domain configured (optional)

## 🎉 Congratulations!

Your Urban Issue Reporter is now live on Render!

**Next Steps:**
1. Share the URL with users
2. Monitor logs and performance
3. Collect user feedback
4. Iterate and improve

---

**Your Application URL:** `https://urban-issue-reporter.onrender.com`

Remember to replace with your actual Render URL!
