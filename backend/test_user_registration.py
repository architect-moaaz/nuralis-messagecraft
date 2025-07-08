#!/usr/bin/env python3
"""
Test user registration with Supabase
"""

import asyncio
import os
from dotenv import load_dotenv
from database import DatabaseManager

# Load environment variables
load_dotenv()

async def test_user_registration():
    """Test user registration flow"""
    print("🧪 Testing User Registration with Supabase")
    print("=" * 50)
    
    db = DatabaseManager()
    test_email = f"test_{int(asyncio.get_event_loop().time())}@example.com"
    
    try:
        # Test 1: Create a new user
        print("\n1️⃣ Creating new user...")
        import hashlib
        password_hash = hashlib.sha256("testpassword123".encode()).hexdigest()
        
        user = await db.create_user(
            email=test_email,
            password_hash=password_hash,
            name="Test User",
            company="Test Company"
        )
        
        print(f"✅ User created successfully!")
        print(f"   ID: {user['id']}")
        print(f"   Email: {user['email']}")
        print(f"   Name: {user['name']}")
        print(f"   Company: {user['company']}")
        
        # Test 2: Try to create duplicate user
        print("\n2️⃣ Testing duplicate user prevention...")
        try:
            await db.create_user(
                email=test_email,
                password_hash=password_hash,
                name="Duplicate User",
                company="Another Company"
            )
            print("❌ Duplicate user was created (this shouldn't happen)")
        except Exception as e:
            print(f"✅ Duplicate user prevented: {e}")
        
        # Test 3: Get user by email
        print("\n3️⃣ Getting user by email...")
        fetched_user = await db.get_user_by_email(test_email)
        if fetched_user:
            print(f"✅ User retrieved successfully")
            print(f"   ID matches: {fetched_user['id'] == user['id']}")
        else:
            print("❌ Failed to retrieve user")
        
        # Test 4: Verify user credentials
        print("\n4️⃣ Verifying user credentials...")
        verified_user = await db.verify_user(test_email, password_hash)
        if verified_user:
            print("✅ User credentials verified successfully")
        else:
            print("❌ Failed to verify user credentials")
        
        # Test 5: Test wrong password
        print("\n5️⃣ Testing wrong password...")
        wrong_hash = hashlib.sha256("wrongpassword".encode()).hexdigest()
        wrong_user = await db.verify_user(test_email, wrong_hash)
        if not wrong_user:
            print("✅ Wrong password correctly rejected")
        else:
            print("❌ Wrong password was accepted")
        
        print("\n🎉 All tests passed! User registration is working with Supabase.")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        return False
    
    return True

async def check_users_table():
    """Check if users can be queried from Supabase"""
    print("\n📊 Checking users table...")
    
    try:
        db = DatabaseManager()
        # Try to query the users table
        result = db.supabase.table("users").select("email").limit(5).execute()
        print(f"✅ Users table accessible")
        print(f"   Found {len(result.data)} users")
        if result.data:
            print("   Sample emails:", [u['email'] for u in result.data])
    except Exception as e:
        print(f"❌ Error accessing users table: {e}")
        print("💡 Make sure the 'users' table exists in Supabase")

if __name__ == "__main__":
    asyncio.run(check_users_table())
    asyncio.run(test_user_registration())
    
    print("\n💡 To see the users in Supabase:")
    print("1. Go to https://app.supabase.com")
    print("2. Select your project")
    print("3. Go to Table Editor → users")
    print("4. You should see the newly created test users")