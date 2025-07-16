#!/usr/bin/env python3
"""
Apply OAuth migration to add google_id and auth_provider columns
"""
import asyncio
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

async def apply_migration():
    """Apply OAuth migration"""
    # Create Supabase client
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    )
    
    # Read migration file
    with open("migrations/003_add_oauth_columns.sql", "r") as f:
        migration_sql = f.read()
    
    print("Applying OAuth migration...")
    
    # Split SQL statements and execute them
    statements = migration_sql.split(';')
    
    for statement in statements:
        statement = statement.strip()
        if statement:
            try:
                print(f"Executing: {statement[:50]}...")
                result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                print("✅ Success")
            except Exception as e:
                print(f"❌ Error: {e}")
                # Some errors might be expected (like constraint already exists)
                continue
    
    print("Migration completed!")

if __name__ == "__main__":
    asyncio.run(apply_migration())