#!/bin/bash
# Quick deployment script to fix CORS on your server

echo "=== MessageCraft CORS Fix Deployment ==="
echo "This script will help you fix CORS on your backend server"
echo ""
echo "Run these commands on your server (216.48.184.243):"
echo ""
echo "1. First, SSH into your server:"
echo "   ssh your-username@216.48.184.243"
echo ""
echo "2. Navigate to your backend directory and create the environment file:"
echo "   cd /path/to/messagecraft/backend"
echo ""
echo "3. Create or update .env.production with:"
cat << 'EOF'
cat > .env.production << 'ENVEOF'
ENVIRONMENT=production
FRONTEND_URL=https://nuralis-messagecraft-erpbjssnd-athergens-projects.vercel.app
SECRET_KEY=your-secret-key-here
ANTHROPIC_API_KEY=your-anthropic-key
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DATABASE_URL=your-database-url
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://216.48.184.243:56001/api/v1/auth/google/callback
ENVEOF
EOF
echo ""
echo "4. If using Docker, restart the container:"
echo "   docker-compose -f docker-compose.production.yml down"
echo "   docker-compose -f docker-compose.production.yml up -d"
echo ""
echo "5. If running Python directly, stop the current process and run:"
echo "   export FRONTEND_URL=https://nuralis-messagecraft-erpbjssnd-athergens-projects.vercel.app"
echo "   export ENVIRONMENT=production"
echo "   uvicorn production_api:app --host 0.0.0.0 --port 56001"
echo ""
echo "6. Or use the quick fix script (temporary solution):"
echo "   python fix_cors_quick.py"