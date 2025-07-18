#!/usr/bin/env python3
"""
Script to apply the generation stages migration (004)
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def apply_generation_stages_migration():
    """Apply the generation stages migration"""
    # Get Supabase configuration
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in environment variables")
        return
    
    # Create Supabase client
    supabase = create_client(supabase_url, supabase_key)
    
    # Read the migration file
    migration_file = "migrations/004_add_generation_stages.sql"
    
    try:
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print("🔄 Applying generation stages migration...")
        print(f"📁 Reading from: {migration_file}")
        
        # Split the SQL into individual statements
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        print(f"📋 Found {len(statements)} SQL statements to execute")
        
        for i, statement in enumerate(statements, 1):
            if not statement:
                continue
                
            try:
                print(f"⏳ Executing statement {i}/{len(statements)}...")
                # Use rpc to execute raw SQL
                result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                print(f"✅ Statement {i} executed successfully")
            except Exception as e:
                # If rpc doesn't work, try direct table operations for specific statements
                if "CREATE TABLE" in statement and "generation_stages" in statement:
                    print(f"⚠️  Direct SQL execution failed for statement {i}, this is normal for Supabase")
                    print("📋 You need to run this migration manually in Supabase SQL Editor")
                elif "CREATE OR REPLACE FUNCTION" in statement:
                    print(f"⚠️  Function creation failed for statement {i}, this is normal for Supabase")
                    print("📋 You need to run this migration manually in Supabase SQL Editor")
                else:
                    print(f"❌ Error executing statement {i}: {e}")
        
        print("\n📋 To complete the migration manually:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the contents of migrations/004_add_generation_stages.sql")
        print("4. Execute the SQL")
        
        # Test if the function exists by trying to call it
        print("\n🧪 Testing if get_generation_progress function exists...")
        try:
            test_result = supabase.rpc('get_generation_progress', {
                'p_session_id': '00000000-0000-0000-0000-000000000000'
            }).execute()
            print("✅ get_generation_progress function exists and is callable")
        except Exception as e:
            print(f"❌ get_generation_progress function not found or not callable: {e}")
            print("📋 Please run the migration manually in Supabase SQL Editor")
        
    except FileNotFoundError:
        print(f"❌ Migration file not found: {migration_file}")
    except Exception as e:
        print(f"❌ Error reading migration file: {e}")

if __name__ == "__main__":
    apply_generation_stages_migration()