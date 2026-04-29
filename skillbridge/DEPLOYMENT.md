# Deployment Guide for SkillBridge API

## Platform: Railway.app

### Prerequisites
- Railway account (free tier available)
- GitHub repository with SkillBridge code
- PostgreSQL database (use Neon)

### Step-by-Step

1. **Create PostgreSQL Database on Neon**
   - Go to https://neon.tech
   - Create new project
   - Note the connection string

2. **Push Code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: SkillBridge API"
   git push origin main
   ```

3. **Create Railway Project**
   - Go to https://railway.app/dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your SkillBridge repository
   - Click "Deploy"

4. **Configure Environment Variables**
   - Go to Railway dashboard
   - Select your project
   - Go to Variables tab
   - Add these environment variables:
     ```
     DATABASE_URL=postgresql://user:password@host/skillbridge
     JWT_SECRET_KEY=your-secret-key-change-this
     MONITORING_OFFICER_API_KEY=your-api-key-change-this
     ```

5. **Configure Procfile** (create in root directory)
   ```
   web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
   ```

6. **Wait for Deployment**
   - Railway will automatically deploy
   - Check logs for any errors
   - Your API will be live at a public URL

---

## Platform: Render.com

### Prerequisites
- Render account (free tier available)
- GitHub repository
- PostgreSQL from Neon

### Step-by-Step

1. **Create Render Web Service**
   - Go to https://render.com/dashboard
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Select branch (main)

2. **Configure Service**
   - Name: `skillbridge-api`
   - Runtime: `Python 3.11`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port 8080`

3. **Add Environment Variables**
   - Go to Environment tab
   - Add:
     ```
     DATABASE_URL=postgresql://...
     JWT_SECRET_KEY=your-secret
     MONITORING_OFFICER_API_KEY=your-api-key
     ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for build and deployment
   - Service will be live at render URL

---

## Platform: Fly.io

### Prerequisites
- Fly.io account (free tier available)
- Fly CLI installed (`curl -L https://fly.io/install.sh | sh`)

### Step-by-Step

1. **Initialize Fly.io App**
   ```bash
   flyctl launch
   # Choose region, accept PostgreSQL database creation
   ```

2. **Configure fly.toml**
   - Set environment variables in [env] section
   - Set memory to 256MB (free tier)

3. **Add Secrets**
   ```bash
   flyctl secrets set \
     DATABASE_URL="postgresql://..." \
     JWT_SECRET_KEY="your-secret-key" \
     MONITORING_OFFICER_API_KEY="your-api-key"
   ```

4. **Deploy**
   ```bash
   flyctl deploy
   ```

5. **Check Status**
   ```bash
   flyctl status
   flyctl logs
   ```

---

## Post-Deployment Steps

### 1. Test Live API
```bash
curl https://your-api-url/health

# Test login
curl -X POST https://your-api-url/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "student1@example.com", "password": "password123"}'
```

### 2. Initialize Database
```bash
# Run seed script on deployed app
flyctl ssh console
python -m src.seed
exit
```

### 3. Monitor Logs
```bash
# Railway
railway logs

# Render
curl https://api.render.com/v1/services/your-service-id/logs

# Fly.io
flyctl logs
```

### 4. Scale Resources (if needed)
- **Railway**: Increase Memory/CPU in settings
- **Render**: Upgrade plan
- **Fly.io**: Adjust in fly.toml

---

## Common Deployment Issues

### Issue: `ModuleNotFoundError: No module named 'src'`
**Solution**: Ensure `PYTHONPATH` includes project root, or use relative imports

### Issue: Database connection timeout
**Solution**: 
- Check DATABASE_URL is correct
- Ensure firewall allows connections
- Test with: `psql $DATABASE_URL`

### Issue: 502 Bad Gateway
**Solution**:
- Check logs for application errors
- Ensure start command is correct
- Verify environment variables are set

### Issue: Out of memory
**Solution**:
- Upgrade memory allocation
- Check for memory leaks in code
- Use connection pooling for database

---

## Monitoring & Logs

### View Logs
```bash
# Railway
railway logs

# Render
Logs tab in dashboard

# Fly.io
flyctl logs -f
```

### Performance Monitoring
- Set up error tracking (Sentry)
- Monitor database query times
- Track API response times

---

## Rollback Procedure

### Railway
```bash
railway redeploy <commit-hash>
```

### Render
- Dashboard → Deployments → Select previous deployment → Rollback

### Fly.io
```bash
flyctl releases list
flyctl releases rollback <release-number>
```

---

## Continuous Deployment

### GitHub Actions Workflow
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm i -g @railway/cli
          railway link ${{ secrets.RAILWAY_PROJECT_ID }}
          railway up
```

---

## Security Checklist

- [ ] Change `JWT_SECRET_KEY` in production
- [ ] Change `MONITORING_OFFICER_API_KEY` in production
- [ ] Enable HTTPS (automatic on Railway/Render)
- [ ] Set database backup schedule
- [ ] Configure database firewall rules
- [ ] Monitor logs for unauthorized access
- [ ] Rotate API keys periodically
- [ ] Use secrets manager for sensitive data

---

## Cost Estimates (Monthly)

| Platform | Database | API | Total |
|----------|----------|-----|-------|
| Railway + Neon | $5-10 | Free | $5-10 |
| Render + Neon | Free | Free | Free |
| Fly.io + Neon | $5 | Free | $5 |

All free tiers include enough resources for development and testing.

---

## Support & Help

- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs
- **Fly.io Docs**: https://fly.io/docs
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
