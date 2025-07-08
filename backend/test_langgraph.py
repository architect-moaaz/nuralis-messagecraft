import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

# Test if LangGraph can be imported and initialized
try:
    from langgraph_agents import MessageCraftAgents
    print("✅ LangGraph agents imported successfully")
    
    async def test_agents():
        try:
            agents = MessageCraftAgents()
            print("✅ LangGraph agents initialized successfully")
            
            # Test with a simple business input
            business_input = "We help small businesses manage their inventory more efficiently."
            result = await agents.generate_messaging_playbook(business_input)
            
            if result.get('status') == 'completed':
                print("✅ LangGraph workflow completed successfully")
                print(f"Generated playbook for: {result.get('business_profile', {}).get('company_name', 'Unknown')}")
            else:
                print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error testing agents: {e}")
    
    # Run the test
    asyncio.run(test_agents())
    
except Exception as e:
    print(f"❌ Error importing LangGraph agents: {e}")
    print("Will fall back to demo mode")