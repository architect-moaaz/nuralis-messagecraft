#!/usr/bin/env python3
"""
Quick test to verify our database changes are working
"""

import asyncio
from dotenv import load_dotenv
from database import DatabaseManager

load_dotenv()

async def quick_test():
    db = DatabaseManager()
    
    # Create test data
    session_id = await db.save_user_session("demo_user", "Quick test")
    await db.save_messaging_results(session_id, {"test": "data", "parsed": True})
    
    # Test our methods
    print("Testing get_user_playbooks:")
    playbooks = await db.get_user_playbooks("demo_user")
    for p in playbooks:
        if p["id"] == session_id:
            print(f"Results type: {type(p.get('results'))}")
            print(f"Results: {p.get('results')}")
            break
    
    print("\nTesting get_playbook_by_id:")
    single = await db.get_playbook_by_id(session_id, "demo_user")
    print(f"Results type: {type(single.get('results'))}")
    print(f"Results: {single.get('results')}")
    
    # Cleanup
    await db.delete_playbook(session_id, "demo_user")

if __name__ == "__main__":
    asyncio.run(quick_test())