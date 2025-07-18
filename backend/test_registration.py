#!/usr/bin/env python3
"""
Simple registration test script
"""
import requests
import json

# API URL
BASE_URL = "http://localhost:8002"

def test_registration():
    """Test user registration"""
    
    # Test data
    test_user = {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User",
        "company": "Test Company"
    }
    
    print(f"Testing registration for: {test_user['email']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            data = response.json()
            print(f"User ID: {data['user']['id']}")
            print(f"Token: {data['access_token'][:50]}...")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during registration: {e}")

def test_login():
    """Test user login"""
    
    # Test data
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    print(f"\nTesting login for: {login_data['email']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            data = response.json()
            print(f"User ID: {data['user']['id']}")
            print(f"Token: {data['access_token'][:50]}...")
        else:
            print(f"❌ Login failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during login: {e}")

if __name__ == "__main__":
    print("🧪 Testing MessageCraft Authentication")
    print("=" * 50)
    
    # Test registration
    test_registration()
    
    # Test login
    test_login()