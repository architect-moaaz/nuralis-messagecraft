from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
from datetime import datetime
import uuid
import io
import os
from simple_agents import SimpleMessagingAgent
from database import DatabaseManager
from payment import PaymentManager
from pdf_generator import PlaybookGenerator

app = FastAPI(
    title="MessageCraft - Messaging & Differentiation SaaS",
    description="AI-powered messaging and differentiation platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    db_manager = DatabaseManager()
    payment_manager = PaymentManager()
    playbook_generator = PlaybookGenerator()
    messaging_agent = SimpleMessagingAgent()
except Exception as e:
    print(f"Warning: Some services failed to initialize: {e}")
    db_manager = None
    payment_manager = None
    playbook_generator = None
    messaging_agent = SimpleMessagingAgent()

# Pydantic models
class BusinessInputRequest(BaseModel):
    business_description: str
    company_name: Optional[str] = None
    industry: Optional[str] = None

class CheckoutRequest(BaseModel):
    plan_type: str
    user_email: str

class UserSession:
    def __init__(self, user_id: str, plan_type: str = "basic"):
        self.user_id = user_id
        self.plan_type = plan_type

async def get_current_user() -> UserSession:
    """Dependency to get current user (demo mode)"""
    return UserSession(user_id="demo_user", plan_type="professional")

# Demo storage for development
demo_playbooks = {}

@app.post("/api/v1/generate-playbook")
async def generate_playbook_endpoint(
    request: BusinessInputRequest,
    background_tasks: BackgroundTasks,
    user: UserSession = Depends(get_current_user)
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
        result = await messaging_agent.generate_messaging_playbook(business_input)
        
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
async def get_playbook_status(session_id: str, user: UserSession = Depends(get_current_user)):
    """Check playbook generation status"""
    if session_id in demo_playbooks:
        playbook = demo_playbooks[session_id]
        return {
            "status": playbook["status"],
            "ready": playbook["status"] == "completed"
        }
    return {"status": "not_found", "ready": False}

@app.get("/api/v1/playbook/{playbook_id}")
async def get_playbook(playbook_id: str, user: UserSession = Depends(get_current_user)):
    """Get playbook details"""
    if playbook_id in demo_playbooks:
        return demo_playbooks[playbook_id]
    raise HTTPException(status_code=404, detail="Playbook not found")

@app.get("/api/v1/download-playbook/{session_id}")
async def download_playbook(session_id: str, user: UserSession = Depends(get_current_user)):
    """Download generated playbook as PDF"""
    try:
        if session_id not in demo_playbooks:
            raise HTTPException(status_code=404, detail="Playbook not found")
        
        playbook = demo_playbooks[session_id]
        
        if not playbook_generator:
            raise HTTPException(status_code=500, detail="PDF generator not available")
        
        # Generate PDF
        company_name = playbook["results"].get("business_profile", {}).get("company_name", "Your Company")
        pdf_content = playbook_generator.generate_messaging_playbook_pdf(
            playbook["results"], 
            company_name
        )
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=playbook-{session_id}.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/create-checkout")
async def create_checkout(request: CheckoutRequest):
    """Create Stripe checkout session"""
    if not payment_manager:
        raise HTTPException(status_code=500, detail="Payment service not available")
    
    checkout_url = await payment_manager.create_checkout_session(request.plan_type, request.user_email)
    return {"checkout_url": checkout_url}

@app.post("/api/v1/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    return {"status": "received"}

@app.get("/api/v1/user/playbooks")
async def get_user_playbooks(user: UserSession = Depends(get_current_user)):
    """Get all playbooks for current user"""
    user_playbooks = [p for p in demo_playbooks.values() if p["user_id"] == user.user_id]
    return {"playbooks": user_playbooks}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "messagecraft-api"}

# Auth endpoints (demo mode)
@app.post("/api/v1/auth/login")
async def login(email: str, password: str):
    """User login endpoint (demo)"""
    return {
        "token": "demo_token",
        "user": {"id": "demo_user", "email": email, "name": "Demo User"}
    }

@app.post("/api/v1/auth/register")
async def register(email: str, password: str, name: str, company: Optional[str] = None):
    """User registration endpoint (demo)"""
    return {
        "token": "demo_token",
        "user": {"id": "demo_user", "email": email, "name": name, "company": company}
    }

@app.get("/api/v1/auth/me")
async def get_current_user_info(user: UserSession = Depends(get_current_user)):
    """Get current user info"""
    return {
        "user": {
            "id": user.user_id,
            "email": "demo@example.com",
            "name": "Demo User",
            "plan": user.plan_type
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)