#!/bin/bash
# MessageCraft Docker Startup Script

echo "🚀 Starting MessageCraft services..."

# Function to wait for a service
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    local max_attempts=30
    local attempt=1

    echo "⏳ Waiting for $service to be ready..."
    
    while ! nc -z $host $port; do
        if [ $attempt -eq $max_attempts ]; then
            echo "❌ $service failed to start after $max_attempts attempts"
            exit 1
        fi
        echo "   Attempt $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "✅ $service is ready!"
}

# Check environment variables
echo "🔍 Checking environment variables..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY is not set. AI features will not work."
fi

if [ -z "$SUPABASE_URL" ]; then
    echo "⚠️  Warning: SUPABASE_URL is not set. Database features will not work."
fi

# Start supervisor
echo "🎯 Starting Supervisor..."
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf &

# Wait for services to be ready
wait_for_service localhost 8000 "Backend API"
wait_for_service localhost 80 "Frontend (Nginx)"

echo "✨ MessageCraft is ready!"
echo "📍 Frontend: http://localhost"
echo "📍 Backend API: http://localhost:8000"
echo "📍 Health check: http://localhost/health"

# Keep the container running
tail -f /dev/null