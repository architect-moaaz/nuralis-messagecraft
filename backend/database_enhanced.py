"""
Enhanced Database Manager with Credit System and Google OAuth Support
"""
from supabase import create_client, Client
import os
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import json
import logging
from config import settings

class EnhancedDatabaseManager:
    def __init__(self):
        # Use service role key for admin operations
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
    
    # User Management
    async def create_user(
        self,
        email: str,
        name: str,
        password_hash: Optional[str] = None,
        google_id: Optional[str] = None,
        auth_provider: str = "local",
        company: Optional[str] = None
    ) -> Dict:
        """Create a new user account"""
        logging.info(f"Creating user: email={email}, name={name}, auth_provider={auth_provider}")
        
        user_data = {
            "email": email,
            "name": name,
            "company": company,
            "auth_provider": auth_provider,
            "created_at": datetime.now().isoformat(),
            "plan_type": "basic",
            "credits": 0,
            "free_kits_used": 0,
            "total_kits_generated": 0
        }
        
        if password_hash:
            user_data["password_hash"] = password_hash
            logging.info("Password hash added to user data")
        if google_id:
            user_data["google_id"] = google_id
            logging.info("Google ID added to user data")
        
        logging.info("Inserting user into Supabase...")
        try:
            result = self.supabase.table("users").insert(user_data).execute()
            logging.info(f"Supabase insert result: {len(result.data)} rows created")
            if result.data:
                logging.info(f"Created user with ID: {result.data[0].get('id', 'unknown')}")
                return result.data[0]
            else:
                logging.error("No data returned from Supabase insert")
                raise Exception("No data returned from user creation")
        except Exception as e:
            logging.error(f"Supabase insert failed: {str(e)}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        result = self.supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    
    async def get_user_by_google_id(self, google_id: str) -> Optional[Dict]:
        """Get user by Google ID"""
        result = self.supabase.table("users").select("*").eq("google_id", google_id).execute()
        return result.data[0] if result.data else None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        result = self.supabase.table("users").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None
    
    async def update_user_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        result = self.supabase.table("users").update({
            "last_login": datetime.now().isoformat()
        }).eq("id", user_id).execute()
        return result
    
    async def update_user_plan(self, user_id: str, plan_type: str):
        """Update user's subscription plan"""
        self.supabase.table("users").update({
            "plan_type": plan_type,
            "updated_at": datetime.now().isoformat()
        }).eq("id", user_id).execute()
    
    # Credit System
    async def check_user_can_generate(self, user_id: str) -> Tuple[bool, str, Dict]:
        """Check if user can generate a kit"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False, "User not found", {}
        
        if settings.IS_PRODUCTION:
            # Production mode - check credits and free tier
            if user["credits"] > 0:
                return True, "Credits available", {"credits": user["credits"]}
            elif user["free_kits_used"] < settings.FREE_TIER_KIT_LIMIT:
                return True, "Free kit available", {"free_kits_remaining": settings.FREE_TIER_KIT_LIMIT - user["free_kits_used"]}
            else:
                return False, "No credits available. Please purchase credits to continue.", {"credits": 0}
        else:
            # Development mode - always allow
            return True, "Development mode - unlimited generation", {"credits": -1}
    
    async def use_kit_generation(self, user_id: str) -> Dict:
        """Use a credit or free kit for generation"""
        # Call database function directly
        result = self.supabase.rpc("use_kit_generation", {"p_user_id": user_id}).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            return {"success": False, "message": "Failed to process kit generation"}
    
    async def add_user_credits(
        self,
        user_id: str,
        credits: int,
        stripe_payment_intent_id: Optional[str] = None,
        description: str = "Credit purchase"
    ) -> int:
        """Add credits to user account"""
        result = self.supabase.rpc("add_user_credits", {
            "p_user_id": user_id,
            "p_credits": credits,
            "p_stripe_payment_intent_id": stripe_payment_intent_id,
            "p_description": description
        }).execute()
        
        return result.data if result.data is not None else 0
    
    async def get_user_credit_balance(self, user_id: str) -> Dict:
        """Get user's credit balance and usage info"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return {"credits": 0, "free_kits_used": 0, "total_kits_generated": 0}
        
        return {
            "credits": user["credits"],
            "free_kits_used": user["free_kits_used"],
            "free_kits_available": max(0, settings.FREE_TIER_KIT_LIMIT - user["free_kits_used"]),
            "total_kits_generated": user["total_kits_generated"]
        }
    
    async def get_credit_transactions(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's credit transaction history"""
        result = self.supabase.table("credit_transactions")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return result.data
    
    # Kit Generation Tracking
    async def record_kit_generation(
        self,
        user_id: str,
        session_id: str,
        business_description: str,
        company_name: Optional[str] = None,
        industry: Optional[str] = None,
        generation_type: str = "paid"
    ) -> str:
        """Record a kit generation"""
        generation_data = {
            "user_id": user_id,
            "session_id": session_id,
            "business_description": business_description,
            "company_name": company_name,
            "industry": industry,
            "generation_type": generation_type,
            "credits_used": 1 if generation_type == "paid" else 0,
            "created_at": datetime.now().isoformat()
        }
        
        result = self.supabase.table("kit_generations").insert(generation_data).execute()
        return result.data[0]["id"]
    
    # Session Management (existing methods)
    async def save_user_session(self, user_id: str, business_input: str) -> str:
        """Save user session and return session ID"""
        session_data = {
            "user_id": user_id,
            "business_input": business_input,
            "status": "processing",
            "created_at": datetime.now().isoformat()
        }
        
        result = self.supabase.table("user_sessions").insert(session_data).execute()
        session_id = result.data[0]["id"]
        
        # Initialize generation stages
        await self.initialize_generation_stages(session_id)
        
        return session_id
    
    async def initialize_generation_stages(self, session_id: str) -> None:
        """Initialize generation stages for a session"""
        try:
            self.supabase.rpc('initialize_generation_stages', {'p_session_id': session_id}).execute()
        except Exception as e:
            logging.error(f"Failed to initialize generation stages: {e}")
    
    async def update_stage_status(self, session_id: str, stage_name: str, status: str, 
                                 stage_data: Optional[Dict] = None, error_message: Optional[str] = None) -> None:
        """Update the status of a generation stage"""
        try:
            params = {
                'p_session_id': session_id,
                'p_stage_name': stage_name,
                'p_status': status,
                'p_stage_data': stage_data,
                'p_error_message': error_message
            }
            self.supabase.rpc('update_stage_status', params).execute()
        except Exception as e:
            logging.error(f"Failed to update stage status: {e}")
    
    async def get_generation_progress(self, session_id: str) -> List[Dict]:
        """Get generation progress for a session"""
        try:
            result = self.supabase.rpc('get_generation_progress', {'p_session_id': session_id}).execute()
            return result.data or []
        except Exception as e:
            logging.error(f"Failed to get generation progress: {e}")
            
            # Fallback: Try to get progress from generation_stages table directly
            try:
                logging.info("Trying fallback method: querying generation_stages table directly")
                result = self.supabase.table("generation_stages")\
                    .select("stage_name, stage_display_name, stage_order, status, started_at, completed_at, stage_data, error_message")\
                    .eq("session_id", session_id)\
                    .order("stage_order")\
                    .execute()
                
                if result.data:
                    logging.info(f"Fallback successful: found {len(result.data)} stages")
                    return result.data
                else:
                    logging.info("No generation stages found for session")
                    return []
            except Exception as fallback_error:
                logging.error(f"Fallback method also failed: {fallback_error}")
                # Return mock stages for better UX
                return self._get_mock_generation_stages()
    
    def _get_mock_generation_stages(self) -> List[Dict]:
        """Return mock generation stages when database function is not available"""
        return [
            {
                "stage_name": "business_discovery",
                "stage_display_name": "Business Discovery",
                "stage_order": 1,
                "status": "completed",
                "started_at": None,
                "completed_at": None,
                "stage_data": None,
                "error_message": None
            },
            {
                "stage_name": "messaging_generator",
                "stage_display_name": "Messaging Framework",
                "stage_order": 7,
                "status": "completed",
                "started_at": None,
                "completed_at": None,
                "stage_data": None,
                "error_message": None
            },
            {
                "stage_name": "final_assembly",
                "stage_display_name": "Final Assembly",
                "stage_order": 11,
                "status": "completed",
                "started_at": None,
                "completed_at": None,
                "stage_data": None,
                "error_message": None
            }
        ]
    
    async def save_messaging_results(self, session_id: str, results: Dict):
        """Save complete messaging playbook results"""
        update_data = {
            "results": json.dumps(results),
            "status": "completed",
            "completed_at": datetime.now().isoformat()
        }
        
        self.supabase.table("user_sessions").update(update_data).eq("id", session_id).execute()
    
    async def get_user_playbooks(self, user_id: str) -> List[Dict]:
        """Get all playbooks for a user"""
        result = self.supabase.table("user_sessions")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        
        playbooks = result.data
        
        # Parse the JSON results field for each playbook
        for playbook in playbooks:
            if playbook.get("results") and isinstance(playbook["results"], str):
                try:
                    playbook["results"] = json.loads(playbook["results"])
                except json.JSONDecodeError:
                    logging.warning(f"Failed to parse results for playbook {playbook.get('id')}")
                    playbook["results"] = None
        
        return playbooks
    
    async def get_playbook_by_id(self, playbook_id: str, user_id: str) -> Optional[Dict]:
        """Get a single playbook by ID"""
        result = self.supabase.table("user_sessions").select("*").eq("id", playbook_id).eq("user_id", user_id).execute()
        
        if not result.data:
            return None
            
        playbook = result.data[0]
        
        # Parse the JSON results field
        if playbook.get("results") and isinstance(playbook["results"], str):
            try:
                playbook["results"] = json.loads(playbook["results"])
            except json.JSONDecodeError:
                logging.warning(f"Failed to parse results for playbook {playbook.get('id')}")
                playbook["results"] = {}
                
        return playbook
    
    async def delete_playbook(self, playbook_id: str, user_id: str):
        """Delete a specific playbook and all related records"""
        # First verify ownership
        session_result = self.supabase.table("user_sessions")\
            .select("id")\
            .eq("id", playbook_id)\
            .eq("user_id", user_id)\
            .execute()
        
        if not session_result.data:
            raise Exception("Playbook not found or access denied")
        
        # Delete in correct order to handle foreign key constraints
        # 1. Delete kit_generations records (has FK to user_sessions without CASCADE)
        kit_gen_result = self.supabase.table("kit_generations")\
            .delete()\
            .eq("session_id", playbook_id)\
            .execute()
        
        # 2. Delete generation_stages records (has FK with CASCADE, but delete explicitly for clarity)
        stages_result = self.supabase.table("generation_stages")\
            .delete()\
            .eq("session_id", playbook_id)\
            .execute()
        
        # 3. Finally delete the user_sessions record
        result = self.supabase.table("user_sessions")\
            .delete()\
            .eq("id", playbook_id)\
            .eq("user_id", user_id)\
            .execute()
        
        if not result.data:
            raise Exception("Failed to delete playbook")
    
    # Payment Management
    async def record_payment(
        self,
        user_id: str,
        stripe_session_id: str,
        amount: int,
        payment_type: str = "subscription",
        plan_type: Optional[str] = None,
        credits_purchased: Optional[int] = None,
        stripe_payment_intent_id: Optional[str] = None,
        status: str = "completed"
    ) -> str:
        """Record a payment transaction"""
        payment_data = {
            "user_id": user_id,
            "stripe_session_id": stripe_session_id,
            "stripe_payment_intent_id": stripe_payment_intent_id,
            "amount": amount,
            "payment_type": payment_type,
            "plan_type": plan_type,
            "credits_purchased": credits_purchased,
            "status": status,
            "created_at": datetime.now().isoformat()
        }
        
        result = self.supabase.table("payments").insert(payment_data).execute()
        return result.data[0]["id"]
    
    # Usage Tracking
    async def track_usage(self, user_id: str, plan_type: str, feature_used: str):
        """Track feature usage"""
        usage_data = {
            "user_id": user_id,
            "plan_type": plan_type,
            "feature_used": feature_used,
            "timestamp": datetime.now().isoformat()
        }
        
        self.supabase.table("usage_tracking").insert(usage_data).execute()
    
    # Authentication (legacy support)
    async def verify_user(self, email: str, password_hash: str) -> Optional[Dict]:
        """Verify user credentials (for local auth)"""
        result = self.supabase.table("users")\
            .select("*")\
            .eq("email", email)\
            .eq("password_hash", password_hash)\
            .execute()
        
        if result.data:
            user = result.data[0]
            await self.update_user_last_login(user["id"])
            return user
        return None