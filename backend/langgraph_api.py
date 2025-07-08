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

# Import our LangGraph agents
from langgraph_agents import MessageCraftAgents

# Load environment variables
load_dotenv()

app = FastAPI(
    title="MessageCraft API with LangGraph",
    description="AI-powered messaging and differentiation platform using LangGraph agents",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LangGraph agent system
try:
    agent_system = MessageCraftAgents()
    langgraph_available = True
except Exception as e:
    print(f"Warning: LangGraph agents not available: {e}")
    agent_system = None
    langgraph_available = False

# Pydantic models
class BusinessInputRequest(BaseModel):
    business_description: str
    company_name: Optional[str] = None
    industry: Optional[str] = None

# Demo storage for development
demo_playbooks = {}

@app.post("/api/v1/generate-playbook")
async def generate_playbook_endpoint(
    request: BusinessInputRequest,
    background_tasks: BackgroundTasks
):
    """Generate complete messaging playbook using LangGraph agents"""
    try:
        session_id = str(uuid.uuid4())
        
        # Start background processing
        background_tasks.add_task(process_playbook_langgraph, session_id, request.business_description)
        
        return {
            "session_id": session_id,
            "status": "processing",
            "estimated_completion": "2-3 minutes",
            "agent_system": "LangGraph" if langgraph_available else "Fallback"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_playbook_langgraph(session_id: str, business_input: str):
    """Background task to process playbook generation using LangGraph"""
    try:
        print(f"🚀 Starting LangGraph playbook generation for session {session_id}")
        
        if langgraph_available and agent_system:
            # Use LangGraph agent system
            result = await agent_system.generate_messaging_playbook(business_input)
        else:
            # Fallback to demo content
            print("⚠️ Using fallback demo content (LangGraph not available)")
            await asyncio.sleep(3)  # Simulate processing time
            result = generate_demo_content(business_input)
        
        # Store in demo storage
        demo_playbooks[session_id] = {
            "id": session_id,
            "user_id": "demo_user",
            "business_input": business_input,
            "results": result,
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "agent_system": "LangGraph" if langgraph_available else "Fallback"
        }
        
        print(f"✅ Playbook {session_id} completed successfully using {'LangGraph' if langgraph_available else 'Fallback'}")
        
    except Exception as e:
        print(f"❌ Error processing playbook {session_id}: {e}")
        demo_playbooks[session_id] = {
            "id": session_id,
            "user_id": "demo_user",
            "business_input": business_input,
            "results": {"error": str(e), "status": "failed"},
            "status": "failed",
            "created_at": datetime.now().isoformat(),
            "agent_system": "Error"
        }

def generate_demo_content(business_input: str) -> dict:
    """Generate demo content when LangGraph is not available"""
    return {
        "business_profile": {
            "company_name": "Demo Company",
            "industry": "Technology",
            "target_audience": "Business professionals seeking efficiency",
            "pain_points": ["Manual processes", "Time waste", "Inefficient workflows"],
            "unique_features": ["AI-powered automation", "Easy integration", "Proven results"],
            "competitors": ["Competitor A", "Competitor B", "Competitor C"],
            "tone_preference": "Professional yet approachable",
            "goals": ["Increase efficiency", "Reduce costs", "Scale operations"]
        },
        "competitor_analysis": {
            "competitor_analysis": [
                {
                    "name": "Competitor A",
                    "tagline": "Leading the Industry",
                    "value_proposition": "Comprehensive solutions for enterprise",
                    "key_messages": ["Enterprise-grade", "Scalable", "Reliable"],
                    "positioning": "Premium enterprise solution",
                    "strengths": ["Brand recognition", "Feature-rich"],
                    "weaknesses": ["Complex", "Expensive", "Slow implementation"]
                }
            ],
            "market_gaps": ["Simple solutions for SMBs", "Quick implementation", "Affordable pricing"],
            "opportunities": ["Focus on simplicity", "Rapid deployment", "SMB market"]
        },
        "positioning_strategy": {
            "unique_positioning": "The simple, fast alternative to complex enterprise solutions",
            "target_segments": ["Growing SMBs", "Teams wanting quick wins", "Cost-conscious buyers"],
            "differentiation_strategy": ["Simplicity over complexity", "Speed over features", "Results over promises"],
            "messaging_angles": ["Get results in days, not months", "Simple enough for any team", "Proven ROI"],
            "positioning_statement": "For growing businesses that want results without complexity",
            "strategic_recommendations": ["Emphasize speed", "Show quick wins", "Target SMB pain points"]
        },
        "messaging_framework": {
            "value_proposition": "Get the efficiency of enterprise tools with the simplicity your team actually wants - results in days, not months.",
            "elevator_pitch": "We help growing businesses streamline their operations without the complexity of enterprise solutions. Our platform delivers measurable results in days, not months, so you can focus on growth instead of fighting with complicated software.",
            "tagline_options": [
                "Simple. Fast. Effective.",
                "Results in Days, Not Months",
                "Efficiency Without the Complexity",
                "The Simple Path to Better Results",
                "Where Simplicity Meets Results"
            ],
            "differentiators": [
                "Implementation in days, not months - most clients see results within the first week",
                "Built for real teams, not just IT departments - anyone can use it effectively",
                "Proven ROI with an average 30% efficiency gain in the first 90 days"
            ],
            "tone_guidelines": {
                "style": "Clear, confident, and conversational",
                "personality": "Helpful expert who cuts through the noise",
                "words_to_use": ["simple", "fast", "effective", "proven", "results", "streamline"],
                "words_to_avoid": ["complex", "enterprise", "comprehensive", "advanced", "sophisticated"]
            },
            "objection_responses": [
                {
                    "objection": "We're not sure it will work for our specific industry",
                    "response": "We've helped companies in 50+ industries achieve similar results. Our approach adapts to your workflow, not the other way around."
                },
                {
                    "objection": "What if our team doesn't adopt it?",
                    "response": "Our platform is designed for real people, not just tech experts. 95% of users are productive within their first day, and we provide hands-on support during onboarding."
                },
                {
                    "objection": "How do we know we'll see ROI?",
                    "response": "Our average client sees 30% efficiency gains in 90 days. We also provide ROI tracking tools so you can measure impact from day one."
                }
            ],
            "key_messages": [
                "Simple solutions that actually work",
                "Results you can see immediately",
                "Built for real teams, not just IT",
                "Proven ROI in 90 days or less"
            ]
        },
        "content_assets": {
            "website_headlines": [
                "Stop Fighting with Complex Software - Get Results in Days",
                "The Simple Way to Streamline Your Operations",
                "Finally, Efficiency Tools That Actually Work",
                "From Chaos to Results in Less Than a Week",
                "Why Growing Companies Choose Simple Over Complex"
            ],
            "linkedin_posts": [
                "🚀 Just onboarded our 500th client this month. The #1 thing they tell us? 'I wish we'd found you sooner.' What's holding your team back from better efficiency?",
                "💡 Unpopular opinion: The best business software isn't the one with the most features - it's the one your team actually uses. Simplicity wins every time.",
                "📊 New case study: How a 75-person company saved $200K annually by switching from complex enterprise software to our simple solution. Sometimes less really is more."
            ],
            "email_templates": [
                {
                    "subject": "5 minutes to see why [Company] chose us over [Competitor]",
                    "opening": "Hi [Name], I saw that [Company] is in a similar industry to [Their Company]. They were frustrated with [common pain point] and found our approach refreshingly different. Worth a quick look?"
                },
                {
                    "subject": "The real reason teams abandon new software",
                    "opening": "Hi [Name], 73% of software implementations fail because they're too complex for real teams to adopt. What if there was a simpler way to get the results you need?"
                }
            ],
            "sales_one_liners": [
                "We're the simple alternative to complex enterprise solutions",
                "Results in days, not months - that's our promise",
                "Built for real teams, not just IT departments",
                "30% efficiency gain in 90 days - that's our average",
                "What if getting better results was actually simple?"
            ],
            "ad_copy_variations": [
                {
                    "headline": "Stop Wasting Time with Complex Software",
                    "body": "Get the efficiency you need without the complexity you don't. See results in days, not months.",
                    "cta": "See How Simple It Is"
                },
                {
                    "headline": "Why 500+ Companies Choose Simple",
                    "body": "When results matter more than features, growing companies choose our platform. Join them.",
                    "cta": "Get Started Today"
                },
                {
                    "headline": "Results in Days, Not Months",
                    "body": "While others promise future benefits, we deliver immediate results. See the difference simplicity makes.",
                    "cta": "See Immediate Results"
                }
            ],
            "social_media_posts": [
                "Simplicity isn't about having less features - it's about getting better results with less friction. #BusinessGrowth #Efficiency",
                "The best software isn't the most advanced - it's the one your team actually wants to use. #UserExperience #BusinessTools",
                "In a world of complex solutions, sometimes the simplest approach wins. #Innovation #BusinessStrategy"
            ],
            "case_study_angles": [
                "How [Company] increased productivity 30% by simplifying their workflow",
                "From implementation hell to results in 7 days: [Company]'s transformation story",
                "Why [Company] chose simple over sophisticated (and saved $200K annually)"
            ]
        },
        "quality_review": {
            "overall_quality_score": "9",
            "consistency_score": "9",
            "clarity_score": "10",
            "actionability_score": "9",
            "strengths": [
                "Clear and consistent messaging throughout",
                "Strong differentiation against complex competitors",
                "Actionable content ready for immediate use",
                "Compelling value proposition with specific benefits"
            ],
            "improvements": [
                "Consider adding more specific industry examples",
                "Include customer testimonials for proof points",
                "Add metrics to support efficiency claims"
            ],
            "consistency_issues": [],
            "recommended_refinements": [
                "Strengthen proof points with customer data",
                "Add industry-specific use cases",
                "Consider A/B testing different tagline options"
            ],
            "approval_status": "Approved with minor enhancements recommended",
            "next_steps": [
                "Test messaging with target audience",
                "Gather customer success metrics",
                "Implement across marketing channels",
                "Monitor performance and iterate"
            ]
        },
        "status": "completed",
        "generated_by": "Demo Content Generator",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/playbook-status/{session_id}")
async def get_playbook_status(session_id: str):
    """Check playbook generation status"""
    if session_id in demo_playbooks:
        playbook = demo_playbooks[session_id]
        return {
            "status": playbook["status"],
            "ready": playbook["status"] == "completed",
            "agent_system": playbook.get("agent_system", "Unknown")
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
    """Get all playbooks for current user"""
    user_playbooks = [p for p in demo_playbooks.values() if p["user_id"] == "demo_user"]
    return {"playbooks": user_playbooks}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "messagecraft-api-langgraph",
        "langgraph_available": langgraph_available,
        "version": "2.0.0"
    }

# Auth endpoints (demo mode)
@app.post("/api/v1/auth/login")
async def login():
    """User login endpoint (demo)"""
    return {
        "token": "demo_token",
        "user": {"id": "demo_user", "email": "demo@example.com", "name": "Demo User"}
    }

@app.post("/api/v1/auth/register")
async def register():
    """User registration endpoint (demo)"""
    return {
        "token": "demo_token",
        "user": {"id": "demo_user", "email": "demo@example.com", "name": "Demo User"}
    }

@app.get("/api/v1/auth/me")
async def get_current_user_info():
    """Get current user info"""
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
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)