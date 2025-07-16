#!/usr/bin/env python3
"""
Simple script to run OAuth migration using Supabase client
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Run the OAuth migration using Supabase client"""
    # Get Supabase configuration
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in environment variables")
        return
    
    # Create Supabase client
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        print("🔄 Applying OAuth migration using Supabase...")
        
        # Check current table structure
        result = supabase.table("users").select("*").limit(1).execute()
        if result.data:
            print("✅ Connected to users table")
            user_columns = list(result.data[0].keys()) if result.data else []
            print(f"Current columns: {user_columns}")
            
            if 'google_id' in user_columns:
                print("✅ google_id column already exists")
            else:
                print("❌ google_id column missing - needs to be added via SQL")
                
            if 'auth_provider' in user_columns:
                print("✅ auth_provider column already exists")
            else:
                print("❌ auth_provider column missing - needs to be added via SQL")
        else:
            print("ℹ️  No users in table yet")
        
        print("\n📋 Manual steps required:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Run the following SQL:")
        print("""
-- Add OAuth columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR;
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR DEFAULT 'local';
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- Make password_hash optional for OAuth users
ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;

-- Add indexes for OAuth
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
CREATE INDEX IF NOT EXISTS idx_users_auth_provider ON users(auth_provider);

-- Add unique constraint for google_id
ALTER TABLE users ADD CONSTRAINT unique_google_id UNIQUE(google_id);
        """)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_migration()