"""
Authentication module with Google OAuth and JWT support
"""
import os
import jwt
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

class AuthManager:
    """Handles authentication with Google OAuth and JWT tokens"""
    
    def __init__(self):
        self.google_discovery_url = "https://accounts.google.com/.well-known/openid-configuration"
        self._google_config = None
    
    async def get_google_config(self) -> Dict[str, Any]:
        """Get Google OAuth configuration"""
        if not self._google_config:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.google_discovery_url)
                self._google_config = response.json()
        return self._google_config
    
    def create_access_token(self, user_id: str, email: str, plan_type: str = "basic") -> str:
        """Create JWT access token"""
        payload = {
            "sub": user_id,
            "email": email,
            "plan_type": plan_type,
            "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_google_auth_url(self, state: Optional[str] = None) -> str:
        """Generate Google OAuth authorization URL"""
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent"
        }
        if state:
            params["state"] = state
        
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    async def exchange_google_code(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange code")
            return response.json()
    
    async def get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from Google"""
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(user_info_url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user info")
            return response.json()

# Create auth manager instance
auth_manager = AuthManager()

# Dependency to get current user from JWT token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    token = credentials.credentials
    try:
        payload = auth_manager.verify_token(token)
        return {
            "user_id": payload["sub"],
            "email": payload["email"],
            "plan_type": payload.get("plan_type", "basic")
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Optional dependency - returns None if no auth
async def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user if authenticated, otherwise None"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.replace("Bearer ", "")
        payload = auth_manager.verify_token(token)
        return {
            "user_id": payload["sub"],
            "email": payload["email"],
            "plan_type": payload.get("plan_type", "basic")
        }
    except:
        return None