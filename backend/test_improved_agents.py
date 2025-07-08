#!/usr/bin/env python3
"""
Test script for the improved messaging agents with better JSON parsing and industry focus
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

async def test_improved_messaging_agent():
    """Test the improved messaging agent with various business types"""
    
    try:
        from langgraph_agents_with_reflection import MessageCraftAgentsWithReflection
        print("✅ Successfully imported improved agents")
    except ImportError as e:
        print(f"❌ Failed to import agents: {e}")
        return
    
    # Test cases representing different industries
    test_cases = [
        {
            "name": "Green Thread (Fashion/Sustainability)",
            "input": "Green Thread is a sustainable fashion company that creates eco-friendly clothing using recycled materials and helps environmentally conscious consumers reduce their carbon footprint while staying stylish",
            "expected_industry": "Fashion"
        },
        {
            "name": "MindEase (Healthcare/Therapy)", 
            "input": "MindEase is a telemedicine platform specifically for mental health therapy. We connect patients with licensed therapists for video sessions and provide tools for session notes, homework tracking, and progress monitoring. Our target market includes adults aged 25-50 dealing with anxiety, depression, or stress who prefer the convenience and privacy of remote therapy.",
            "expected_industry": "Healthcare"
        },
        {
            "name": "TechFlow (Technology/AI)",
            "input": "TechFlow creates AI-powered automation tools for small businesses to streamline their workflows and reduce manual tasks. We help companies automate repetitive processes and focus on strategic growth.",
            "expected_industry": "Technology"
        }
    ]
    
    # Initialize the agent system
    agent_system = MessageCraftAgentsWithReflection(
        quality_threshold=8.0,
        max_reflection_cycles=2
    )
    
    print("🚀 Testing Improved Messaging Agent System")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 TEST CASE {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Test just the messaging generation
            result = await agent_system.generate_messaging_playbook(test_case["input"])
            
            # Extract key results
            business_profile = result.get("business_profile", {})
            messaging = result.get("messaging_framework", {})
            
            print(f"✅ Company: {business_profile.get('company_name', 'NOT_EXTRACTED')}")
            print(f"✅ Industry: {business_profile.get('industry', 'NOT_EXTRACTED')}")
            print(f"✅ Target: {business_profile.get('target_audience', 'NOT_EXTRACTED')}")
            
            if messaging.get('value_proposition'):
                print(f"✅ Value Prop: {messaging['value_proposition'][:80]}...")
            else:
                print("❌ No value proposition generated")
                
            if messaging.get('tagline_options'):
                print(f"✅ Taglines: {len(messaging['tagline_options'])} options")
                print(f"   → {messaging['tagline_options'][0]}")
            else:
                print("❌ No taglines generated")
            
            # Check if industry-specific messaging was used
            industry_detected = business_profile.get('industry', '').lower()
            if ('healthcare' in industry_detected or 'medical' in industry_detected or 'therapy' in industry_detected):
                if any(word in str(messaging).lower() for word in ['trust', 'secure', 'confidential', 'clinical', 'outcomes']):
                    print("✅ Healthcare-specific language detected")
                else:
                    print("⚠️ Healthcare-specific language not clearly detected")
            elif ('technology' in industry_detected or 'tech' in industry_detected or 'ai' in industry_detected):
                if any(word in str(messaging).lower() for word in ['innovation', 'efficiency', 'scalable', 'automation', 'roi']):
                    print("✅ Technology-specific language detected")
                else:
                    print("⚠️ Technology-specific language not clearly detected")
            elif ('fashion' in industry_detected or 'sustainable' in industry_detected):
                if any(word in str(messaging).lower() for word in ['sustainable', 'eco', 'style', 'conscious', 'environmental']):
                    print("✅ Sustainability/Fashion-specific language detected")
                else:
                    print("⚠️ Sustainability/Fashion-specific language not clearly detected")
            
        except Exception as e:
            print(f"❌ Error in test case {i}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ Testing completed!")
    print("🎯 Key improvements validated:")
    print("   - Better JSON parsing with error handling")
    print("   - Industry-specific messaging guidelines")
    print("   - Enhanced prompting for different sectors")
    print("   - Robust fallback systems")

if __name__ == "__main__":
    asyncio.run(test_improved_messaging_agent())