from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
from datetime import datetime
import uuid
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="MessageCraft API",
    description="AI-powered messaging and differentiation platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    print(f"Warning: OpenAI client not initialized: {e}")
    client = None

# Pydantic models
class BusinessInputRequest(BaseModel):
    business_description: str
    company_name: Optional[str] = None
    industry: Optional[str] = None

# Demo storage
demo_playbooks = {}

async def generate_messaging_content(business_input: str) -> dict:
    """Generate messaging content using OpenAI"""
    if not client:
        # Return demo content if OpenAI is not configured
        return {
            "business_profile": {
                "company_name": "Demo Company",
                "industry": "Technology",
                "target_audience": "Business professionals",
                "pain_points": ["Inefficient processes", "Poor communication"],
                "unique_features": ["AI-powered", "Easy to use"],
                "competitors": ["Competitor A", "Competitor B"],
                "tone_preference": "Professional",
                "goals": ["Increase efficiency", "Improve communication"]
            },
            "messaging_framework": {
                "value_proposition": "We help businesses streamline their operations with AI-powered solutions.",
                "elevator_pitch": "Our platform uses artificial intelligence to automate repetitive tasks, allowing your team to focus on what matters most - growing your business.",
                "tagline_options": [
                    "Automate. Optimize. Succeed.",
                    "Smart Solutions for Smart Businesses",
                    "Where AI Meets Efficiency",
                    "Transform Your Workflow",
                    "The Future of Business Operations"
                ],
                "differentiators": [
                    "AI-powered automation that learns from your business",
                    "Integration with existing tools and workflows",
                    "24/7 support and dedicated account management"
                ],
                "tone_guidelines": {
                    "style": "Professional yet approachable",
                    "personality": "Confident, helpful, innovative",
                    "words_to_use": ["streamline", "optimize", "efficient", "intelligent"],
                    "words_to_avoid": ["complicated", "overwhelming", "traditional"]
                },
                "objection_responses": [
                    {
                        "objection": "It's too expensive",
                        "response": "Our ROI calculator shows most clients save 20-30% on operational costs within the first quarter."
                    },
                    {
                        "objection": "We're not ready for AI",
                        "response": "Our platform is designed for easy adoption with minimal training required - most teams are productive within a week."
                    },
                    {
                        "objection": "What about data security?",
                        "response": "We use enterprise-grade encryption and comply with SOC2 and GDPR standards to keep your data secure."
                    }
                ]
            },
            "content_assets": {
                "website_headlines": [
                    "Transform Your Business with AI-Powered Automation",
                    "Stop Wasting Time on Manual Tasks - Automate Everything",
                    "The Smart Way to Scale Your Operations",
                    "From Chaos to Control: AI That Actually Works",
                    "Finally, AI That Understands Your Business"
                ],
                "linkedin_posts": [
                    "🚀 Just helped another client save 15 hours per week with intelligent automation. What manual process is holding your team back?",
                    "💡 Pro tip: The best AI solutions don't replace your team - they amplify their capabilities. Here's how we're doing it...",
                    "📊 New case study: How a 50-person company increased productivity by 40% in 90 days. The secret? Smart automation that adapts."
                ],
                "email_templates": [
                    "Subject: Quick question about your current workflow\nHi [Name], I noticed your team might be spending a lot of time on [specific process]. Would you be interested in seeing how companies like yours are automating this?",
                    "Subject: 15 minutes to save 15 hours per week?\nHi [Name], I have a quick demo that shows exactly how [similar company] eliminated their biggest workflow bottleneck. Worth a quick look?"
                ],
                "sales_one_liners": [
                    "We help businesses like yours eliminate 80% of manual data entry",
                    "Most of our clients see ROI within 60 days of implementation",
                    "Think of us as your business operations on autopilot",
                    "We turn your repetitive tasks into automated workflows",
                    "Your competition is already automating - are you?"
                ],
                "ad_copy_variations": [
                    "Stop doing work a computer should handle. Automate your workflows in minutes, not months.",
                    "What if your biggest operational headaches just... disappeared? See how AI automation is changing everything.",
                    "Your team is too valuable to waste on manual tasks. Discover intelligent automation that actually works."
                ]
            },
            "quality_review": {
                "quality_score": 9,
                "improvements": [
                    "Consider adding more industry-specific examples",
                    "Include customer testimonials in sales materials"
                ],
                "approval_status": "Approved with minor suggestions"
            },
            "status": "completed"
        }
    
    try:
        # Comprehensive prompt for OpenAI
        prompt = f"""
        As an expert marketing strategist and copywriter, create a comprehensive messaging playbook for this business:
        
        Business Description: {business_input}
        
        Create a detailed JSON response with the following structure:
        
        {{
            "business_profile": {{
                "company_name": "inferred or provided company name",
                "industry": "specific industry",
                "target_audience": "detailed target audience description",
                "pain_points": ["specific problems this business solves"],
                "unique_features": ["what makes this business different"],
                "competitors": ["3-5 likely competitors"],
                "tone_preference": "recommended tone of voice",
                "goals": ["business objectives"]
            }},
            "messaging_framework": {{
                "value_proposition": "compelling 1-2 sentence value proposition",
                "elevator_pitch": "30-second elevator pitch",
                "tagline_options": ["5 memorable tagline options"],
                "differentiators": ["3 key competitive advantages"],
                "tone_guidelines": {{
                    "style": "writing style description",
                    "personality": "brand personality traits",
                    "words_to_use": ["positive words to include"],
                    "words_to_avoid": ["words to avoid"]
                }},
                "objection_responses": [
                    {{"objection": "common objection", "response": "persuasive response"}},
                    {{"objection": "another objection", "response": "another response"}},
                    {{"objection": "third objection", "response": "third response"}}
                ]
            }},
            "content_assets": {{
                "website_headlines": ["5 compelling website headlines"],
                "linkedin_posts": ["3 LinkedIn post templates"],
                "email_templates": ["2 email templates with subject lines"],
                "sales_one_liners": ["5 sales one-liners for different situations"],
                "ad_copy_variations": ["3 ad copy variations with different angles"]
            }},
            "quality_review": {{
                "quality_score": 8,
                "improvements": ["suggested improvements"],
                "approval_status": "assessment status"
            }}
        }}
        
        Make everything specific, actionable, and tailored to this exact business. Ensure all content is professional, compelling, and ready to use.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=4000
        )
        
        result = json.loads(response.choices[0].message.content)
        result["status"] = "completed"
        return result
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        # Return demo content on error
        result = await generate_messaging_content("")  # Call recursively without client
        result["status"] = "completed"
        return result

@app.post("/api/v1/generate-playbook")
async def generate_playbook_endpoint(
    request: BusinessInputRequest,
    background_tasks: BackgroundTasks
):
    """Generate complete messaging playbook"""
    try:
        session_id = str(uuid.uuid4())
        
        # Start background processing
        background_tasks.add_task(process_playbook, session_id, request.business_description)
        
        return {
            "session_id": session_id,
            "status": "processing",
            "estimated_completion": "2-3 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_playbook(session_id: str, business_input: str):
    """Background task to process playbook generation"""
    try:
        print(f"Starting playbook generation for session {session_id}")
        
        # Simulate some processing time
        await asyncio.sleep(2)
        
        result = await generate_messaging_content(business_input)
        
        # Store in demo storage
        demo_playbooks[session_id] = {
            "id": session_id,
            "user_id": "demo_user",
            "business_input": business_input,
            "results": result,
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat()
        }
        
        print(f"Playbook {session_id} completed successfully")
        
    except Exception as e:
        print(f"Error processing playbook {session_id}: {e}")
        demo_playbooks[session_id] = {
            "id": session_id,
            "user_id": "demo_user",
            "business_input": business_input,
            "results": {"error": str(e), "status": "failed"},
            "status": "failed",
            "created_at": datetime.now().isoformat()
        }

@app.get("/api/v1/playbook-status/{session_id}")
async def get_playbook_status(session_id: str):
    """Check playbook generation status"""
    if session_id in demo_playbooks:
        playbook = demo_playbooks[session_id]
        return {
            "status": playbook["status"],
            "ready": playbook["status"] == "completed"
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
        "service": "messagecraft-api",
        "openai_configured": client is not None
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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)