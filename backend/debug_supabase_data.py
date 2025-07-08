#!/usr/bin/env python3
"""
Debug Supabase data storage format
"""

import asyncio
import json
from dotenv import load_dotenv
from database import DatabaseManager

load_dotenv()

async def debug_data_format():
    """Check how data is actually stored in Supabase"""
    print("🔍 Debugging Supabase Data Format")
    print("=" * 50)
    
    db = DatabaseManager()
    
    # Create a test session and save results
    session_id = await db.save_user_session(
        user_id="debug_user",
        business_input="Debug test"
    )
    
    test_results = {"test": "data", "number": 123}
    await db.save_messaging_results(session_id, test_results)
    
    # Check raw data from Supabase
    print("\n1️⃣ Raw data from Supabase:")
    raw_result = db.supabase.table("user_sessions").select("*").eq("id", session_id).execute()
    raw_data = raw_result.data[0] if raw_result.data else None
    
    if raw_data:
        print(f"   Results field type: {type(raw_data.get('results'))}")
        print(f"   Results content: {raw_data.get('results')}")
        
        # Check if it's already parsed
        if isinstance(raw_data.get('results'), dict):
            print("   ✅ Supabase returns JSONB as dict (no parsing needed)")
        elif isinstance(raw_data.get('results'), str):
            print("   📝 Supabase returns JSONB as string (parsing needed)")
            try:
                parsed = json.loads(raw_data['results'])
                print(f"   ✅ String can be parsed: {parsed}")
            except:
                print("   ❌ String cannot be parsed")
    
    # Test our get methods
    print("\n2️⃣ Testing get_user_playbooks:")
    playbooks = await db.get_user_playbooks("debug_user")
    if playbooks:
        print(f"   Results type: {type(playbooks[0].get('results'))}")
        print(f"   Results: {playbooks[0].get('results')}")
    
    print("\n3️⃣ Testing get_playbook_by_id:")
    single = await db.get_playbook_by_id(session_id, "debug_user")
    if single:
        print(f"   Results type: {type(single.get('results'))}")
        print(f"   Results: {single.get('results')}")
    
    # Cleanup
    await db.delete_playbook(session_id, "debug_user")
    print("\n🧹 Cleaned up debug data")

if __name__ == "__main__":
    asyncio.run(debug_data_format())