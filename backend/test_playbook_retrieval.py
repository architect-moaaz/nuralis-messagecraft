#!/usr/bin/env python3
"""
Test playbook retrieval with JSON parsing
"""

import asyncio
import json
from dotenv import load_dotenv
from database import DatabaseManager

# Load environment variables
load_dotenv()

async def test_playbook_storage_and_retrieval():
    """Test storing and retrieving playbooks with JSON data"""
    print("🧪 Testing Playbook Storage and Retrieval")
    print("=" * 50)
    
    db = DatabaseManager()
    test_user_id = "test_user_123"
    
    try:
        # 1. Create a test session
        print("\n1️⃣ Creating test session...")
        session_id = await db.save_user_session(
            user_id=test_user_id,
            business_input="Test business for playbook retrieval"
        )
        print(f"✅ Session created: {session_id}")
        
        # 2. Save test results
        print("\n2️⃣ Saving test results...")
        test_results = {
            "business_profile": {
                "company_name": "Test Company",
                "industry": "Technology",
                "target_audience": "B2B SaaS companies"
            },
            "messaging_framework": {
                "value_proposition": "We help companies save time",
                "elevator_pitch": "Our platform automates workflows",
                "tagline_options": ["Automate Everything", "Work Smarter"]
            },
            "quality_review": {
                "overall_quality_score": "9.2",
                "quality_percentage": "92%"
            }
        }
        
        await db.save_messaging_results(session_id, test_results)
        print("✅ Results saved successfully")
        
        # 3. Retrieve all playbooks
        print("\n3️⃣ Retrieving all playbooks...")
        all_playbooks = await db.get_user_playbooks(test_user_id)
        print(f"✅ Found {len(all_playbooks)} playbooks")
        
        if all_playbooks:
            playbook = all_playbooks[0]
            print(f"\n📋 First playbook details:")
            print(f"   ID: {playbook['id']}")
            print(f"   Status: {playbook['status']}")
            print(f"   Results type: {type(playbook.get('results'))}")
            
            if isinstance(playbook.get('results'), dict):
                print("   ✅ Results are properly parsed as dict")
                print(f"   Company name: {playbook['results'].get('business_profile', {}).get('company_name')}")
            else:
                print("   ❌ Results are not parsed!")
        
        # 4. Test single playbook retrieval
        print("\n4️⃣ Testing single playbook retrieval...")
        single_playbook = await db.get_playbook_by_id(session_id, test_user_id)
        
        if single_playbook:
            print("✅ Single playbook retrieved")
            print(f"   Results type: {type(single_playbook.get('results'))}")
            
            if isinstance(single_playbook.get('results'), dict):
                print("   ✅ Results are properly parsed")
                quality = single_playbook['results'].get('quality_review', {})
                print(f"   Quality score: {quality.get('overall_quality_score')}")
                print(f"   Quality percentage: {quality.get('quality_percentage')}")
            else:
                print("   ❌ Results parsing failed")
        
        # 5. Test API endpoint simulation
        print("\n5️⃣ Testing API response format...")
        api_response = json.dumps(single_playbook, indent=2, default=str)
        print("✅ API response can be serialized to JSON")
        print(f"   Response preview: {api_response[:200]}...")
        
        # Cleanup
        print("\n6️⃣ Cleaning up test data...")
        await db.delete_playbook(session_id, test_user_id)
        print("✅ Test playbook deleted")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def check_existing_playbooks():
    """Check any existing playbooks in the database"""
    print("\n📊 Checking existing playbooks...")
    
    db = DatabaseManager()
    
    # Check for demo user playbooks
    demo_playbooks = await db.get_user_playbooks("demo_user")
    print(f"Found {len(demo_playbooks)} playbooks for demo_user")
    
    if demo_playbooks:
        for i, playbook in enumerate(demo_playbooks[:3]):  # Show first 3
            print(f"\n📄 Playbook {i+1}:")
            print(f"   ID: {playbook['id']}")
            print(f"   Status: {playbook['status']}")
            print(f"   Created: {playbook['created_at']}")
            print(f"   Results parsed: {isinstance(playbook.get('results'), dict)}")

if __name__ == "__main__":
    asyncio.run(test_playbook_storage_and_retrieval())
    asyncio.run(check_existing_playbooks())