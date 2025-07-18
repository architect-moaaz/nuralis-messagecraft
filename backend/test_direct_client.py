#!/usr/bin/env python3
"""
Quick test of the direct Anthropic client approach
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_direct_client():
    try:
        print("Testing direct Anthropic client...")
        
        import anthropic
        client = anthropic.AsyncAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        print("✅ Direct client initialized")
        
        # Test a simple call
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            temperature=0.6,
            system="You are a helpful assistant.",
            messages=[{"role": "user", "content": "Say hello!"}]
        )
        
        print("✅ Direct API call successful")
        print(f"Response: {response.content[0].text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_agents_import():
    try:
        print("Testing agents import...")
        from langgraph_agents_with_reflection import MessageCraftAgentsWithReflection
        print("✅ Import successful")
        
        agents = MessageCraftAgentsWithReflection()
        print("✅ Agents initialization successful")
        
        # Test a simple LLM call through the agents
        from langchain.schema import HumanMessage, SystemMessage
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Say hello!")
        ]
        
        response = await agents._call_llm_direct(messages)
        print("✅ Direct LLM call through agents successful")
        print(f"Response: {response.content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🔧 Testing Direct Client Implementation")
    print("=" * 50)
    
    direct_ok = await test_direct_client()
    print()
    agents_ok = await test_agents_import()
    
    if direct_ok and agents_ok:
        print("\n✅ All tests passed - ready for kit generation!")
    else:
        print("\n❌ Some tests failed - need debugging")

if __name__ == "__main__":
    asyncio.run(main())