# Railway Deployment Guide

This guide explains how to deploy MessageCraft on Railway with both backend and frontend services.

## 🚂 Railway Configuration

### Project Structure
```
messagecraft/
├── railway.json                 # Root configuration
├── backend/
│   ├── railway.json            # Backend service config
│   ├── Dockerfile              # Backend container
│   └── enhanced_api.py         # FastAPI application
├── frontend/
│   ├── railway.json            # Frontend service config
│   ├── Dockerfile              # Frontend container
│   └── nginx.conf              # Nginx configuration
└── RAILWAY_DEPLOYMENT.md       # This guide
```

## 🔧 Setup Instructions

### 1. Prerequisites
- Railway account: https://railway.app
- GitHub repository with MessageCraft code
- Environment variables ready

### 2. Deploy Backend Service

1. **Create New Project** on Railway
2. **Connect GitHub Repository**
3. **Add Backend Service:**
   - Service name: `messagecraft-backend`
   - Root directory: `/backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn enhanced_api:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables:**
   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   DATABASE_URL=postgresql://postgres:password@host:5432/postgres
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ENVIRONMENT=production
   PORT=8000
   ```

### 3. Deploy Frontend Service

1. **Add Frontend Service:**
   - Service name: `messagecraft-frontend`
   - Root directory: `/frontend`
   - Build command: `npm ci && npm run build`
   - Start command: Uses Dockerfile with Nginx

2. **Set Environment Variables:**
   ```env
   VITE_API_URL=https://your-backend-service.railway.app
   NODE_ENV=production
   PORT=80
   ```

### 4. Configure Custom Domains (Optional)

1. **Backend Domain:**
   - Add custom domain: `api.yourdomain.com`
   - Update frontend API URL

2. **Frontend Domain:**
   - Add custom domain: `app.yourdomain.com`
   - Update CORS settings in backend

## 🔄 Deployment Process

### Automatic Deployment
Railway automatically deploys when you push to the main branch:

```bash
git add .
git commit -m "Deploy to Railway"
git push origin main
```

### Manual Deployment
1. Go to Railway dashboard
2. Select your project
3. Click "Deploy" on each service

## 🏗️ Service Configuration

### Backend Service (FastAPI)
- **Framework**: FastAPI with Uvicorn
- **Port**: 8000 (automatically assigned by Railway)
- **Health Check**: `/health` endpoint
- **Auto-scaling**: Enabled
- **Restart Policy**: ON_FAILURE

### Frontend Service (React + Nginx)
- **Framework**: React with Vite build
- **Server**: Nginx
- **Port**: 80
- **SPA Routing**: Configured for client-side routing
- **Static Assets**: Cached with optimal headers

## 🔒 Environment Variables

### Required Backend Variables
```env
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
DATABASE_URL=postgresql://...

# AI
ANTHROPIC_API_KEY=sk-ant-api03-...

# App
ENVIRONMENT=production
PORT=$PORT
```

### Required Frontend Variables
```env
# API Configuration
VITE_API_URL=https://your-backend.railway.app

# Build
NODE_ENV=production
PORT=80
```

## 🚨 Security Configuration

### CORS Settings
Update backend `enhanced_api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.railway.app",
        "https://app.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Protection
- Never commit `.env` files
- Use Railway's environment variable system
- Rotate API keys regularly

## 📊 Monitoring & Health Checks

### Health Endpoints
- **Backend**: `https://your-backend.railway.app/health`
- **Frontend**: `https://your-frontend.railway.app/health`

### Logging
Railway provides built-in logging:
1. Go to service dashboard
2. Click "Logs" tab
3. Monitor real-time application logs

## 🔧 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check dependency versions in `requirements.txt`/`package.json`
   - Verify build commands in `railway.json`

2. **Environment Variables**
   - Ensure all required variables are set
   - Check variable names match exactly

3. **Port Configuration**
   - Backend: Use `$PORT` environment variable
   - Frontend: Nginx configured for port 80

4. **Database Connection**
   - Verify Supabase URL and keys
   - Check database permissions

### Debugging Steps
1. **Check Logs**: Railway dashboard > Service > Logs
2. **Test Health**: Visit `/health` endpoints
3. **Environment**: Verify all variables are set
4. **Build Process**: Check build and deploy logs

## 🚀 Performance Optimization

### Backend Optimizations
- **Caching**: Implement Redis for session caching
- **Database**: Use connection pooling
- **API**: Add rate limiting and compression

### Frontend Optimizations
- **CDN**: Railway provides global CDN
- **Caching**: Static assets cached for 1 year
- **Compression**: Gzip enabled for all text content

## 💰 Cost Optimization

### Railway Pricing
- **Hobby Plan**: $5/month per service
- **Pro Plan**: Usage-based pricing
- **Sleep Mode**: Services sleep after inactivity (Hobby)

### Resource Management
- Monitor usage in Railway dashboard
- Optimize build times with caching
- Use appropriate service sizing

## 📞 Support

### Railway Resources
- **Documentation**: https://docs.railway.app
- **Discord**: https://discord.gg/railway
- **GitHub**: https://github.com/railwayapp

### MessageCraft Support
- **Repository**: Check GitHub issues
- **Documentation**: Review project README
- **Logs**: Use Railway logging for debugging

---

## Quick Deploy Commands

```bash
# 1. Ensure your code is committed
git add .
git commit -m "Prepare for Railway deployment"
git push origin main

# 2. Railway will automatically deploy both services
# 3. Set environment variables in Railway dashboard
# 4. Test both services using health endpoints
```

Your MessageCraft application will be live at:
- **Backend**: `https://your-backend.railway.app`
- **Frontend**: `https://your-frontend.railway.app`