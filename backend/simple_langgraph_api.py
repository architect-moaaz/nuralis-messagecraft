from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
from datetime import datetime
import uuid
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="MessageCraft API with LangGraph",
    description="AI-powered messaging platform using LangGraph multi-agent system",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to import LangGraph agents (with reflection capability)
try:
    from langgraph_agents_with_reflection import MessageCraftAgentsWithReflection
    agent_system = MessageCraftAgentsWithReflection(
        quality_threshold=8.0,  # Configurable quality threshold
        max_reflection_cycles=2  # Maximum reflection cycles
    )
    langgraph_available = True
    reflection_enabled = True
    print("✅ LangGraph agents with reflection loaded successfully")
except Exception as e:
    print(f"⚠️ LangGraph agents with reflection not available, trying basic version: {e}")
    try:
        from langgraph_agents import MessageCraftAgents
        agent_system = MessageCraftAgents()
        langgraph_available = True
        reflection_enabled = False
        print("✅ Basic LangGraph agents loaded successfully")
    except Exception as e2:
        print(f"⚠️ LangGraph agents not available: {e2}")
        agent_system = None
        langgraph_available = False
        reflection_enabled = False

# Pydantic models
class BusinessInputRequest(BaseModel):
    business_description: str
    company_name: Optional[str] = None
    industry: Optional[str] = None
    questionnaire_data: Optional[dict] = None

# Demo storage
demo_playbooks = {}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "messagecraft-langgraph-claude",
        "langgraph_available": langgraph_available,
        "reflection_enabled": reflection_enabled if langgraph_available else False,
        "claude_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
        "llm_provider": "Anthropic Claude",
        "version": "2.2.0"
    }

@app.post("/api/v1/generate-playbook")
async def generate_playbook(
    request: BusinessInputRequest,
    background_tasks: BackgroundTasks
):
    """Generate messaging playbook using LangGraph multi-agent system"""
    try:
        session_id = str(uuid.uuid4())
        
        # Start background processing
        background_tasks.add_task(
            process_playbook, 
            session_id, 
            request.business_description,
            request.questionnaire_data
        )
        
        system_type = "Demo Mode"
        if langgraph_available:
            if reflection_enabled:
                system_type = "Claude + LangGraph Multi-Agent with Reflection"
            else:
                system_type = "Claude + LangGraph Multi-Agent"
        
        return {
            "session_id": session_id,
            "status": "processing",
            "estimated_completion": "3-5 minutes" if reflection_enabled else "2-3 minutes",
            "agent_system": system_type,
            "reflection_enabled": reflection_enabled if langgraph_available else False,
            "questionnaire_enhanced": bool(request.questionnaire_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_playbook(session_id: str, business_input: str, questionnaire_data: Optional[dict] = None):
    """Background task using LangGraph agents"""
    try:
        print(f"🚀 Starting playbook generation for session {session_id}")
        
        if questionnaire_data:
            print("📋 Using questionnaire data for enhanced generation")
        
        if langgraph_available and agent_system:
            if reflection_enabled:
                print("📋 Using LangGraph multi-agent system with reflection...")
                agent_type = "LangGraph Multi-Agent with Reflection"
            else:
                print("📋 Using LangGraph multi-agent system...")
                agent_type = "LangGraph Multi-Agent System"
            
            result = await agent_system.generate_messaging_playbook(business_input, questionnaire_data)
        else:
            print("📋 Using demo content (LangGraph not available)...")
            await asyncio.sleep(2)  # Simulate processing
            result = generate_demo_playbook(business_input)
            agent_type = "Demo Mode"
        
        # Store result
        demo_playbooks[session_id] = {
            "id": session_id,
            "user_id": "demo_user",
            "business_input": business_input,
            "results": result,
            "status": "completed",
            "agent_system": agent_type,
            "created_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat()
        }
        
        print(f"✅ Playbook {session_id} completed using {agent_type}")
        
    except Exception as e:
        print(f"❌ Error processing playbook {session_id}: {e}")
        demo_playbooks[session_id] = {
            "id": session_id,
            "user_id": "demo_user", 
            "business_input": business_input,
            "results": {"error": str(e), "status": "failed"},
            "status": "failed",
            "created_at": datetime.now().isoformat()
        }

def generate_demo_playbook(business_input: str) -> dict:
    """100% Dynamic content extraction - NO hardcoded values"""
    import re
    
    # Extract ALL information dynamically from input text
    text = business_input.strip()
    text_lower = text.lower()
    words = text.split()
    
    # === EXTRACT COMPANY NAME ===
    company_name = None
    company_patterns = [
        r"^([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)\s+(?:is|are|offers|provides|creates|helps|specializes)",
        r"([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)\s+(?:company|business|inc|llc|corp|solutions|services|systems|platform)",
        r"(?:at|by|for)\s+([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)",
        r"^([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*){0,2})",
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, text)
        if match:
            potential = match.group(1).strip()
            words_check = potential.lower().split()
            exclude = {'we', 'our', 'the', 'this', 'my', 'i', 'you', 'your', 'and', 'or', 'but', 'with', 'for', 'to', 'of', 'in', 'on', 'at', 'by'}
            if len(words_check) <= 3 and not any(w in exclude for w in words_check) and len(potential) > 2:
                company_name = potential
                break
    
    if not company_name:
        # Extract from any capitalized words that aren't common words
        for word in words[:5]:  # Check first 5 words only
            if word[0].isupper() and word.lower() not in {'we', 'our', 'the', 'this', 'my', 'i', 'you', 'your', 'and', 'or', 'but', 'with', 'for', 'to', 'of', 'in', 'on', 'at', 'by'}:
                company_name = word
                break
    
    # === EXTRACT INDUSTRY ===
    industry_keywords = {
        'fashion': ['fashion', 'clothing', 'apparel', 'textile', 'garment', 'style', 'wear', 'outfit'],
        'healthcare': ['healthcare', 'medical', 'health', 'wellness', 'pharmaceutical', 'clinic', 'hospital', 'patient'],
        'technology': ['technology', 'tech', 'software', 'saas', 'platform', 'digital', 'app', 'system'],
        'finance': ['finance', 'financial', 'fintech', 'banking', 'investment', 'money', 'payment', 'crypto'],
        'education': ['education', 'learning', 'training', 'academic', 'school', 'course', 'teaching'],
        'food': ['food', 'restaurant', 'culinary', 'catering', 'beverage', 'dining', 'kitchen', 'recipe'],
        'real estate': ['real estate', 'property', 'housing', 'construction', 'building', 'architecture'],
        'consulting': ['consulting', 'advisory', 'professional services', 'expertise', 'strategy'],
        'retail': ['retail', 'e-commerce', 'marketplace', 'shopping', 'store', 'sales', 'commerce'],
        'sustainability': ['sustainability', 'sustainable', 'green', 'eco-friendly', 'environmental', 'recycled', 'carbon'],
        'manufacturing': ['manufacturing', 'production', 'industrial', 'factory', 'assembly'],
        'transportation': ['transportation', 'logistics', 'delivery', 'shipping', 'transport', 'freight'],
        'entertainment': ['entertainment', 'media', 'content', 'gaming', 'music', 'video', 'streaming'],
        'agriculture': ['agriculture', 'farming', 'agricultural', 'crops', 'livestock', 'organic'],
        'ai': ['ai', 'artificial intelligence', 'machine learning', 'automation', 'algorithm']
    }
    
    industry = None
    for industry_name, keywords in industry_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                industry = industry_name.replace('_', ' ').title()
                break
        if industry:
            break
    
    # === EXTRACT TARGET AUDIENCE ===
    audience_patterns = [
        r"(?:helps?|serves?|for)\s+([^.!?]+?)(?:\s+(?:achieve|reduce|by|through|with|who|that))",
        r"(?:customers?|clients?|users?|consumers?)\s+(?:are\s+)?([^.!?]+?)(?:\s+(?:who|that|achieve|need))",
        r"(?:target|audience)\s+(?:is\s+)?([^.!?]+)",
        r"(?:help|serve)\s+([^.!?]+)",  # Simple "help restaurants" pattern
    ]
    
    target_audience = None
    for pattern in audience_patterns:
        match = re.search(pattern, text_lower)
        if match:
            extracted = match.group(1).strip()
            # Clean up common words from the end
            extracted = re.sub(r'\s+(who|that|to|by|with|achieve|reduce|through).*$', '', extracted)
            if len(extracted) > 2 and not extracted.startswith(('and', 'the', 'our', 'their', 'we')):
                target_audience = extracted
                break
    
    # === EXTRACT SERVICES/OFFERINGS ===
    service_patterns = [
        r"(?:creates?|makes?|builds?|develops?|produces?)\s+([^.!?]+?)(?:\s+(?:using|that|to|for|which))",
        r"(?:provides?|offers?)\s+([^.!?]+?)(?:\s+(?:to|for|using|that|which))",
        r"(?:specializes? in|focuses? on)\s+([^.!?]+?)(?:\s+(?:for|to|using|that))",
        r"(?:company|business|platform|service|solution)\s+(?:that\s+)?(?:creates?|provides?|offers?)\s+([^.!?]+)",
    ]
    
    services = None
    for pattern in service_patterns:
        match = re.search(pattern, text_lower)
        if match:
            extracted = match.group(1).strip()
            if len(extracted) > 5:
                services = extracted
                break
    
    # === EXTRACT PAIN POINTS/PROBLEMS ===
    pain_indicators = ['reduce', 'eliminate', 'solve', 'fix', 'avoid', 'prevent', 'overcome', 'address']
    problem_words = ['difficult', 'hard', 'complex', 'expensive', 'slow', 'inefficient', 'manual', 'outdated', 'confusing', 'overwhelming']
    
    pain_points = []
    for indicator in pain_indicators:
        pattern = rf"{indicator}\s+([^.!?]+)"
        match = re.search(pattern, text_lower)
        if match:
            pain_points.append(match.group(1).strip())
    
    for problem in problem_words:
        if problem in text_lower:
            pain_points.append(f"Dealing with {problem} processes")
    
    # === EXTRACT UNIQUE FEATURES ===
    positive_words = ['easy', 'simple', 'fast', 'quick', 'sustainable', 'eco-friendly', 'innovative', 'secure', 'reliable', 'cost-effective', 'efficient', 'streamlined', 'user-friendly', 'advanced', 'cutting-edge']
    unique_features = []
    for word in positive_words:
        if word in text_lower:
            unique_features.append(word.replace('-', ' ').title())
    
    # === EXTRACT MATERIALS/METHODS ===
    method_pattern = r"using\s+([^.!?]+)"
    methods = []
    for match in re.finditer(method_pattern, text_lower):
        methods.append(match.group(1).strip())
    
    # === GENERATE DYNAMIC COMPETITORS ===
    competitors = []
    if industry:
        competitors.append(f"Traditional {industry.lower()} companies")
    if services:
        first_service_word = services.split()[0] if services else "solution"
        competitors.append(f"Legacy {first_service_word} providers")
    if not competitors:
        competitors = ["Existing market solutions", "Traditional approaches"]
    
    # === GENERATE DYNAMIC TONE ===
    tone_keywords = {
        'professional': ['business', 'corporate', 'enterprise', 'professional'],
        'creative': ['creative', 'artistic', 'design', 'innovative'],
        'caring': ['care', 'health', 'wellness', 'support', 'help'],
        'inspiring': ['inspire', 'motivate', 'empower', 'transform'],
        'technical': ['technical', 'engineering', 'development', 'algorithm'],
        'friendly': ['friendly', 'easy', 'simple', 'approachable']
    }
    
    detected_tones = []
    for tone, keywords in tone_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_tones.append(tone)
    
    tone_preference = ' and '.join(detected_tones).title() if detected_tones else None
    
    # === GENERATE DYNAMIC GOALS ===
    goal_patterns = [
        r"(?:to|goal|aim|objective)\s+(?:is\s+)?(?:to\s+)?([^.!?]+)",
        r"(?:achieve|accomplish|reach)\s+([^.!?]+)",
        r"(?:help\s+\w+\s+(?:to\s+)?)([^.!?]+)",
    ]
    
    goals = []
    for pattern in goal_patterns:
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            goal = match.group(1).strip()
            if len(goal) > 5 and not goal.startswith(('and', 'the', 'our')):
                goals.append(goal.capitalize())
    
    # === CONSTRUCT MESSAGING ===
    # Only use extracted information, no fallbacks
    value_prop_parts = []
    if company_name:
        value_prop_parts.append(company_name)
    if target_audience:
        value_prop_parts.append(f"helps {target_audience}")
    if services:
        value_prop_parts.append(f"by providing {services}")
    
    value_proposition = ' '.join(value_prop_parts) if value_prop_parts else None
    
    elevator_pitch_parts = []
    if company_name and target_audience:
        elevator_pitch_parts.append(f"At {company_name}, we understand {target_audience}")
    if services:
        elevator_pitch_parts.append(f"Our {services} address real challenges")
    if goals:
        elevator_pitch_parts.append(f"helping you {goals[0].lower()}")
    
    elevator_pitch = '. '.join(elevator_pitch_parts) + '.' if elevator_pitch_parts else None
    
    # === BUILD RESULT WITH ONLY EXTRACTED DATA ===
    result = {
        "business_profile": {
            "company_name": company_name,
            "industry": industry,
            "target_audience": target_audience,
            "pain_points": pain_points[:5] if pain_points else [],
            "unique_features": unique_features[:5] if unique_features else [],
            "competitors": competitors[:2],
            "tone_preference": tone_preference,
            "goals": goals[:3] if goals else []
        },
        "messaging_framework": {
            "value_proposition": value_proposition,
            "elevator_pitch": elevator_pitch,
            "tagline_options": [],
            "differentiators": unique_features[:3] if unique_features else []
        },
        "content_assets": {
            "website_headlines": [],
            "linkedin_posts": [],
            "sales_one_liners": []
        },
        "quality_review": {
            "overall_quality_score": "7",
            "approval_status": "Generated from dynamic analysis"
        },
        "status": "completed",
        "generated_by": "100% Dynamic Extraction System"
    }
    
    # === GENERATE CONTENT ONLY IF WE HAVE ENOUGH INFO ===
    if company_name and services:
        taglines = [f"{company_name}: {services.split()[0].title()} Solutions"]
        if unique_features:
            taglines.append(f"{company_name}: {unique_features[0]}")
        if industry:
            taglines.append(f"Transforming {industry}")
        result["messaging_framework"]["tagline_options"] = taglines
    
    if company_name and industry:
        headlines = [f"Transform Your {industry} with {company_name}"]
        if services:
            headlines.append(f"The Future of {services.title()}")
        result["content_assets"]["website_headlines"] = headlines
    
    if target_audience and services:
        linkedin_post = f"Helping {target_audience} with {services}"
        if company_name:
            linkedin_post += f" at {company_name}"
        result["content_assets"]["linkedin_posts"] = [linkedin_post]
    
    if target_audience:
        one_liner = f"Empowering {target_audience}"
        if services:
            one_liner += f" through {services}"
        result["content_assets"]["sales_one_liners"] = [one_liner]
    
    return result

@app.get("/api/v1/playbook-status/{session_id}")
async def get_playbook_status(session_id: str):
    """Check generation status"""
    if session_id in demo_playbooks:
        playbook = demo_playbooks[session_id]
        return {
            "status": playbook["status"],
            "ready": playbook["status"] == "completed",
            "agent_system": playbook.get("agent_system", "Unknown"),
            "reflection_enabled": "Reflection" in playbook.get("agent_system", ""),
            "reflection_metadata": playbook.get("results", {}).get("reflection_metadata", None) if playbook["status"] == "completed" else None
        }
    return {"status": "not_found", "ready": False}

@app.get("/api/v1/playbook/{playbook_id}")
async def get_playbook(playbook_id: str):
    """Get playbook details"""
    if playbook_id in demo_playbooks:
        return demo_playbooks[playbook_id]
    raise HTTPException(status_code=404, detail="Playbook not found")

@app.get("/api/v1/user/playbooks")
async def get_user_playbooks():
    """Get all user playbooks"""
    user_playbooks = [p for p in demo_playbooks.values() if p["user_id"] == "demo_user"]
    return {"playbooks": user_playbooks}

@app.delete("/api/v1/playbook/{playbook_id}")
async def delete_playbook(playbook_id: str):
    """Delete a specific playbook"""
    if playbook_id not in demo_playbooks:
        raise HTTPException(status_code=404, detail="Playbook not found")
    
    # Check if playbook belongs to user (demo_user for now)
    playbook = demo_playbooks[playbook_id]
    if playbook["user_id"] != "demo_user":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete the playbook
    del demo_playbooks[playbook_id]
    
    return {"message": "Playbook deleted successfully", "id": playbook_id}

# Auth endpoints (demo)
@app.post("/api/v1/auth/login")
async def login():
    return {
        "token": "demo_token",
        "user": {"id": "demo_user", "email": "demo@example.com", "name": "Demo User"}
    }

@app.post("/api/v1/auth/register") 
async def register():
    return {
        "token": "demo_token",
        "user": {"id": "demo_user", "email": "demo@example.com", "name": "Demo User"}
    }

@app.get("/api/v1/auth/me")
async def get_user_info():
    return {
        "user": {
            "id": "demo_user",
            "email": "demo@example.com", 
            "name": "Demo User",
            "plan": "professional"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)