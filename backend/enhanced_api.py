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
from database_enhanced import EnhancedDatabaseManager
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
db_manager = EnhancedDatabaseManager()
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
    agent_system = None
    try:
        # Initialize LangGraph agent system with reflection and stage tracking
        agent_system = MessageCraftAgentsWithReflection(
            quality_threshold=9.0,
            db_manager=db_manager
        )
        # Set the session ID for tracking
        agent_system.current_session_id = session_id
        
        # Run the complete workflow with session tracking
        results = await agent_system.generate_messaging_playbook(
            business_input,
            "Company",  # Default company name
            "General",  # Default industry
            questionnaire_data or {},
            session_id=session_id
        )
        
        # Save results to database
        await db_manager.save_messaging_results(session_id, results)
        
        logging.info(f"Successfully completed playbook generation for session {session_id}")
        
    except Exception as e:
        logging.error(f"Error processing playbook for session {session_id}: {str(e)}")
        # Mark final assembly as failed if we get here
        if agent_system and hasattr(agent_system, 'db_manager') and agent_system.db_manager:
            await agent_system._track_stage_progress("final_assembly", "failed", None, str(e))
        
        # Update session status to failed
        await db_manager.supabase.table("user_sessions").update({
            "status": "failed",
            "completed_at": datetime.now().isoformat()
        }).eq("id", session_id).execute()

@app.get("/api/v1/playbook-status/{session_id}")
async def get_playbook_status(session_id: str, user: UserSession = Depends(get_current_user)):
    """Get real-time status and progress for a playbook generation"""
    try:
        # Get session status
        session_result = db_manager.supabase.table("user_sessions")\
            .select("*")\
            .eq("id", session_id)\
            .eq("user_id", user.user_id)\
            .execute()
        
        if not session_result.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = session_result.data[0]
        
        # Get stage progress
        progress = await db_manager.get_generation_progress(session_id)
        
        # Calculate overall progress
        total_stages = len(progress) if progress else 11
        completed_stages = len([stage for stage in progress if stage["status"] == "completed"]) if progress else 0
        
        # Get current stage (first in_progress or failed stage)
        current_stage = None
        if progress:
            for stage in progress:
                if stage["status"] in ["in_progress", "failed"]:
                    current_stage = stage
                    break
        
        return {
            "session_id": session_id,
            "status": session["status"],
            "created_at": session["created_at"],
            "completed_at": session.get("completed_at"),
            "progress": {
                "total_stages": total_stages,
                "completed_stages": completed_stages,
                "percentage": int((completed_stages / total_stages) * 100) if total_stages > 0 else 0,
                "current_stage": current_stage,
                "stages": progress
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting playbook status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get playbook status")

@app.get("/api/v1/generation-progress/{session_id}")
async def get_generation_progress(session_id: str, user: UserSession = Depends(get_current_user)):
    """Get detailed generation progress for real-time updates"""
    try:
        # Verify session belongs to user
        session_result = db_manager.supabase.table("user_sessions")\
            .select("id, status")\
            .eq("id", session_id)\
            .eq("user_id", user.user_id)\
            .execute()
        
        if not session_result.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get stage progress
        progress = await db_manager.get_generation_progress(session_id)
        
        return {
            "session_id": session_id,
            "status": session_result.data[0]["status"],
            "stages": progress
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting generation progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get generation progress")

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
    """Download generated playbook as PDF with MessageCraft watermark"""
    try:
        # Get playbook from database
        playbook = await db_manager.get_playbook_by_id(session_id, user.user_id)
        
        if not playbook:
            raise HTTPException(status_code=404, detail="Playbook not found")
        
        if not playbook.get("results"):
            raise HTTPException(status_code=400, detail="Playbook not ready for download")
        
        # Extract company name from results or use default
        company_name = "Your Company"
        if playbook.get("results"):
            results = playbook["results"]
            if isinstance(results, dict):
                # Try to get company name from various sources
                if results.get("business_profile", {}).get("company_name"):
                    company_name = results["business_profile"]["company_name"]
                elif results.get("company_name"):
                    company_name = results["company_name"]
        
        # Generate PDF with watermark
        pdf_content = playbook_generator.generate_messaging_playbook_pdf(
            playbook["results"], 
            company_name
        )
        
        # Create filename with company name
        safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_company_name.replace(' ', '_')}_Messaging_Playbook.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error generating PDF for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

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

@app.get("/api/v1/playbooks")
async def get_playbooks(user: UserSession = Depends(get_current_user)):
    """Get all playbooks for the current user"""
    playbooks = await db_manager.get_user_playbooks(user.user_id)
    
    # Ensure all results are properly parsed
    for playbook in playbooks:
        if playbook.get("results") and isinstance(playbook["results"], str):
            try:
                playbook["results"] = json.loads(playbook["results"])
            except json.JSONDecodeError:
                logging.warning(f"Failed to parse results for playbook {playbook.get('id')}")
                playbook["results"] = {"error": "Invalid results format"}
    
    return {"playbooks": playbooks, "total": len(playbooks)}

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
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting playbook {playbook_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete playbook: {str(e)}")

@app.get("/")
@app.head("/")
async def root():
    return {"message": "MessageCraft API", "status": "running", "service": "messaging-saas"}

@app.get("/health")
@app.head("/health")
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
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
