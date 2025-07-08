#!/usr/bin/env python3
"""
Test API endpoints with Supabase integration
"""

import requests
import json
import time

BASE_URL = "http://localhost:8002"

def test_registration_and_login():
    """Test complete registration and login flow"""
    print("🧪 Testing Registration and Login with Supabase")
    print("=" * 50)
    
    # Create unique email for this test
    test_email = f"apitest_{int(time.time())}@example.com"
    
    # 1. Register a new user
    print("\n1️⃣ Registering new user...")
    register_data = {
        "email": test_email,
        "password": "securepassword123",
        "name": "API Test User",
        "company": "API Test Company"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Registration successful!")
            print(f"   User ID: {data['user']['id']}")
            print(f"   Token: {data['token'][:20]}...")
            token = data['token']
        else:
            print(f"   ❌ Registration failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # 2. Try to register with same email (should fail)
    print("\n2️⃣ Testing duplicate registration prevention...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print(f"   ✅ Duplicate registration correctly prevented")
        else:
            print(f"   ❌ Duplicate registration not prevented!")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Login with correct credentials
    print("\n3️⃣ Testing login with correct credentials...")
    login_data = {
        "email": test_email,
        "password": "securepassword123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login successful!")
            print(f"   User ID: {data['user']['id']}")
            token = data['token']
        else:
            print(f"   ❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Login with wrong password
    print("\n4️⃣ Testing login with wrong password...")
    wrong_login_data = {
        "email": test_email,
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=wrong_login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 401:
            print(f"   ✅ Wrong password correctly rejected")
        else:
            print(f"   ❌ Wrong password not rejected!")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 5. Test authenticated endpoint
    print("\n5️⃣ Testing authenticated endpoint...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Authenticated request successful!")
            print(f"   User info: {json.dumps(data['user'], indent=2)}")
        else:
            print(f"   ❌ Authenticated request failed")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🎉 All API tests completed!")
    return True

def check_supabase_dashboard():
    """Instructions to verify in Supabase"""
    print("\n📊 To verify in Supabase Dashboard:")
    print("1. Go to https://app.supabase.com")
    print("2. Select your project: cuslsfwlfpcbonvaferb")
    print("3. Go to Table Editor → users")
    print("4. You should see:")
    print("   - Test users created by the API")
    print("   - Email, name, company, and other fields")
    print("   - Timestamps for created_at and updated_at")

if __name__ == "__main__":
    print("🚀 Testing Enhanced API with Supabase Integration")
    print()
    print("Make sure the API is running on port 8002")
    print("Run: python enhanced_api.py")
    print()
    
    if test_registration_and_login():
        check_supabase_dashboard()
    else:
        print("\n❌ Some tests failed. Check the API logs for details.")