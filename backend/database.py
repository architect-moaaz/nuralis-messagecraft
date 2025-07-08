from supabase import create_client, Client
import os
from datetime import datetime
from typing import Optional, Dict, List
import json
import logging

class DatabaseManager:
    def __init__(self):
        # Use service role key for admin operations, fallback to anon key
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            supabase_key
        )
    
    async def save_user_session(self, user_id: str, business_input: str) -> str:
        """Save user session and return session ID"""
        session_data = {
            "user_id": user_id,
            "business_input": business_input,
            "status": "processing",
            "created_at": datetime.now().isoformat()
        }
        
        result = self.supabase.table("user_sessions").insert(session_data).execute()
        return result.data[0]["id"]
    
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
        result = self.supabase.table("user_sessions").select("*").eq("user_id", user_id).execute()
        playbooks = result.data
        
        # Parse the JSON results field for each playbook
        for playbook in playbooks:
            if playbook.get("results") and isinstance(playbook["results"], str):
                try:
                    playbook["results"] = json.loads(playbook["results"])
                except json.JSONDecodeError:
                    logging.warning(f"Failed to parse results for playbook {playbook.get('id')}")
                    playbook["results"] = {}
        
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
    
    async def track_usage(self, user_id: str, plan_type: str, feature_used: str):
        """Track feature usage for billing"""
        usage_data = {
            "user_id": user_id,
            "plan_type": plan_type,
            "feature_used": feature_used,
            "timestamp": datetime.now().isoformat()
        }
        
        self.supabase.table("usage_tracking").insert(usage_data).execute()
    
    async def delete_playbook(self, playbook_id: str, user_id: str):
        """Delete a specific playbook"""
        # Verify ownership and delete
        result = self.supabase.table("user_sessions").delete().eq("id", playbook_id).eq("user_id", user_id).execute()
        
        if not result.data:
            raise Exception("Playbook not found or access denied")
    
    async def create_user(self, email: str, password_hash: str, name: str, company: Optional[str] = None) -> Dict:
        """Create a new user"""
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "name": name,
            "company": company,
            "plan_type": "basic",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            result = self.supabase.table("users").insert(user_data).execute()
            return result.data[0]
        except Exception as e:
            if "duplicate key" in str(e):
                raise Exception("User with this email already exists")
            raise e
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        result = self.supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    
    async def verify_user(self, email: str, password_hash: str) -> Optional[Dict]:
        """Verify user credentials"""
        user = await self.get_user_by_email(email)
        if user and user["password_hash"] == password_hash:
            return user
        return None