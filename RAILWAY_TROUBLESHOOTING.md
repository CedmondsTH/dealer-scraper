# Railway Deployment Troubleshooting

## Issue: Railway Not Auto-Deploying After Push

### Quick Fixes:

1. **Manually Trigger Deployment in Railway**
   - Click on your project in Railway
   - Look for "Deploy" or "Redeploy" button
   - Or go to Deployments → Click "..." → "Redeploy"

2. **Check Auto-Deploy Settings**
   - In Railway: Settings → Service Settings
   - Look for "Auto Deploy" or "Deploy Triggers"
   - Make sure it's enabled for the `main` branch

3. **Verify Branch Configuration**
   - Railway Settings → Source
   - Branch should be set to: `main`
   - Root Directory: `/` (or leave blank)

4. **Check for Build/Deploy Errors**
   - Click "View" on the failed deployment
   - Review the build logs
   - Look for error messages

### Common Issues:

#### If Railway is watching wrong branch:
- Your push was to `main` ✅
- But Railway might be watching `original-main` or another branch
- **Fix:** Change branch in Railway Settings → Source → Branch → `main`

#### If Auto-Deploy is disabled:
- Railway won't trigger on pushes
- **Fix:** Enable in Settings → Deploy Triggers → Auto Deploy: ON

#### If there's a build error:
- Railway tried to deploy but build failed
- **Fix:** Check logs and fix the error

### Manual Deploy Now:

**Option 1: Through Railway Dashboard**
1. Go to: https://railway.app/dashboard
2. Click your "dealer-scraper" project
3. Click the service
4. Look for "Deploy" or "⋮" menu → "Redeploy"
5. Select "Latest commit" or "Redeploy from main"

**Option 2: Force a New Commit (Push Empty Commit)**
If Railway is configured correctly but didn't trigger:

```bash
git commit --allow-empty -m "Trigger Railway deployment"
git push origin main
```

This creates an empty commit that should trigger Railway.

### Check Current Railway Status:

1. **Click "View" on the failed deployment** to see what went wrong
2. **Check Settings → Deployments** to see if auto-deploy is enabled
3. **Verify the branch** in Settings → Source

Let me know what you see when you click "View" on that deployment!
