#!/usr/bin/env python3
"""
Simple test script to verify Supabase connection using the Supabase client
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def test_supabase_simple():
    """Test basic Supabase connection"""
    
    print("🚀 Testing Supabase Connection (Simple)")
    print("=" * 40)
    
    try:
        # Get environment variables
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Missing SUPABASE_URL or SUPABASE_KEY in environment")
            return False
        
        print(f"🔗 Connecting to: {supabase_url}")
        
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        
        # Test connection by listing tables
        print("\n📋 Checking existing tables...")
        try:
            # Try to query the user_sessions table (this will fail if table doesn't exist)
            result = supabase.table("user_sessions").select("id").limit(1).execute()
            print("✅ user_sessions table exists")
        except Exception as e:
            print(f"⚠️  user_sessions table may not exist: {e}")
        
        # Test basic insert/select/delete operations
        print("\n📝 Testing basic operations...")
        
        # Insert test data
        test_data = {
            "user_id": "test_user_simple",
            "business_input": "Test business for simple connection test",
            "status": "processing"
        }
        
        try:
            insert_result = supabase.table("user_sessions").insert(test_data).execute()
            session_id = insert_result.data[0]["id"]
            print(f"✅ Test session created: {session_id}")
            
            # Query the data back
            query_result = supabase.table("user_sessions").select("*").eq("user_id", "test_user_simple").execute()
            print(f"✅ Retrieved {len(query_result.data)} test sessions")
            
            # Delete the test data
            delete_result = supabase.table("user_sessions").delete().eq("id", session_id).execute()
            print("✅ Test session deleted")
            
        except Exception as e:
            print(f"❌ Error with basic operations: {e}")
            return False
        
        print("\n🎉 All basic tests passed! Supabase connection is working.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_supabase_simple()
    if success:
        print("\n✅ Supabase is configured correctly!")
        print("\n📋 Next steps:")
        print("1. Install requirements: pip install -r requirements.txt")
        print("2. Run enhanced API: python3 enhanced_api.py")
        print("3. Test with frontend at http://localhost:3000")
    else:
        print("\n❌ Please check your Supabase configuration in .env file")