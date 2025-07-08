#!/usr/bin/env python3
"""
Test the _safe_extract_string method fix
"""

import os
import sys

# Set a test API key for structure testing
os.environ["ANTHROPIC_API_KEY"] = "test_key_for_structure_testing"

def test_safe_extract_method():
    """Test that _safe_extract_string method exists and works"""
    try:
        # Import the class
        from langgraph_agents_with_reflection import MessageCraftAgentsWithReflection
        
        # Create an instance
        agent_system = MessageCraftAgentsWithReflection()
        
        # Test the method exists
        if hasattr(agent_system, '_safe_extract_string'):
            print("✅ _safe_extract_string method exists")
            
            # Test different input types
            test_cases = [
                ("simple string", "simple string"),
                ({"primary": "primary value"}, "primary value"), 
                ({"name": "name value"}, "name value"),
                (["first item", "second"], "first item"),
                (None, "default"),
                (123, "default")
            ]
            
            print("\n🧪 Testing _safe_extract_string method:")
            for input_val, expected in test_cases:
                result = agent_system._safe_extract_string(input_val, "default")
                status = "✅" if result == expected else "❌"
                print(f"{status} Input: {input_val} -> Output: {result}")
            
            print("\n✅ _safe_extract_string method is working correctly!")
            return True
        else:
            print("❌ _safe_extract_string method not found")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing method: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Testing _safe_extract_string Method Fix")
    print("=" * 50)
    
    success = test_safe_extract_method()
    
    if success:
        print("\n🎉 Fix successful! The missing method has been restored.")
        print("The LangGraph agent should now work correctly.")
    else:
        print("\n💥 Fix failed. Please check the implementation.")
        sys.exit(1)