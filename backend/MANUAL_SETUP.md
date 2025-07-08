# Manual Supabase Setup Instructions

## ✅ Connection Status
Your Supabase client connection is working! The only issue is that the database tables don't exist yet.

## 🔧 Create Tables Manually

Since the direct PostgreSQL connection has DNS issues, please create the tables manually:

### Step 1: Go to Supabase SQL Editor
1. Go to: https://app.supabase.com
2. Select your project: `cuslsfwlfpcbonvaferb`
3. Click on **SQL Editor** in the left menu
4. Click **New Query**

### Step 2: Copy and Paste This SQL

```sql
-- MessageCraft Database Schema
-- Use this with Supabase or any PostgreSQL database

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User sessions table
CREATE TABLE user_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    business_input TEXT NOT NULL,
    results JSONB,
    status VARCHAR DEFAULT 'processing',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Usage tracking table
CREATE TABLE usage_tracking (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    plan_type VARCHAR NOT NULL,
    feature_used VARCHAR NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Users table (if not using external auth)
CREATE TABLE users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    company VARCHAR,
    plan_type VARCHAR DEFAULT 'basic',
    password_hash VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Payments table
CREATE TABLE payments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    stripe_session_id VARCHAR,
    plan_type VARCHAR NOT NULL,
    amount INTEGER NOT NULL,
    status VARCHAR DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_status ON user_sessions(status);
CREATE INDEX idx_usage_tracking_user_id ON usage_tracking(user_id);
CREATE INDEX idx_usage_tracking_timestamp ON usage_tracking(timestamp);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_payments_user_id ON payments(user_id);

-- Row Level Security (RLS) policies for Supabase
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- Policies (adjust based on your auth setup)
CREATE POLICY "Users can view own sessions" ON user_sessions
    FOR SELECT USING (user_id = auth.uid()::text);

CREATE POLICY "Users can insert own sessions" ON user_sessions
    FOR INSERT WITH CHECK (user_id = auth.uid()::text);

CREATE POLICY "Users can update own sessions" ON user_sessions
    FOR UPDATE USING (user_id = auth.uid()::text);

CREATE POLICY "Users can view own usage" ON usage_tracking
    FOR SELECT USING (user_id = auth.uid()::text);

CREATE POLICY "Users can insert own usage" ON usage_tracking
    FOR INSERT WITH CHECK (user_id = auth.uid()::text);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for users table
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Step 3: Run the SQL
1. Paste the SQL into the SQL Editor
2. Click **Run** or press Ctrl+Enter
3. You should see "Success. No rows returned" - this is normal!

## 🧪 Test the Setup

After creating the tables, run the test:

```bash
# Make sure you're in your virtual environment
source env/bin/activate

# Test the connection
python test_real_keys.py
```

You should see:
- ✅ Supabase Client: Working
- ✅ user_sessions table accessible

## 🚀 Start the Application

Once the tables are created:

```bash
# Start the enhanced API server
python enhanced_api.py
```

The server will run on: http://localhost:8002

## 🎯 Alternative: Disable RLS Temporarily

If you get authentication errors, you can temporarily disable Row Level Security:

```sql
ALTER TABLE user_sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE usage_tracking DISABLE ROW LEVEL SECURITY;
```

⚠️ **Warning**: Only do this for development/testing. Enable RLS for production!

## 🔍 Verify Tables Were Created

After running the SQL, you can verify the tables exist:

1. Go to **Table Editor** in Supabase
2. You should see: `user_sessions`, `usage_tracking`, `users`, `payments`
3. Or run this test query in SQL Editor: `SELECT * FROM user_sessions LIMIT 1;`

Your MessageCraft application is now ready to use Supabase! 🎉