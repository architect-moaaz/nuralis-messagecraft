#!/usr/bin/env python3
"""
Test script to verify the DELETE endpoint works correctly
"""

import requests
import json

def test_delete_endpoint():
    """Test the playbook deletion functionality"""
    
    # Base URL for the API
    base_url = "http://localhost:8000"
    
    try:
        print("🧪 Testing DELETE /api/v1/playbook/{id} endpoint...")
        
        # First, get the list of playbooks to find one to delete
        print("\n1. Getting existing playbooks...")
        response = requests.get(f"{base_url}/api/v1/user/playbooks")
        
        if response.status_code == 200:
            playbooks = response.json().get("playbooks", [])
            print(f"Found {len(playbooks)} playbooks")
            
            if playbooks:
                # Take the first playbook for testing
                test_playbook = playbooks[0]
                playbook_id = test_playbook["id"]
                print(f"Testing deletion of playbook: {playbook_id}")
                
                # Attempt to delete the playbook
                print("\n2. Attempting to delete playbook...")
                delete_response = requests.delete(f"{base_url}/api/v1/playbook/{playbook_id}")
                
                if delete_response.status_code == 200:
                    result = delete_response.json()
                    print(f"✅ Playbook deleted successfully: {result}")
                    
                    # Verify the playbook is gone
                    print("\n3. Verifying playbook is deleted...")
                    verify_response = requests.get(f"{base_url}/api/v1/user/playbooks")
                    
                    if verify_response.status_code == 200:
                        remaining_playbooks = verify_response.json().get("playbooks", [])
                        deleted_ids = [p["id"] for p in remaining_playbooks]
                        
                        if playbook_id not in deleted_ids:
                            print("✅ Playbook successfully removed from list")
                            print(f"Remaining playbooks: {len(remaining_playbooks)}")
                        else:
                            print("❌ Playbook still appears in list")
                    else:
                        print(f"❌ Error verifying deletion: {verify_response.status_code}")
                        
                else:
                    print(f"❌ Delete failed with status: {delete_response.status_code}")
                    print(f"Response: {delete_response.text}")
                    
            else:
                print("⚠️ No playbooks found to test deletion")
                print("Create a playbook first, then run this test")
                
        else:
            print(f"❌ Error getting playbooks: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: python3 simple_langgraph_api.py")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def test_delete_nonexistent():
    """Test deleting a non-existent playbook"""
    base_url = "http://localhost:8000"
    
    try:
        print("\n🧪 Testing deletion of non-existent playbook...")
        fake_id = "nonexistent-playbook-id"
        
        response = requests.delete(f"{base_url}/api/v1/playbook/{fake_id}")
        
        if response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent playbook")
        else:
            print(f"❌ Expected 404, got {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🎯 Testing Playbook Deletion API")
    print("=" * 50)
    
    test_delete_endpoint()
    test_delete_nonexistent()
    
    print("\n" + "=" * 50)
    print("🏁 Delete endpoint testing complete!")