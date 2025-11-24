# Railway Branch Configuration Guide

## How to Change Railway Deployment Branch

### Method 1: Railway Dashboard (Web UI)

1. **Go to Railway Dashboard**
   - Visit: https://railway.app/dashboard
   - Log in to your account

2. **Select Your Project**
   - Click on your "Dealer Scraper" project

3. **Open Service Settings**
   - Click on your service/deployment
   - Click on the **"Settings"** tab

4. **Change Source Branch**
   - Scroll to **"Source"** or **"GitHub"** section
   - Look for **"Branch"** or **"Production Branch"** setting
   - Click on the branch dropdown
   - Select your desired branch:
     - `refactor/professional-cleanup-2025-11-24` (new refactored code)
     - `main` (if you merge the PR first)
     - Or any other branch

5. **Save and Redeploy**
   - Changes should auto-save
   - Railway will automatically trigger a new deployment
   - Wait for deployment to complete (usually 2-5 minutes)

### Method 2: Railway CLI (Alternative)

If you have Railway CLI installed:

```bash
# Install Railway CLI (if not installed)
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Check current settings
railway vars

# You may need to go to dashboard for branch settings
```

Note: Branch configuration is typically done through the web dashboard.

## Before Changing the Branch

### Option A: Merge to Main First (Recommended)

If you want to keep using the `main` branch on Railway:

```bash
# 1. Switch to main branch
git checkout main

# 2. Merge your refactored branch
git merge refactor/professional-cleanup-2025-11-24

# 3. Push to GitHub
git push origin main
```

Then Railway will automatically deploy the new code if it's watching `main`.

### Option B: Point Railway to New Branch

Keep Railway pointed at your new branch:
- Branch: `refactor/professional-cleanup-2025-11-24`
- This is good for testing before merging to main

### Option C: Create a Production Branch

```bash
# Create a dedicated production branch
git checkout -b production
git merge refactor/professional-cleanup-2025-11-24
git push -u origin production
```

Then point Railway to the `production` branch.

## Checking Current Railway Configuration

In Railway Dashboard:
1. Go to your project
2. Click on "Settings"
3. Look for "Source" section
4. You'll see:
   - Repository: `CedmondsTH/dealer-scraper`
   - Branch: `<current-branch>`
   - Root Directory: (usually `/`)

## Environment Variables

After changing branches, verify these are still set in Railway:
- Any API keys you're using
- `PYTHON_VERSION` (if specified)
- Other custom environment variables

Railway preserves environment variables across deployments.

## Deploy Triggers

Railway can be configured to:
- ✅ Auto-deploy on push to specified branch (recommended)
- ⏸️ Manual deployments only
- 🔄 Deploy on pull requests

Check "Deployments" settings in Railway to configure this.

## Troubleshooting

### If deployment fails after branch change:

1. **Check build logs** in Railway dashboard
2. **Verify all files are pushed** to GitHub
3. **Check requirements.txt** is up to date
4. **Verify Railway start command**:
   - Should be: `streamlit run app.py`
   - Check in Settings → Deploy

### Build Command (if needed):
```bash
pip install -r requirements.txt
playwright install chromium
```

### Start Command:
```bash
streamlit run app.py
```

## Recommended Workflow

For production deployments:

```
Feature Branch → PR → Main → Railway Deploys
```

1. Develop on feature branch: `refactor/professional-cleanup-2025-11-24` ✅
2. Push to GitHub ✅
3. Create Pull Request
4. Review and merge to `main`
5. Railway auto-deploys from `main`

This keeps your production environment stable!
