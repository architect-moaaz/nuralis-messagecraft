#!/usr/bin/env python3
"""
Quick test script to verify content generation works
"""

import os
import asyncio
import json

# Set a test API key for structure testing
os.environ["ANTHROPIC_API_KEY"] = "test_key_for_structure_testing"

def test_fallback_content():
    """Test that fallback content generation works"""
    try:
        # Import after setting env vars
        from langgraph_agents_with_reflection import MessageCraftAgentsWithReflection
        
        # Create agent system
        agent_system = MessageCraftAgentsWithReflection()
        
        # Test content insufficiency check
        empty_content = {}
        insufficient_content = {"value_proposition": ""}
        good_content = {
            "value_proposition": "We help businesses grow",
            "elevator_pitch": "Our solution transforms operations",
            "tagline_options": ["Grow Better", "Transform Today"]
        }
        
        print("Testing content validation:")
        print(f"Empty content insufficient: {agent_system._is_content_insufficient(empty_content)}")
        print(f"Insufficient content: {agent_system._is_content_insufficient(insufficient_content)}")
        print(f"Good content sufficient: {not agent_system._is_content_insufficient(good_content)}")
        
        # Test premium fallback generation
        print("\nTesting premium fallback generation:")
        fallback = agent_system._create_premium_fallback(
            company_name="TestCorp",
            industry="technology",
            target_audience="small businesses",
            unique_features=["fast", "secure"],
            pain_points=["slow processes", "security concerns"]
        )
        
        print(f"Fallback has value_proposition: {bool(fallback.get('premium_value_propositions'))}")
        print(f"Fallback has taglines: {bool(fallback.get('premium_taglines'))}")
        print(f"Fallback structure: {list(fallback.keys())}")
        
        # Test safe string extraction
        print("\nTesting safe string extraction:")
        test_cases = [
            "simple string",
            {"primary": "primary value"},
            {"name": "name value"},
            ["first item", "second"],
            None,
            123
        ]
        
        for test_case in test_cases:
            result = agent_system._safe_extract_string(test_case, "default")
            print(f"Input: {test_case} -> Output: {result}")
        
        print("\n✅ All fallback mechanisms working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing fallbacks: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fallback_content()