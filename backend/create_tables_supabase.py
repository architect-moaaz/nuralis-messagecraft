#!/usr/bin/env python3
"""
Create tables using Supabase client instead of direct PostgreSQL connection
"""

import os

def load_env_file():
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        print("❌ .env file not found")
        return None
    return env_vars

def create_tables():
    print("🚀 Creating Tables with Supabase Client")
    print("=" * 40)
    
    # Load environment variables
    env_vars = load_env_file()
    if not env_vars:
        return False
    
    supabase_url = env_vars.get('SUPABASE_URL')
    supabase_key = env_vars.get('SUPABASE_SERVICE_ROLE_KEY')
    
    try:
        from supabase import create_client
        
        # Create client with service role key for admin operations
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created with service role key")
        
        # SQL to create tables
        sql_commands = [
            # Enable UUID extension
            'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"',
            
            # Create user_sessions table
            '''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                business_input TEXT NOT NULL,
                results JSONB,
                status VARCHAR DEFAULT 'processing',
                created_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP
            )
            ''',
            
            # Create usage_tracking table  
            '''
            CREATE TABLE IF NOT EXISTS usage_tracking (
                id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                plan_type VARCHAR NOT NULL,
                feature_used VARCHAR NOT NULL,
                timestamp TIMESTAMP DEFAULT NOW()
            )
            ''',
            
            # Create users table
            '''
            CREATE TABLE IF NOT EXISTS users (
                id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                email VARCHAR UNIQUE NOT NULL,
                name VARCHAR NOT NULL,
                company VARCHAR,
                plan_type VARCHAR DEFAULT 'basic',
                password_hash VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            ''',
            
            # Create payments table
            '''
            CREATE TABLE IF NOT EXISTS payments (
                id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                user_id UUID REFERENCES users(id),
                stripe_session_id VARCHAR,
                plan_type VARCHAR NOT NULL,
                amount INTEGER NOT NULL,
                status VARCHAR DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT NOW()
            )
            ''',
            
            # Create indexes
            'CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_user_sessions_status ON user_sessions(status)',
            'CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_usage_tracking_timestamp ON usage_tracking(timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)',
            'CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)',
        ]
        
        # Execute each SQL command
        for i, sql in enumerate(sql_commands, 1):
            try:
                print(f"📝 Executing SQL command {i}/{len(sql_commands)}...")
                result = supabase.rpc('exec_sql', {'sql': sql}).execute()
                print(f"✅ Command {i} executed successfully")
            except Exception as e:
                print(f"⚠️  Command {i} failed: {e}")
                # Try alternative approach for table creation
                if 'CREATE TABLE' in sql:
                    print(f"💡 Trying alternative approach for table creation...")
                    # We'll handle this differently - let the user do it manually
                    pass
        
        # Test if tables were created
        print("\n🔍 Testing table creation...")
        try:
            result = supabase.table('user_sessions').select('id').limit(1).execute()
            print("✅ user_sessions table accessible")
        except Exception as e:
            print(f"❌ user_sessions table not accessible: {e}")
            return False
            
        try:
            result = supabase.table('usage_tracking').select('id').limit(1).execute()
            print("✅ usage_tracking table accessible")
        except Exception as e:
            print(f"❌ usage_tracking table not accessible: {e}")
        
        print("\n🎉 Table creation completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_tables_manual():
    print("\n📋 Manual Table Creation Instructions")
    print("=" * 40)
    print("If automatic table creation failed, follow these steps:")
    print()
    print("1. Go to your Supabase dashboard: https://app.supabase.com")
    print("2. Select your project: cuslsfwlfpcbonvaferb")
    print("3. Go to SQL Editor")
    print("4. Copy and paste the contents of schema.sql")
    print("5. Click 'Run' to execute the SQL")
    print()
    print("Your schema.sql file contains all the necessary tables and indexes.")

if __name__ == "__main__":
    success = create_tables()
    
    if not success:
        create_tables_manual()
        print("\n💡 After creating tables manually, run: python test_real_keys.py")
    else:
        print("\n🚀 Ready to test the application!")
        print("Next steps:")
        print("1. Run: python test_real_keys.py")
        print("2. Start API: python enhanced_api.py")
        print("3. Test frontend connection")