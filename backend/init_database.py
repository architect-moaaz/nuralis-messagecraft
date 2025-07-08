#!/usr/bin/env python3
"""
Database initialization script for MessageCraft
Applies the schema.sql to your Supabase database
"""

import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def init_database():
    """Initialize the database with the required schema"""
    
    # Get database connection details
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Connect to the database
        print("🔌 Connecting to Supabase database...")
        conn = await asyncpg.connect(database_url)
        
        # Read the schema file
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        print("📝 Applying database schema...")
        
        # Execute the schema
        await conn.execute(schema_sql)
        
        print("✅ Database schema applied successfully!")
        
        # Verify tables were created
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND table_name IN ('user_sessions', 'usage_tracking', 'users', 'payments')
        """)
        
        print(f"📊 Created tables: {[table['table_name'] for table in tables]}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

async def test_connection():
    """Test the database connection and check existing tables"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        print("🧪 Testing database connection...")
        conn = await asyncpg.connect(database_url)
        
        # Check existing tables
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """)
        
        print(f"📋 Existing tables: {[table['table_name'] for table in tables]}")
        
        # Check if our required tables exist
        required_tables = {'user_sessions', 'usage_tracking', 'users', 'payments'}
        existing_table_names = {table['table_name'] for table in tables}
        missing_tables = required_tables - existing_table_names
        
        if missing_tables:
            print(f"⚠️  Missing tables: {missing_tables}")
            return False
        else:
            print("✅ All required tables exist!")
            return True
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MessageCraft Database Initialization")
    print("=" * 40)
    
    # Test connection first
    connection_ok = asyncio.run(test_connection())
    
    if not connection_ok:
        print("\n🔧 Initializing database schema...")
        success = asyncio.run(init_database())
        if success:
            print("\n✅ Database initialization completed!")
        else:
            print("\n❌ Database initialization failed!")
    else:
        print("\n✅ Database is already set up correctly!")