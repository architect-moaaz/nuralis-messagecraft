#!/usr/bin/env python3
"""
Quick CORS fix for production deployment
Run this instead of production_api.py if you need to quickly allow your Vercel frontend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import everything from production_api except the app instance
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from production_api import *

# Create new app with explicit CORS for your Vercel deployment
app = FastAPI(
    title="MessageCraft API - CORS Fixed",
    description="Marketing message generation with AI",
    version="1.0.0"
)

# Add CORS middleware with your specific frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nuralis-messagecraft-erpbjssnd-athergens-projects.vercel.app",
        "http://localhost:3000",  # for local development
        "http://127.0.0.1:3000"   # for local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Import all routes from production_api
from production_api import router
app.include_router(router)

# Add all the existing routes from production_api
app.mount = production_api_app.mount
app.dependency_overrides = production_api_app.dependency_overrides

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=56001)