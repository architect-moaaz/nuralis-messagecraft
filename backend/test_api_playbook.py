#!/usr/bin/env python3
"""
Test playbook API endpoint
"""

import requests
import json
import asyncio
from dotenv import load_dotenv
from database import DatabaseManager

load_dotenv()

BASE_URL = "http://localhost:8002"

async def create_test_playbook():
    """Create a test playbook in the database"""
    db = DatabaseManager()
    
    # Create a session
    session_id = await db.save_user_session(
        user_id="demo_user",
        business_input="Test company for API testing"
    )
    
    # Save results
    test_results = {
        "business_profile": {
            "company_name": "API Test Company",
            "industry": "Technology",
            "target_audience": "B2B SaaS companies",
            "pain_points": ["Manual processes", "Time waste"],
            "unique_features": ["AI-powered", "Automation"]
        },
        "messaging_framework": {
            "value_proposition": "We help companies save 10 hours per week",
            "elevator_pitch": "Our AI platform automates repetitive tasks",
            "tagline_options": ["Automate Everything", "Work Smarter", "AI for Everyone"],
            "differentiators": ["First AI solution", "10x faster", "Enterprise ready"]
        },
        "positioning_strategy": {
            "unique_positioning": "The only AI platform built for enterprises",
            "target_segments": ["Fortune 500", "Mid-market"],
            "differentiation_strategy": ["Speed", "Security", "Scalability"]
        },
        "content_assets": {
            "website_headlines": ["Transform Your Business with AI", "Automate in Minutes"],
            "linkedin_posts": ["Did you know companies waste 40% of time on manual tasks?"],
            "email_templates": [{"subject": "Save 10 hours per week", "opening": "Hi {{name}}"}],
            "sales_one_liners": ["We turn hours into minutes", "Your AI transformation partner"]
        },
        "quality_review": {
            "overall_quality_score": "9.5",
            "quality_percentage": "95%",
            "strengths": ["Clear value prop", "Strong differentiation"],
            "improvements": ["Add more metrics", "Include testimonials"]
        },
        "competitor_analysis": {
            "main_competitors": ["Competitor A", "Competitor B"],
            "competitive_advantages": ["Faster implementation", "Better support"],
            "gaps": ["Mobile app", "Integrations"]
        }
    }
    
    await db.save_messaging_results(session_id, test_results)
    print(f"✅ Created test playbook: {session_id}")
    return session_id

def test_playbook_endpoint(playbook_id):
    """Test the playbook retrieval endpoint"""
    print(f"\n🧪 Testing API endpoint for playbook: {playbook_id}")
    print("=" * 60)
    
    try:
        # Test without auth (should work with demo user)
        response = requests.get(f"{BASE_URL}/api/v1/playbook/{playbook_id}")
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Playbook retrieved successfully!")
            
            # Check data structure
            print("\n📋 Playbook Structure:")
            print(f"   ID: {data.get('id')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Results type: {type(data.get('results'))}")
            
            if isinstance(data.get('results'), dict):
                print("   ✅ Results are properly parsed as dict")
                
                # Check key sections
                results = data['results']
                print("\n📊 Content Sections:")
                for section in ['business_profile', 'messaging_framework', 'positioning_strategy', 
                              'content_assets', 'quality_review', 'competitor_analysis']:
                    if section in results:
                        print(f"   ✅ {section}: {len(results[section])} items")
                    else:
                        print(f"   ❌ {section}: missing")
                
                # Check specific content
                if results.get('quality_review'):
                    quality = results['quality_review']
                    print(f"\n🎯 Quality Score: {quality.get('overall_quality_score')}/10")
                    print(f"   Percentage: {quality.get('quality_percentage')}")
                
                if results.get('messaging_framework'):
                    messaging = results['messaging_framework']
                    print(f"\n💬 Value Proposition: {messaging.get('value_proposition')}")
                    
                # Pretty print a sample
                print("\n📄 Sample JSON Response:")
                print(json.dumps(data, indent=2)[:500] + "...")
                
            else:
                print("   ❌ Results are not parsed correctly!")
                print(f"   Results: {data.get('results')}")
                
        else:
            print(f"❌ Failed to retrieve playbook: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        import traceback
        traceback.print_exc()

async def cleanup_test_playbook(playbook_id):
    """Clean up the test playbook"""
    db = DatabaseManager()
    try:
        await db.delete_playbook(playbook_id, "demo_user")
        print(f"\n🧹 Cleaned up test playbook: {playbook_id}")
    except Exception as e:
        print(f"⚠️  Could not clean up: {e}")

async def main():
    print("🚀 Testing Playbook API Endpoint")
    print()
    print("Make sure the API is running on port 8002")
    print()
    
    # Create test data
    playbook_id = await create_test_playbook()
    
    # Test the API
    test_playbook_endpoint(playbook_id)
    
    # Cleanup
    await cleanup_test_playbook(playbook_id)

if __name__ == "__main__":
    asyncio.run(main())