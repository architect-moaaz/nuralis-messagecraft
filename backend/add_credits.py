#!/usr/bin/env python3
"""
Admin script to add credits to user accounts
"""
import asyncio
import sys
from dotenv import load_dotenv
from database_enhanced import EnhancedDatabaseManager

# Load environment variables
load_dotenv()

async def add_credits_to_user(email: str, credits: int, description: str = "Manual credit addition"):
    """Add credits to a user account by email"""
    db_manager = EnhancedDatabaseManager()
    
    try:
        # Find user by email
        print(f"🔍 Looking up user: {email}")
        user = await db_manager.get_user_by_email(email)
        
        if not user:
            print(f"❌ User not found: {email}")
            return False
        
        print(f"✅ User found: {user['name']} (ID: {user['id']})")
        
        # Get current balance
        current_balance = await db_manager.get_user_credit_balance(user['id'])
        print(f"📊 Current balance: {current_balance['credits']} credits")
        
        # Add credits
        print(f"💳 Adding {credits} credits...")
        new_balance = await db_manager.add_user_credits(
            user_id=user['id'],
            credits=credits,
            description=description
        )
        
        if new_balance > 0:
            print(f"✅ Successfully added {credits} credits!")
            print(f"💰 New balance: {new_balance} credits")
            
            # Show transaction history
            transactions = await db_manager.get_credit_transactions(user['id'], limit=3)
            if transactions:
                print("\n📜 Recent transactions:")
                for txn in transactions[:3]:
                    print(f"  • {txn['transaction_type']}: {txn['credits_amount']} credits - {txn['description']}")
            
            return True
        else:
            print("❌ Failed to add credits")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def list_users():
    """List all users and their credit balances"""
    db_manager = EnhancedDatabaseManager()
    
    try:
        print("👥 All Users and Credit Balances:")
        print("=" * 60)
        
        # Get all users (you might need to implement this method)
        # For now, let's just show how it would work
        print("📋 To list all users, you would need to implement get_all_users() in database_enhanced.py")
        print("   Or use the Supabase dashboard to view users")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

async def main():
    """Main function"""
    print("💳 MessageCraft Credit Management")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 add_credits.py <email> <credits> [description]")
        print("  python3 add_credits.py list")
        print("")
        print("Examples:")
        print("  python3 add_credits.py user@example.com 50")
        print("  python3 add_credits.py user@example.com 100 'Bonus credits'")
        print("  python3 add_credits.py list")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        await list_users()
    else:
        email = command
        
        if len(sys.argv) < 3:
            print("❌ Please specify the number of credits to add")
            return
        
        try:
            credits = int(sys.argv[2])
        except ValueError:
            print("❌ Credits must be a number")
            return
        
        description = sys.argv[3] if len(sys.argv) > 3 else "Manual credit addition"
        
        success = await add_credits_to_user(email, credits, description)
        if success:
            print("\n🎉 Credits added successfully!")
        else:
            print("\n💥 Failed to add credits")

if __name__ == "__main__":
    asyncio.run(main())