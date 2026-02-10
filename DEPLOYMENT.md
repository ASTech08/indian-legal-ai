# Complete Deployment Guide - Indian Legal AI Platform

## 🚀 Quick Deployment Guide

### Prerequisites Checklist
- [ ] GitHub account
- [ ] Vercel account (free tier)
- [ ] Render account (free tier)
- [ ] OpenAI API key
- [ ] Clerk account (for authentication)
- [ ] AWS account (for S3 storage) - optional

---

## Step-by-Step Deployment Process

### Step 1: Prepare Your Repository

```bash
# 1. Initialize git repository
cd indian-legal-ai
git init
git add .
git commit -m "Initial commit: Indian Legal AI Platform"

# 2. Create GitHub repository
# Go to github.com → New Repository → "indian-legal-ai"
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/indian-legal-ai.git
git branch -M main
git push -u origin main
```

### Step 2: Set Up Authentication (Clerk)

1. **Sign up at [Clerk.dev](https://clerk.dev)**
2. **Create Application**:
   - Name: "Indian Legal AI"
   - Choose: Email + Password (or add Google/GitHub OAuth)
3. **Get API Keys**:
   - Copy `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
   - Copy `CLERK_SECRET_KEY`
4. **Configure Settings**:
   - Go to "Paths" → Set sign-in URL: `/sign-in`
   - Set sign-up URL: `/sign-up`
   - Set after sign-in: `/chat`

### Step 3: Deploy Backend to Render

#### A. Create Database

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "PostgreSQL"
3. Settings:
   ```
   Name: indian-legal-ai-db
   Database: legal_ai
   User: legal_ai_user
   Region: Singapore (or closest to users)
   Plan: Free
   ```
4. Click "Create Database"
5. **SAVE** the Internal Database URL (looks like: `postgresql://user:pass@...`)

#### B. Create Redis

1. Click "New +" → "Redis"
2. Settings:
   ```
   Name: indian-legal-ai-redis
   Region: Same as database
   Plan: Free
   ```
3. Click "Create Redis"
4. **SAVE** the Internal Redis URL

#### C. Deploy Backend Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Settings:
   ```
   Name: indian-legal-ai-backend
   Region: Same as database
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT
   Instance Type: Free
   ```

4. **Add Environment Variables** (click "Advanced" → "Add Environment Variable"):

   ```bash
   # Database
   DATABASE_URL=<paste Internal Database URL from step A>
   
   # Redis
   REDIS_URL=<paste Internal Redis URL from step B>
   
   # Security
   SECRET_KEY=<generate using: openssl rand -hex 32>
   ALGORITHM=HS256
   
   # OpenAI
   OPENAI_API_KEY=sk-...  # Your OpenAI key
   OPENAI_MODEL=gpt-4-turbo-preview
   
   # AWS S3 (optional - for file uploads)
   AWS_ACCESS_KEY_ID=your_aws_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret
   AWS_REGION=ap-south-1
   S3_BUCKET_NAME=indian-legal-ai-uploads
   
   # App Config
   ENVIRONMENT=production
   DEBUG=False
   
   # CORS (will add frontend URL after Step 4)
   CORS_ORIGINS=https://indian-legal-ai.vercel.app,https://your-custom-domain.com
   ```

5. Click "Create Web Service"
6. Wait for deployment (5-10 minutes)
7. **SAVE** the backend URL (looks like: `https://indian-legal-ai-backend.onrender.com`)

#### D. Initialize Database

Once backend is deployed:

1. Go to backend service → "Shell" tab
2. Run migrations:
   ```bash
   alembic upgrade head
   ```

### Step 4: Deploy Frontend to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Settings:
   ```
   Framework Preset: Next.js
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

5. **Add Environment Variables**:

   ```bash
   # API Configuration
   NEXT_PUBLIC_API_URL=<your backend URL from Step 3>
   NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
   
   # Clerk Authentication
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=<from Step 2>
   CLERK_SECRET_KEY=<from Step 2>
   ```

6. Click "Deploy"
7. Wait for deployment (3-5 minutes)
8. **Your app is live!** 🎉

### Step 5: Update CORS Settings

1. Go back to Render → Backend Service → Environment
2. Update `CORS_ORIGINS` to include your Vercel URL:
   ```
   CORS_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
   ```
3. Save changes (backend will redeploy)

### Step 6: Configure Custom Domain (Optional)

#### For Frontend (Vercel):
1. Go to Project Settings → Domains
2. Add your domain (e.g., `legalai.in`)
3. Update DNS records at your domain registrar:
   ```
   Type: A
   Name: @
   Value: 76.76.21.21
   
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```

#### For Backend (Render):
1. Go to Service → Settings → Custom Domains
2. Add subdomain (e.g., `api.legalai.in`)
3. Update DNS records:
   ```
   Type: CNAME
   Name: api
   Value: <your-service>.onrender.com
   ```

### Step 7: Set Up Monitoring

#### A. Enable Vercel Analytics
1. Go to Project → Analytics tab
2. Enable Web Analytics (free)

#### B. Set Up Sentry (Error Tracking)
1. Sign up at [sentry.io](https://sentry.io)
2. Create project: "Indian Legal AI"
3. Get DSN key
4. Add to environment variables:
   ```
   # Frontend
   NEXT_PUBLIC_SENTRY_DSN=https://...

   # Backend
   SENTRY_DSN=https://...
   ```

### Step 8: Test Everything

```bash
# 1. Test backend health
curl https://your-backend.onrender.com/health

# 2. Test frontend
# Open browser: https://your-app.vercel.app

# 3. Test full flow:
# - Sign up
# - Sign in
# - Send a chat message
# - Upload a document
# - Check conversation history
```

---

## Environment Variables Reference

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://indian-legal-ai-backend.onrender.com
NEXT_PUBLIC_APP_URL=https://indian-legal-ai.vercel.app
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_SENTRY_DSN=https://...
```

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/legal_ai

# Redis
REDIS_URL=redis://host:6379

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# AWS S3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=ap-south-1
S3_BUCKET_NAME=indian-legal-ai-uploads

# App Config
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=https://indian-legal-ai.vercel.app

# Monitoring
SENTRY_DSN=https://...
```

---

## Troubleshooting

### Backend Issues

**Database connection failed**
```bash
# Check DATABASE_URL format
# Should be: postgresql://USER:PASSWORD@HOST:PORT/DATABASE
# Ensure using INTERNAL database URL from Render
```

**OpenAI API errors**
```bash
# Verify API key is valid
# Check billing in OpenAI account
# Ensure OPENAI_API_KEY env var is set
```

**CORS errors**
```bash
# Ensure frontend URL is in CORS_ORIGINS
# Format: https://your-app.vercel.app (no trailing slash)
```

### Frontend Issues

**Authentication not working**
```bash
# Check Clerk API keys
# Verify Clerk paths are configured correctly
# Check browser console for errors
```

**API calls failing**
```bash
# Verify NEXT_PUBLIC_API_URL is correct
# Check backend is running (test /health endpoint)
# Check CORS settings on backend
```

---

## Scaling & Optimization

### When you're ready to scale:

1. **Upgrade Render Plans**:
   - PostgreSQL: $7/month (1GB RAM)
   - Redis: $10/month
   - Web Service: $7/month (512MB RAM)

2. **Add CDN** (for frontend):
   - Vercel Pro: $20/month (better performance)

3. **Enable Caching**:
   - Redis caching for case laws
   - Vector store caching

4. **Add Monitoring**:
   - Sentry for error tracking
   - LogRocket for session replay
   - PostHog for analytics

---

## Security Checklist

- [ ] All secrets in environment variables (not committed to git)
- [ ] HTTPS enabled on both frontend and backend
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] File upload limits enforced
- [ ] Database backups configured
- [ ] Error messages don't leak sensitive info

---

## Maintenance

### Daily
- Check error logs in Sentry
- Monitor API usage in OpenAI dashboard

### Weekly
- Review user feedback
- Check performance metrics
- Update case law index

### Monthly
- Update dependencies
- Review and optimize database queries
- Backup critical data
- Security audit

---

## Cost Estimate (Monthly)

**Free Tier (For Testing)**:
- Vercel: Free
- Render Database: Free (512MB)
- Render Redis: Free (25MB)
- Render Backend: Free (512MB RAM)
- OpenAI API: Pay-as-you-go (~$20-50 for moderate use)
- **Total**: ~$20-50/month

**Production Tier**:
- Vercel Pro: $20
- Render Database: $7
- Render Redis: $10
- Render Backend: $7
- OpenAI API: ~$100-300 (depends on usage)
- AWS S3: ~$5
- **Total**: ~$150-350/month

---

## Support

For issues:
1. Check logs in Render dashboard
2. Check browser console for frontend errors
3. Review this deployment guide
4. Check GitHub Issues

For questions:
- Email: support@legalai.in
- GitHub Discussions: github.com/your-repo/discussions

---

## Next Steps After Deployment

1. **Add Content**:
   - Populate vector store with legal documents
   - Add FAQ content
   - Create tutorial videos

2. **Marketing**:
   - Share on social media
   - Reach out to law firms
   - Create demo videos

3. **Gather Feedback**:
   - User testing
   - Feedback forms
   - Usage analytics

4. **Iterate**:
   - Fix bugs
   - Add features
   - Improve AI responses

---

## Success! 🎉

Your Indian Legal AI platform is now live and ready to help legal professionals and citizens!

**Frontend**: https://your-app.vercel.app
**Backend API**: https://your-backend.onrender.com
**API Docs**: https://your-backend.onrender.com/docs
