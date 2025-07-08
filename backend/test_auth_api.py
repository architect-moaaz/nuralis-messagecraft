#!/usr/bin/env python3
"""
Test script for auth endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8002"

def test_register():
    """Test the register endpoint"""
    print("🧪 Testing Registration Endpoint")
    print("=" * 40)
    
    # Registration data
    register_data = {
        "email": "test@example.com",
        "password": "securepassword123",
        "name": "Test User",
        "company": "Test Company"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
        else:
            print("❌ Registration failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_login():
    """Test the login endpoint"""
    print("\n🧪 Testing Login Endpoint")
    print("=" * 40)
    
    # Login data
    login_data = {
        "email": "test@example.com",
        "password": "securepassword123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
        else:
            print("❌ Login failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health():
    """Test the health endpoint"""
    print("\n🧪 Testing Health Endpoint")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health check passed!")
        else:
            print("❌ Health check failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Enhanced API Auth Endpoints")
    print()
    print("Make sure the API is running on port 8002")
    print()
    
    test_health()
    test_register()
    test_login()
    
    print("\n✅ All tests completed!")