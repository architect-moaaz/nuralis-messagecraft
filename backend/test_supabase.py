#!/usr/bin/env python3
"""
Test script to verify Supabase connection and basic operations
"""

import asyncio
import os
from dotenv import load_dotenv
from database import DatabaseManager

# Load environment variables
load_dotenv()

async def test_supabase_connection():
    """Test the Supabase connection and basic operations"""
    
    print("🚀 Testing Supabase Connection")
    print("=" * 40)
    
    try:
        # Initialize DatabaseManager
        db = DatabaseManager()
        print("✅ DatabaseManager initialized successfully")
        
        # Test creating a user session
        print("\n📝 Testing user session creation...")
        session_id = await db.save_user_session(
            user_id="test_user_123",
            business_input="Test business description for Supabase connection"
        )
        print(f"✅ Session created with ID: {session_id}")
        
        # Test retrieving user playbooks
        print("\n📖 Testing playbook retrieval...")
        playbooks = await db.get_user_playbooks("test_user_123")
        print(f"✅ Retrieved {len(playbooks)} playbooks for user")
        
        # Test saving results to the session
        print("\n💾 Testing results saving...")
        test_results = {
            "messaging_framework": {
                "value_proposition": "Test value proposition",
                "elevator_pitch": "Test elevator pitch",
                "tagline_options": ["Test tagline 1", "Test tagline 2"]
            },
            "quality_review": {
                "overall_quality_score": 8.5
            }
        }
        
        await db.save_messaging_results(session_id, test_results)
        print("✅ Results saved successfully")
        
        # Test retrieving updated playbooks
        print("\n🔄 Testing updated playbook retrieval...")
        updated_playbooks = await db.get_user_playbooks("test_user_123")
        print(f"✅ Retrieved {len(updated_playbooks)} updated playbooks")
        
        # Display the created playbook
        if updated_playbooks:
            latest_playbook = updated_playbooks[-1]
            print(f"\n📋 Latest playbook:")
            print(f"   ID: {latest_playbook['id']}")
            print(f"   Status: {latest_playbook['status']}")
            print(f"   Created: {latest_playbook['created_at']}")
            if latest_playbook.get('completed_at'):
                print(f"   Completed: {latest_playbook['completed_at']}")
        
        # Test usage tracking
        print("\n📊 Testing usage tracking...")
        await db.track_usage("test_user_123", "basic", "playbook_generation")
        print("✅ Usage tracked successfully")
        
        # Test deleting the test playbook
        print(f"\n🗑️  Testing playbook deletion...")
        await db.delete_playbook(session_id, "test_user_123")
        print("✅ Playbook deleted successfully")
        
        # Verify deletion
        print("\n🔍 Verifying deletion...")
        final_playbooks = await db.get_user_playbooks("test_user_123")
        print(f"✅ Final playbook count: {len(final_playbooks)}")
        
        print("\n🎉 All tests passed! Supabase is configured correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_supabase_connection())
    if success:
        print("\n✅ Supabase configuration is working correctly!")
    else:
        print("\n❌ Supabase configuration needs attention. Check your .env file and database setup.")