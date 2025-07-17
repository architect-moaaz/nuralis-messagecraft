"""
Production-ready API with Google OAuth, Stripe Credits, and Kit Generation Limits
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Response, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, RedirectResponse, JSONResponse
import io
import json
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime
import uuid
import os
import logging
from dotenv import load_dotenv

# Import our modules
from config import settings
from auth import auth_manager, get_current_user, get_optional_user
from database_enhanced import EnhancedDatabaseManager
from payment_enhanced import EnhancedPaymentManager
from payment import PaymentManager
from langgraph_agents_with_reflection import MessageCraftAgentsWithReflection
from pdf_generator import PlaybookGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MessageCraft Production API",
    description="AI-powered messaging platform with credits system",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db_manager = EnhancedDatabaseManager()
payment_manager = EnhancedPaymentManager(db_manager)
legacy_payment_manager = PaymentManager()  # For legacy endpoints
playbook_generator = PlaybookGenerator()

# Pydantic models
class BusinessInputRequest(BaseModel):
    business_description: str
    company_name: Optional[str] = None
    industry: Optional[str] = None
    questionnaire_data: Optional[dict] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    company: Optional[str] = None

class CheckoutRequest(BaseModel):
    payment_type: str  # "subscription" or "credits"
    package_id: str    # plan name or credit package

class GoogleAuthCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None

class CheckoutRequest(BaseModel):
    plan_type: str
    user_email: str

class UserSession:
    def __init__(self, user_id: str, plan_type: str = "basic"):
        self.user_id = user_id
        self.plan_type = plan_type

# Health check
@app.get("/")
@app.head("/")
async def root():
    """Root endpoint for health checks"""
    return {
        "message": "MessageCraft Production API",
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
@app.head("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "is_production": settings.IS_PRODUCTION,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/debug/cors")
async def debug_cors():
    """Debug CORS configuration"""
    return {
        "environment": settings.ENVIRONMENT,
        "is_production": settings.IS_PRODUCTION,
        "frontend_url": settings.FRONTEND_URL,
        "cors_origins": settings.CORS_ORIGINS,
        "google_client_id": settings.GOOGLE_CLIENT_ID[:10] + "..." if settings.GOOGLE_CLIENT_ID else "Not set"
    }

# Authentication Endpoints
@app.post("/api/v1/auth/register")
async def register(request: RegisterRequest):
    """User registration with email/password"""
    try:
        # Check if user already exists
        existing_user = await db_manager.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Hash password
        password_hash = auth_manager.hash_password(request.password)
        
        # Create user
        user = await db_manager.create_user(
            email=request.email,
            name=request.name,
            password_hash=password_hash,
            company=request.company,
            auth_provider="local"
        )
        
        # Create JWT token
        token = auth_manager.create_access_token(
            user_id=user["id"],
            email=user["email"],
            plan_type=user["plan_type"]
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "plan_type": user["plan_type"],
                "credits": user["credits"],
                "free_kits_available": settings.FREE_TIER_KIT_LIMIT - user["free_kits_used"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
    """User login with email/password"""
    try:
        # Get user
        user = await db_manager.get_user_by_email(request.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not auth_manager.verify_password(request.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Update last login
        await db_manager.update_user_last_login(user["id"])
        
        # Create JWT token
        token = auth_manager.create_access_token(
            user_id=user["id"],
            email=user["email"],
            plan_type=user["plan_type"]
        )
        
        # Get credit balance
        balance = await db_manager.get_user_credit_balance(user["id"])
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "plan_type": user["plan_type"],
                "credits": balance["credits"],
                "free_kits_available": balance["free_kits_available"],
                "total_kits_generated": balance["total_kits_generated"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/api/v1/auth/google")
async def google_auth(response: Response):
    """Initiate Google OAuth flow"""
    # Add CORS headers manually
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    auth_url = auth_manager.get_google_auth_url()
    return {"auth_url": auth_url}

@app.get("/api/v1/auth/google/callback")
async def google_auth_callback_get(request: Request, response: Response):
    """Handle Google OAuth callback (GET request)"""
    # Add CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    # Get code from query parameters
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    
    return await handle_google_callback(code)

@app.post("/api/v1/auth/google/callback")
async def google_auth_callback_post(request: GoogleAuthCallbackRequest):
    """Handle Google OAuth callback (POST request)"""
    return await handle_google_callback(request.code)

async def handle_google_callback(code: str):
    """Common handler for Google OAuth callback"""
    try:
        # Exchange code for tokens
        tokens = await auth_manager.exchange_google_code(code)
        
        # Get user info from Google
        user_info = await auth_manager.get_google_user_info(tokens["access_token"])
        
        # Check if user exists
        user = await db_manager.get_user_by_google_id(user_info["id"])
        
        if not user:
            # Check if email already exists
            user = await db_manager.get_user_by_email(user_info["email"])
            
            if user:
                # Link Google account to existing user
                await db_manager.supabase.table("users").update({
                    "google_id": user_info["id"],
                    "auth_provider": "google"
                }).eq("id", user["id"]).execute()
            else:
                # Create new user
                user = await db_manager.create_user(
                    email=user_info["email"],
                    name=user_info.get("name", ""),
                    google_id=user_info["id"],
                    auth_provider="google"
                )
        
        # Update last login
        await db_manager.update_user_last_login(user["id"])
        
        # Create JWT token
        token = auth_manager.create_access_token(
            user_id=user["id"],
            email=user["email"],
            plan_type=user["plan_type"]
        )
        
        # For web OAuth flow, redirect to frontend with token (using hash router)
        frontend_url = settings.FRONTEND_URL
        redirect_url = f"{frontend_url}/#/auth/callback?token={token}"
        
        return RedirectResponse(url=redirect_url, status_code=302)
        
    except Exception as e:
        logger.error(f"Google auth error: {str(e)}")
        # Redirect to frontend with error (using hash router)
        frontend_url = settings.FRONTEND_URL
        error_url = f"{frontend_url}/#/auth/error?error=oauth_failed"
        return RedirectResponse(url=error_url, status_code=302)

@app.get("/api/v1/auth/me")
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """Get current user information"""
    user = await db_manager.get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    balance = await db_manager.get_user_credit_balance(user["id"])
    
    return {
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "plan_type": user["plan_type"],
            "credits": balance["credits"],
            "free_kits_available": balance["free_kits_available"],
            "total_kits_generated": balance["total_kits_generated"],
            "auth_provider": user["auth_provider"]
        }
    }

# Kit Generation Endpoints
@app.post("/api/v1/check-generation-eligibility")
async def check_generation_eligibility(current_user: Dict = Depends(get_current_user)):
    """Check if user can generate a kit"""
    can_generate, message, info = await db_manager.check_user_can_generate(current_user["user_id"])
    
    return {
        "can_generate": can_generate,
        "message": message,
        "credits": info.get("credits", 0),
        "free_kits_remaining": info.get("free_kits_remaining", 0)
    }

@app.post("/api/v1/generate-playbook")
async def generate_playbook_endpoint(
    request: BusinessInputRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """Generate complete messaging playbook with credit/limit checks"""
    try:
        user_id = current_user["user_id"]
        
        # Check if user can generate
        can_generate, message, info = await db_manager.check_user_can_generate(user_id)
        if not can_generate:
            raise HTTPException(status_code=403, detail=message)
        
        # Use credit or free kit
        result = await db_manager.use_kit_generation(user_id)
        if not result["success"]:
            raise HTTPException(status_code=403, detail=result["message"])
        
        # Create session
        session_id = await db_manager.save_user_session(user_id, request.business_description)
        
        # Record kit generation
        generation_type = "free" if info.get("free_kits_remaining", 0) > 0 and result.get("credits_remaining", 0) == 0 else "paid"
        await db_manager.record_kit_generation(
            user_id=user_id,
            session_id=session_id,
            business_description=request.business_description,
            company_name=request.company_name,
            industry=request.industry,
            generation_type=generation_type
        )
        
        # Track usage
        await db_manager.track_usage(user_id, current_user["plan_type"], "playbook_generation")
        
        # Initialize agents with session tracking
        agents = MessageCraftAgentsWithReflection(
            quality_threshold=9.0,
            db_manager=db_manager
        )
        # Set the session ID for tracking
        agents.current_session_id = session_id
        
        # Process in background
        background_tasks.add_task(
            process_messaging_playbook,
            agents,
            session_id,
            request.business_description,
            request.company_name,
            request.industry,
            request.questionnaire_data
        )
        
        return {
            "session_id": session_id,
            "status": "processing",
            "message": "Your messaging playbook is being generated. This usually takes 2-3 minutes.",
            "credits_remaining": result.get("credits_remaining", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Payment Endpoints
@app.get("/api/v1/pricing")
async def get_pricing():
    """Get all pricing information"""
    return payment_manager.get_pricing_info()

@app.post("/api/v1/checkout")
async def create_checkout_session(
    request: CheckoutRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Create Stripe checkout session for subscriptions or credits"""
    try:
        user = await db_manager.get_user_by_id(current_user["user_id"])
        
        checkout_url = await payment_manager.create_checkout_session(
            user_id=user["id"],
            user_email=user["email"],
            payment_type=request.payment_type,
            package_id=request.package_id
        )
        
        return {"checkout_url": checkout_url}
        
    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/verify-payment")
async def verify_payment(session_id: str):
    """Verify payment completion"""
    try:
        result = await payment_manager.handle_checkout_completion(session_id)
        return result
    except Exception as e:
        logger.error(f"Payment verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/stripe-webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        result = await payment_manager.handle_webhook(payload, sig_header)
        return result
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# User Account Endpoints
@app.get("/api/v1/credit-balance")
async def get_credit_balance(current_user: Dict = Depends(get_current_user)):
    """Get user's credit balance"""
    balance = await db_manager.get_user_credit_balance(current_user["user_id"])
    return balance

@app.get("/api/v1/credit-history")
async def get_credit_history(current_user: Dict = Depends(get_current_user)):
    """Get user's credit transaction history"""
    transactions = await db_manager.get_credit_transactions(current_user["user_id"])
    return {"transactions": transactions}

@app.get("/api/v1/playbooks")
async def get_user_playbooks(current_user: Dict = Depends(get_current_user)):
    """Get all playbooks for the current user"""
    playbooks = await db_manager.get_user_playbooks(current_user["user_id"])
    
    # Ensure all results are properly parsed
    for playbook in playbooks:
        if playbook.get("results") and isinstance(playbook["results"], str):
            try:
                playbook["results"] = json.loads(playbook["results"])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse results for playbook {playbook.get('id')}")
                playbook["results"] = {"error": "Invalid results format"}
    
    return {"playbooks": playbooks, "total": len(playbooks)}

@app.get("/api/v1/user/playbooks")
async def get_user_playbooks_alt(current_user: Dict = Depends(get_current_user)):
    """Get all playbooks for current user (alternative endpoint)"""
    playbooks = await db_manager.get_user_playbooks(current_user["user_id"])
    
    # Ensure all results are properly parsed
    for playbook in playbooks:
        if playbook.get("results") and isinstance(playbook["results"], str):
            try:
                playbook["results"] = json.loads(playbook["results"])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse results for playbook {playbook.get('id')}")
                playbook["results"] = {"error": "Invalid results format"}
    
    return {"playbooks": playbooks}

@app.get("/api/v1/playbook/{playbook_id}")
async def get_playbook(playbook_id: str, current_user: Dict = Depends(get_current_user)):
    """Get playbook details"""
    try:
        # Get playbook from database using the new method
        playbook = await db_manager.get_playbook_by_id(playbook_id, current_user["user_id"])
        
        if not playbook:
            raise HTTPException(status_code=404, detail="Playbook not found")
        
        # Ensure results are properly parsed as dict
        if playbook.get("results"):
            if isinstance(playbook["results"], str):
                try:
                    playbook["results"] = json.loads(playbook["results"])
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse results for playbook {playbook_id}")
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
        logger.error(f"Error fetching playbook {playbook_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/download-playbook/{session_id}")
async def download_playbook(session_id: str, current_user: Dict = Depends(get_current_user)):
    """Download generated playbook as PDF with MessageCraft watermark"""
    try:
        # Get playbook from database
        playbook = await db_manager.get_playbook_by_id(session_id, current_user["user_id"])
        
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
        logger.error(f"Error generating PDF for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@app.delete("/api/v1/playbook/{playbook_id}")
async def delete_playbook(playbook_id: str, current_user: Dict = Depends(get_current_user)):
    """Delete a specific playbook"""
    try:
        # Get user's playbooks to verify ownership
        playbooks = await db_manager.get_user_playbooks(current_user["user_id"])
        playbook = next((p for p in playbooks if p["id"] == playbook_id), None)
        
        if not playbook:
            raise HTTPException(status_code=404, detail="Playbook not found")
        
        # Delete the playbook from database
        await db_manager.delete_playbook(playbook_id, current_user["user_id"])
        
        return {"message": "Playbook deleted successfully", "id": playbook_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting playbook {playbook_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete playbook: {str(e)}")

@app.get("/api/v1/playbook-status/{session_id}")
async def get_playbook_status(session_id: str, current_user: Dict = Depends(get_current_user)):
    """Get real-time status and progress for a playbook generation"""
    try:
        # Get session status
        session_result = db_manager.supabase.table("user_sessions")\
            .select("*")\
            .eq("id", session_id)\
            .eq("user_id", current_user["user_id"])\
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
        logger.error(f"Error getting playbook status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get playbook status")

@app.get("/api/v1/generation-progress/{session_id}")
async def get_generation_progress(session_id: str, current_user: Dict = Depends(get_current_user)):
    """Get detailed generation progress for real-time updates"""
    try:
        # Verify session belongs to user
        session_result = db_manager.supabase.table("user_sessions")\
            .select("id, status")\
            .eq("id", session_id)\
            .eq("user_id", current_user["user_id"])\
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
        logger.error(f"Error getting generation progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get generation progress")

# Legacy simplified authentication (for backward compatibility)
async def get_current_user_legacy(authorization: Optional[str] = Header(None)) -> UserSession:
    """Dependency to get current user from token (legacy simplified version)"""
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

# Legacy endpoints for backward compatibility
@app.post("/api/v1/create-checkout")
async def create_checkout(request: CheckoutRequest):
    """Create Stripe checkout session (legacy endpoint)"""
    checkout_url = await legacy_payment_manager.create_checkout_session(request.plan_type, request.user_email)
    return {"checkout_url": checkout_url}

@app.post("/api/v1/webhook/stripe")
async def stripe_webhook_legacy(request: Request):
    """Handle Stripe webhooks (legacy endpoint)"""
    # Implement webhook handling for payment completion
    return {"status": "received"}

# Enhanced auth endpoints for backward compatibility

# Helper function
async def process_messaging_playbook(
    agents: MessageCraftAgentsWithReflection,
    session_id: str,
    business_description: str,
    company_name: Optional[str],
    industry: Optional[str],
    questionnaire_data: Optional[dict]
):
    """Process messaging playbook generation"""
    try:
        # Run the complete workflow with session tracking
        results = await agents.generate_messaging_playbook(
            business_description,
            company_name or "Your Company",
            industry or "General",
            questionnaire_data or {},
            session_id=session_id
        )
        
        # Save results to database
        await db_manager.save_messaging_results(session_id, results)
        
        logger.info(f"Successfully completed playbook generation for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error processing playbook for session {session_id}: {str(e)}")
        # Mark final assembly as failed if we get here
        if hasattr(agents, 'db_manager') and agents.db_manager:
            await agents._track_stage_progress("final_assembly", "failed", None, str(e))
        
        # Update session status to failed
        await db_manager.supabase.table("user_sessions").update({
            "status": "failed",
            "completed_at": datetime.now().isoformat()
        }).eq("id", session_id).execute()

# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)