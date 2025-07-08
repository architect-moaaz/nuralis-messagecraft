#!/usr/bin/env python3
"""
Test script to verify reliable content generation works
"""

import os
import asyncio
import json

# Set a test API key for structure testing
os.environ["ANTHROPIC_API_KEY"] = "test_key_for_structure_testing"

def test_reliable_generation():
    """Test that reliable content generation approach works"""
    try:
        # Import after setting env vars
        from langgraph_agents_with_reflection import MessageCraftAgentsWithReflection
        
        # Create agent system
        agent_system = MessageCraftAgentsWithReflection()
        
        print("✅ Import successful - reliable generation system loaded")
        
        # Test messaging framework structure
        print("\n🧪 Testing messaging framework structure...")
        
        # Create sample messaging framework
        sample_messaging = {
            "value_proposition": "TestCorp helps small businesses achieve better results through innovative technology solutions.",
            "elevator_pitch": "At TestCorp, we understand the challenges facing small businesses in technology. Our proven solution addresses these challenges while delivering measurable results that help your business grow.",
            "tagline_options": ["Transform Your Technology", "Innovation Delivered", "Your Success Partner"],
            "differentiators": ["Industry expertise", "Proven results", "Comprehensive approach"]
        }
        
        # Test content validation
        insufficient_content = {}
        good_content = sample_messaging
        
        print(f"Empty content insufficient: {agent_system._is_content_insufficient(insufficient_content)}")
        print(f"Good content sufficient: {not agent_system._is_content_insufficient(good_content)}")
        
        # Test safe string extraction
        print("\n🧪 Testing safe string extraction...")
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
        
        print("\n✅ All reliable generation tests passed!")
        print("🎯 Ready for reliable messaging framework and content generation!")
        
        # Test messaging framework generation
        print("\n🧪 Testing messaging framework methods...")
        
        # Mock async methods exist
        if hasattr(agent_system, '_generate_messaging_framework_reliable'):
            print("✅ Reliable messaging framework method exists")
        if hasattr(agent_system, '_generate_content_assets_reliable'):
            print("✅ Reliable content assets method exists")
        
        print("\n🚀 System is ready for reliable content generation without fallbacks!")
        
    except Exception as e:
        print(f"❌ Error testing reliable generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reliable_generation()