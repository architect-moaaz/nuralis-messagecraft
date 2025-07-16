#!/usr/bin/env python3
"""
Production Setup Test Script
Run this to verify your production configuration is working correctly.
"""

import asyncio
import httpx
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

class ProductionTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.test_results = []
    
    async def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("is_production") is True:
                    self.log_success("✓ Health check passed - Production mode enabled")
                else:
                    self.log_warning("⚠ Health check passed but not in production mode")
                return True
            else:
                self.log_error(f"✗ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_error(f"✗ Health check failed: {str(e)}")
            return False
    
    async def test_google_oauth(self):
        """Test Google OAuth configuration"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/auth/google")
            if response.status_code == 200:
                data = response.json()
                if "auth_url" in data and "accounts.google.com" in data["auth_url"]:
                    self.log_success("✓ Google OAuth configuration working")
                    return True
                else:
                    self.log_error("✗ Google OAuth URL invalid")
                    return False
            else:
                self.log_error(f"✗ Google OAuth test failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_error(f"✗ Google OAuth test failed: {str(e)}")
            return False
    
    async def test_pricing_endpoint(self):
        """Test pricing information endpoint"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/pricing")
            if response.status_code == 200:
                data = response.json()
                if "credit_packages" in data and "subscriptions" in data:
                    self.log_success("✓ Pricing endpoint working")
                    return True
                else:
                    self.log_error("✗ Pricing data incomplete")
                    return False
            else:
                self.log_error(f"✗ Pricing endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_error(f"✗ Pricing endpoint test failed: {str(e)}")
            return False
    
    async def test_environment_variables(self):
        """Test that required environment variables are set"""
        required_vars = [
            "ENVIRONMENT",
            "SECRET_KEY",
            "ANTHROPIC_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_SERVICE_ROLE_KEY",
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_SECRET",
            "STRIPE_SECRET_KEY",
            "STRIPE_PRICE_CREDITS_10"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if not missing_vars:
            self.log_success("✓ All required environment variables are set")
            return True
        else:
            self.log_error(f"✗ Missing environment variables: {', '.join(missing_vars)}")
            return False
    
    async def test_user_registration(self):
        """Test user registration functionality"""
        try:
            test_user = {
                "email": f"test+{int(asyncio.get_event_loop().time())}@example.com",
                "password": "testpassword123",
                "name": "Test User",
                "company": "Test Company"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/register",
                json=test_user
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.log_success("✓ User registration working")
                    return True, data["access_token"]
                else:
                    self.log_error("✗ Registration response incomplete")
                    return False, None
            else:
                self.log_error(f"✗ User registration failed: {response.status_code}")
                return False, None
        except Exception as e:
            self.log_error(f"✗ User registration test failed: {str(e)}")
            return False, None
    
    async def test_generation_eligibility(self, token):
        """Test generation eligibility check"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.post(
                f"{self.base_url}/api/v1/check-generation-eligibility",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("can_generate") is True:
                    self.log_success("✓ Generation eligibility check working - Free kit available")
                    return True
                else:
                    self.log_warning("⚠ Cannot generate - check credit system")
                    return False
            else:
                self.log_error(f"✗ Generation eligibility test failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_error(f"✗ Generation eligibility test failed: {str(e)}")
            return False
    
    def log_success(self, message):
        print(f"\033[92m{message}\033[0m")
        self.test_results.append(("PASS", message))
    
    def log_warning(self, message):
        print(f"\033[93m{message}\033[0m")
        self.test_results.append(("WARN", message))
    
    def log_error(self, message):
        print(f"\033[91m{message}\033[0m")
        self.test_results.append(("FAIL", message))
    
    async def run_all_tests(self):
        """Run all production tests"""
        print("🚀 Starting MessageCraft Production Tests...\n")
        
        # Test environment variables first
        await self.test_environment_variables()
        
        # Test basic connectivity
        health_ok = await self.test_health_check()
        if not health_ok:
            print("\n❌ Basic connectivity failed. Check if the API is running.")
            return False
        
        # Test endpoints
        await self.test_google_oauth()
        await self.test_pricing_endpoint()
        
        # Test user flow
        reg_ok, token = await self.test_user_registration()
        if reg_ok and token:
            await self.test_generation_eligibility(token)
        
        # Close client
        await self.client.aclose()
        
        # Print summary
        self.print_summary()
        
        return all(result[0] in ["PASS", "WARN"] for result in self.test_results)
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for result in self.test_results if result[0] == "PASS")
        warned = sum(1 for result in self.test_results if result[0] == "WARN")
        failed = sum(1 for result in self.test_results if result[0] == "FAIL")
        
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Warnings: {warned}")
        print(f"❌ Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 All critical tests passed! Production setup looks good.")
        elif failed <= 2:
            print("\n⚠️  Minor issues detected. Review failed tests.")
        else:
            print("\n❌ Major issues detected. Production setup needs attention.")

async def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test MessageCraft production setup")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL for the API (default: http://localhost:8000)")
    
    args = parser.parse_args()
    
    tester = ProductionTester(args.url)
    success = await tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())