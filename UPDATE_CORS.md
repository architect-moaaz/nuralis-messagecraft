# CORS Configuration Update Instructions

## Current Setup
- Frontend: https://nuralis-messagecraft-erpbjssnd-athergens-projects.vercel.app/
- Backend: http://216.48.184.243:56001/

## Steps to Fix CORS

1. **Update Environment Variables on your backend server:**
   
   SSH into your server at 216.48.184.243 and update the environment variables:
   
   ```bash
   # Set the FRONTEND_URL to your Vercel deployment
   export FRONTEND_URL=https://nuralis-messagecraft-erpbjssnd-athergens-projects.vercel.app
   ```

2. **If using Docker Compose:**
   
   Update your `.env.production` file on the server with:
   ```
   FRONTEND_URL=https://nuralis-messagecraft-erpbjssnd-athergens-projects.vercel.app
   ```
   
   Then restart the backend:
   ```bash
   docker-compose -f docker-compose.production.yml restart backend
   ```

3. **If running directly with Python:**
   
   Make sure the environment variable is set before starting the server:
   ```bash
   FRONTEND_URL=https://nuralis-messagecraft-erpbjssnd-athergens-projects.vercel.app \
   uvicorn production_api:app --host 0.0.0.0 --port 56001
   ```

## How the CORS Configuration Works

The `production_api.py` uses the `config.py` settings which:
- In production mode: Only allows the `FRONTEND_URL` domain
- In development mode: Allows all origins (`*`)

The backend checks the `ENVIRONMENT` variable. If set to "production", it will only accept requests from the `FRONTEND_URL`.

## Verify CORS is Working

After updating, test from your browser console on the Vercel app:

```javascript
fetch('http://216.48.184.243:56001/api/v1/health')
  .then(response => response.json())
  .then(data => console.log('CORS working!', data))
  .catch(error => console.error('CORS error:', error));
```

## Alternative: Update Frontend to Use HTTPS Backend

For better security, consider deploying your backend with HTTPS using:
- A reverse proxy like Nginx with SSL certificates
- A service like Railway, Render, or Fly.io that provides HTTPS automatically
- Add SSL to your current server using Let's Encrypt

This would allow you to use `https://` for your backend URL instead of `http://`.