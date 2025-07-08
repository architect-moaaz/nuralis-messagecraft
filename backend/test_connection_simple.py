#!/usr/bin/env python3
"""
Simple connection test without external dependencies
"""

import os

# Manual environment loading (replace with your actual keys)
SUPABASE_URL = "https://cuslsfwlfpcbonvaferb.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN1c2xzZndsZnBjYm9udmFmZXJiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzY5MzE3OTMsImV4cCI6MjA1MjUwNzc5M30.Q3oXN8QhmnG0PQe0_J2vBEqQCaBYEO3YX77R5iajFhk"

def test_basic_connection():
    print("🔧 Basic Connection Test")
    print("=" * 30)
    
    try:
        from supabase import create_client
        print("✅ Supabase package imported successfully")
        
        # Create client
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        print("✅ Supabase client created")
        
        # Test a simple query
        result = supabase.table("user_sessions").select("count").execute()
        print("✅ Database query executed successfully")
        print(f"📊 Result: {result}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing supabase package: {e}")
        print("💡 Install with: pip install supabase")
        return False
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("💡 Check your API keys in the Supabase dashboard")
        return False

if __name__ == "__main__":
    print("🚀 MessageCraft Supabase Connection Test")
    print()
    print("⚠️  WARNING: Using example API keys!")
    print("📝 Update the keys in this file with your real ones from:")
    print("   https://app.supabase.com → Settings → API")
    print()
    
    success = test_basic_connection()
    
    if success:
        print("\n✅ Basic connection works!")
        print("📋 Next steps:")
        print("1. Update .env with your real API keys")
        print("2. Run: python3 init_database.py")
        print("3. Start API: python3 enhanced_api.py")
    else:
        print("\n❌ Connection failed - check your API keys")