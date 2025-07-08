#!/usr/bin/env python3
"""
Debug script to check what playbooks exist in the demo storage
"""

import requests
import json

def debug_playbooks():
    """Debug the playbook storage and deletion"""
    
    base_url = "http://localhost:8002"
    
    try:
        print("🔍 Debugging Playbook Storage")
        print("=" * 50)
        
        # 1. Get all playbooks
        print("1. Getting all playbooks...")
        response = requests.get(f"{base_url}/api/v1/user/playbooks")
        
        if response.status_code == 200:
            data = response.json()
            playbooks = data.get("playbooks", [])
            
            print(f"Found {len(playbooks)} playbooks:")
            print()
            
            for i, playbook in enumerate(playbooks, 1):
                print(f"Playbook {i}:")
                print(f"  ID: {playbook.get('id', 'No ID')}")
                print(f"  Status: {playbook.get('status', 'No status')}")
                print(f"  Created: {playbook.get('created_at', 'No date')}")
                print(f"  User ID: {playbook.get('user_id', 'No user')}")
                print()
                
            if playbooks:
                # Test deletion with the first available playbook
                test_playbook = playbooks[0]
                test_id = test_playbook.get('id')
                
                print(f"2. Testing deletion of playbook: {test_id}")
                
                # Try to delete
                delete_response = requests.delete(f"{base_url}/api/v1/playbook/{test_id}")
                
                print(f"Delete response status: {delete_response.status_code}")
                print(f"Delete response body: {delete_response.text}")
                
                if delete_response.status_code == 200:
                    print("✅ Deletion successful!")
                    
                    # Verify it's gone
                    verify_response = requests.get(f"{base_url}/api/v1/user/playbooks")
                    if verify_response.status_code == 200:
                        remaining = verify_response.json().get("playbooks", [])
                        print(f"3. Remaining playbooks: {len(remaining)}")
                        
                        if not any(p.get('id') == test_id for p in remaining):
                            print("✅ Playbook successfully removed!")
                        else:
                            print("❌ Playbook still exists after deletion")
                else:
                    print(f"❌ Deletion failed: {delete_response.status_code}")
                    
            else:
                print("⚠️ No playbooks found to test deletion")
                print("Create a playbook first using the frontend")
                
        else:
            print(f"❌ Error getting playbooks: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

def test_specific_id():
    """Test the specific ID that was failing"""
    base_url = "http://localhost:8002"
    failing_id = "3894164f-366c-46b8-86cb-b119211f2dc7"
    
    print(f"\n🎯 Testing specific failing ID: {failing_id}")
    print("=" * 50)
    
    try:
        # First check if this ID exists in any playbook
        response = requests.get(f"{base_url}/api/v1/user/playbooks")
        
        if response.status_code == 200:
            playbooks = response.json().get("playbooks", [])
            found = False
            
            for playbook in playbooks:
                if playbook.get('id') == failing_id:
                    found = True
                    print(f"✅ Found playbook with ID {failing_id}")
                    print(f"Details: {json.dumps(playbook, indent=2)}")
                    break
            
            if not found:
                print(f"❌ Playbook with ID {failing_id} not found in storage")
                print("Available IDs:")
                for playbook in playbooks:
                    print(f"  - {playbook.get('id')}")
                    
        # Try to get this specific playbook
        get_response = requests.get(f"{base_url}/api/v1/playbook/{failing_id}")
        print(f"\nDirect GET response: {get_response.status_code}")
        print(f"Response body: {get_response.text}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    debug_playbooks()
    test_specific_id()