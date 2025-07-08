#!/usr/bin/env python3
"""
Debug API endpoint to see what user is being used
"""

import requests
import json
import asyncio
from dotenv import load_dotenv
from database import DatabaseManager

load_dotenv()

BASE_URL = "http://localhost:8002"

async def create_playbooks_for_different_users():
    """Create playbooks for different user IDs"""
    db = DatabaseManager()
    
    users = ["demo_user", "test_user", "another_user"]
    created_playbooks = {}
    
    for user_id in users:
        # Create a session
        session_id = await db.save_user_session(
            user_id=user_id,
            business_input=f"Test for {user_id}"
        )
        
        # Save results
        test_results = {
            "business_profile": {"company_name": f"Company for {user_id}"},
            "test_user": user_id,
            "debug_info": "API Debug Test"
        }
        
        await db.save_messaging_results(session_id, test_results)
        created_playbooks[user_id] = session_id
        print(f"✅ Created playbook for {user_id}: {session_id}")
    
    return created_playbooks

def test_api_with_different_auth(playbook_id):
    """Test API with different auth scenarios"""
    print(f"\n🧪 Testing API for playbook: {playbook_id}")
    
    # Test 1: No auth header
    print("\n1️⃣ Testing without auth header:")
    response = requests.get(f"{BASE_URL}/api/v1/playbook/{playbook_id}")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Retrieved for user: {data.get('user_id')}")
        print(f"   Results type: {type(data.get('results'))}")
        if isinstance(data.get('results'), dict):
            print(f"   ✅ Results parsed correctly")
            print(f"   Test data: {data['results'].get('test_user')}")
        else:
            print(f"   ❌ Results not parsed: {data.get('results')[:100]}...")
    else:
        print(f"   Error: {response.text}")
    
    # Test 2: With auth header
    print("\n2️⃣ Testing with auth header:")
    headers = {"Authorization": "Bearer token_demo_user_123456"}
    response = requests.get(f"{BASE_URL}/api/v1/playbook/{playbook_id}", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Retrieved for user: {data.get('user_id')}")
        print(f"   Results type: {type(data.get('results'))}")
        if isinstance(data.get('results'), dict):
            print(f"   ✅ Results parsed correctly")
        else:
            print(f"   ❌ Results not parsed")
    else:
        print(f"   Error: {response.text}")

def test_user_playbooks_endpoint():
    """Test the user playbooks endpoint"""
    print("\n3️⃣ Testing user playbooks endpoint:")
    response = requests.get(f"{BASE_URL}/api/v1/user/playbooks")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        playbooks = data.get('playbooks', [])
        print(f"   Found {len(playbooks)} playbooks")
        
        if playbooks:
            first = playbooks[0]
            print(f"   First playbook user: {first.get('user_id')}")
            print(f"   Results type: {type(first.get('results'))}")
            if isinstance(first.get('results'), dict):
                print(f"   ✅ Results parsed in list endpoint")
            else:
                print(f"   ❌ Results not parsed in list endpoint")
    else:
        print(f"   Error: {response.text}")

async def cleanup_test_data(created_playbooks):
    """Clean up test data"""
    db = DatabaseManager()
    for user_id, playbook_id in created_playbooks.items():
        try:
            await db.delete_playbook(playbook_id, user_id)
            print(f"🧹 Cleaned up {playbook_id} for {user_id}")
        except Exception as e:
            print(f"⚠️  Could not clean up {playbook_id}: {e}")

async def main():
    print("🔍 API Debug Test")
    print("=" * 40)
    
    # Create test data
    created_playbooks = await create_playbooks_for_different_users()
    
    # Test with demo_user playbook (most likely to work)
    demo_playbook = created_playbooks.get("demo_user")
    if demo_playbook:
        test_api_with_different_auth(demo_playbook)
    
    # Test user playbooks endpoint
    test_user_playbooks_endpoint()
    
    # Cleanup
    await cleanup_test_data(created_playbooks)

if __name__ == "__main__":
    asyncio.run(main())