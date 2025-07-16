"""
Production-ready API with Google OAuth, Stripe Credits, and Kit Generation Limits
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, RedirectResponse, JSONResponse
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
    allow_origins=["*"] if not settings.IS_PRODUCTION else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db_manager = EnhancedDatabaseManager()
payment_manager = EnhancedPaymentManager(db_manager)
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
async def google_auth():
    """Initiate Google OAuth flow"""
    auth_url = auth_manager.get_google_auth_url()
    return {"auth_url": auth_url}

@app.post("/api/v1/auth/google/callback")
async def google_auth_callback(request: GoogleAuthCallbackRequest):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for tokens
        tokens = await auth_manager.exchange_google_code(request.code)
        
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
    except Exception as e:
        logger.error(f"Google auth error: {str(e)}")
        raise HTTPException(status_code=500, detail="Google authentication failed")

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
        
        # Initialize agents
        agents = MessageCraftAgentsWithReflection(quality_threshold=9.0)
        
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
    return {"playbooks": playbooks, "total": len(playbooks)}

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
        # Run the complete workflow
        results = await agents.run_complete_workflow(
            business_description,
            company_name or "Your Company",
            industry or "General",
            questionnaire_data or {}
        )
        
        # Save results to database
        await db_manager.save_messaging_results(session_id, results)
        
        logger.info(f"Successfully completed playbook generation for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error processing playbook for session {session_id}: {str(e)}")
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