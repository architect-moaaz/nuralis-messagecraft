#!/usr/bin/env python3
"""
Simple script to run OAuth migration
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Run the OAuth migration"""
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return
    
    # Connect to database
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔄 Applying OAuth migration...")
        
        # Add columns
        cursor.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR;
        """)
        print("✅ Added google_id column")
        
        cursor.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR DEFAULT 'local';
        """)
        print("✅ Added auth_provider column")
        
        cursor.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;
        """)
        print("✅ Added last_login column")
        
        # Make password_hash optional
        cursor.execute("""
            ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;
        """)
        print("✅ Made password_hash optional")
        
        # Add indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
        """)
        print("✅ Added google_id index")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_auth_provider ON users(auth_provider);
        """)
        print("✅ Added auth_provider index")
        
        # Add unique constraint for google_id (only if not exists)
        try:
            cursor.execute("""
                ALTER TABLE users ADD CONSTRAINT unique_google_id UNIQUE(google_id);
            """)
            print("✅ Added unique constraint for google_id")
        except psycopg2.errors.DuplicateObject:
            print("ℹ️  Unique constraint already exists")
        
        # Commit changes
        conn.commit()
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migration()