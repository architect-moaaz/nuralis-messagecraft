from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
from datetime import datetime
import uuid
import io
import os
import logging
import json
from dotenv import load_dotenv
from langgraph_agents_with_reflection import MessageCraftAgentsWithReflection
from database import DatabaseManager
from payment import PaymentManager
from pdf_generator import PlaybookGenerator

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Messaging & Differentiation SaaS",
    description="AI-powered messaging and differentiation platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db_manager = DatabaseManager()
payment_manager = PaymentManager()
playbook_generator = PlaybookGenerator()

# Pydantic models
class BusinessInputRequest(BaseModel):
    business_description: str
    company_name: Optional[str] = None
    industry: Optional[str] = None
    questionnaire_data: Optional[dict] = None

class CheckoutRequest(BaseModel):
    plan_type: str
    user_email: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    company: Optional[str] = None

class UserSession:
    def __init__(self, user_id: str, plan_type: str = "basic"):
        self.user_id = user_id
        self.plan_type = plan_type

async def get_current_user(authorization: Optional[str] = Header(None)) -> UserSession:
    """Dependency to get current user from token"""
    if not authorization or not authorization.startswith("Bearer "):
        # Return demo user if no auth (for testing)
        return UserSession(user_id="demo_user", plan_type="professional")
    
    try:
        token = authorization.replace("Bearer ", "")
        # Simple token parsing (use JWT in production)
        if token.startswith("token_"):
            parts = token.split("_")
            if len(parts) >= 2:
                user_id = parts[1]
                return UserSession(user_id=user_id, plan_type="professional")
    except Exception:
        pass
    
    # Return demo user as fallback
    return UserSession(user_id="demo_user", plan_type="professional")

@app.post("/api/v1/generate-playbook")
async def generate_playbook_endpoint(
    request: BusinessInputRequest,
    background_tasks: BackgroundTasks,
    user: UserSession = Depends(get_current_user)
):
    """Generate complete messaging playbook"""
    try:
        # Create session
        session_id = await db_manager.save_user_session(user.user_id, request.business_description)
        
        # Track usage
        await db_manager.track_usage(user.user_id, user.plan_type, "playbook_generation")
        
        # Start background processing
        background_tasks.add_task(
            process_playbook, 
            session_id, 
            request.business_description,
            request.questionnaire_data
        )
        
        return {
            "session_id": session_id,
            "status": "processing",
            "estimated_completion": "2-3 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_playbook(session_id: str, business_input: str, questionnaire_data: Optional[dict] = None):
    """Background task to process playbook generation"""
    try:
        # Initialize LangGraph agent system with reflection
        agent_system = MessageCraftAgentsWithReflection(
            quality_threshold=8.0,
            max_reflection_cycles=2
        )
        results = await agent_system.generate_messaging_playbook(business_input, questionnaire_data)
        await db_manager.save_messaging_results(session_id, results)
    except Exception as e:
        # Handle errors and update session status
        error_result = {"error": str(e), "status": "failed"}
        await db_manager.save_messaging_results(session_id, error_result)

@app.get("/api/v1/playbook-status/{session_id}")
async def get_playbook_status(session_id: str, user: UserSession = Depends(get_current_user)):
    """Check playbook generation status"""
    # Implement status checking logic
    return {"status": "completed", "ready": True}

@app.get("/api/v1/playbook/{playbook_id}")
async def get_playbook(playbook_id: str, user: UserSession = Depends(get_current_user)):
    """Get playbook details"""
    try:
        # Get playbook from database using the new method
        playbook = await db_manager.get_playbook_by_id(playbook_id, user.user_id)
        
        if not playbook:
            raise HTTPException(status_code=404, detail="Playbook not found")
        
        # Ensure results are properly parsed as dict
        if playbook.get("results"):
            if isinstance(playbook["results"], str):
                try:
                    playbook["results"] = json.loads(playbook["results"])
                except json.JSONDecodeError:
                    logging.warning(f"Failed to parse results for playbook {playbook_id}")
                    playbook["results"] = {"error": "Invalid results format"}
        else:
            playbook["results"] = {
                "error": "No results available", 
                "status": playbook.get("status", "unknown")
            }
        
        return playbook
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching playbook {playbook_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/download-playbook/{session_id}")
async def download_playbook(session_id: str, user: UserSession = Depends(get_current_user)):
    """Download generated playbook as PDF"""
    try:
        # Get results from database
        playbooks = await db_manager.get_user_playbooks(user.user_id)
        playbook = next((p for p in playbooks if p["id"] == session_id), None)
        
        if not playbook:
            raise HTTPException(status_code=404, detail="Playbook not found")
        
        # Generate PDF
        pdf_content = playbook_generator.generate_messaging_playbook_pdf(
            playbook["results"], 
            playbook.get("company_name", "Your Company")
        )
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=messaging-playbook.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/create-checkout")
async def create_checkout(request: CheckoutRequest):
    """Create Stripe checkout session"""
    checkout_url = await payment_manager.create_checkout_session(request.plan_type, request.user_email)
    return {"checkout_url": checkout_url}

@app.post("/api/v1/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    # Implement webhook handling for payment completion
    return {"status": "received"}

@app.get("/api/v1/user/playbooks")
async def get_user_playbooks(user: UserSession = Depends(get_current_user)):
    """Get all playbooks for current user"""
    playbooks = await db_manager.get_user_playbooks(user.user_id)
    
    # Ensure all results are properly parsed
    for playbook in playbooks:
        if playbook.get("results") and isinstance(playbook["results"], str):
            try:
                playbook["results"] = json.loads(playbook["results"])
            except json.JSONDecodeError:
                logging.warning(f"Failed to parse results for playbook {playbook.get('id')}")
                playbook["results"] = {"error": "Invalid results format"}
    
    return {"playbooks": playbooks}

@app.delete("/api/v1/playbook/{playbook_id}")
async def delete_playbook(playbook_id: str, user: UserSession = Depends(get_current_user)):
    """Delete a specific playbook"""
    try:
        # Get user's playbooks to verify ownership
        playbooks = await db_manager.get_user_playbooks(user.user_id)
        playbook = next((p for p in playbooks if p["id"] == playbook_id), None)
        
        if not playbook:
            raise HTTPException(status_code=404, detail="Playbook not found")
        
        # Delete the playbook from database
        await db_manager.delete_playbook(playbook_id, user.user_id)
        
        return {"message": "Playbook deleted successfully", "id": playbook_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "messaging-saas"}

# Auth endpoints (simplified)
@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
    """User login endpoint"""
    try:
        # Simple password hashing (use bcrypt in production)
        import hashlib
        password_hash = hashlib.sha256(request.password.encode()).hexdigest()
        
        # Verify user
        user = await db_manager.verify_user(request.email, password_hash)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Generate simple token (use JWT in production)
        token = f"token_{user['id']}_{datetime.now().timestamp()}"
        
        return {
            "token": token,
            "user": {
                "id": user["id"], 
                "email": user["email"], 
                "name": user["name"],
                "company": user.get("company"),
                "plan_type": user.get("plan_type", "basic")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/auth/register")
async def register(request: RegisterRequest):
    """User registration endpoint"""
    try:
        # Check if user already exists
        existing_user = await db_manager.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Simple password hashing (use bcrypt in production)
        import hashlib
        password_hash = hashlib.sha256(request.password.encode()).hexdigest()
        
        # Create user
        user = await db_manager.create_user(
            email=request.email,
            password_hash=password_hash,
            name=request.name,
            company=request.company
        )
        
        # Generate simple token (use JWT in production)
        token = f"token_{user['id']}_{datetime.now().timestamp()}"
        
        return {
            "token": token,
            "user": {
                "id": user["id"], 
                "email": user["email"], 
                "name": user["name"],
                "company": user.get("company"),
                "plan_type": user.get("plan_type", "basic")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    uvicorn.run(app, host="0.0.0.0")
