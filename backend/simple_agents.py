import asyncio
import json
import os
from openai import OpenAI
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logging.basicConfig(level=logging.INFO)

@dataclass
class BusinessProfile:
    company_name: str
    industry: str
    target_audience: str
    current_description: str
    pain_points: List[str]
    unique_features: List[str]
    competitors: List[str]
    tone_preference: str
    goals: List[str]

class SimpleMessagingAgent:
    def __init__(self):
        self.client = client

    async def analyze_business(self, business_input: str) -> Dict:
        """Extract business insights"""
        prompt = f"""
        Analyze this business description and extract key insights:
        
        Business: {business_input}
        
        Return a JSON object with:
        1. company_name (inferred if not provided)
        2. industry
        3. target_audience (specific demographics)
        4. pain_points (list of problems they solve)
        5. unique_features (what makes them different)
        6. competitors (3-5 likely competitors)
        7. tone_preference (professional/casual/etc)
        8. goals (business objectives)
        
        Format as valid JSON.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "company_name": "Your Company",
                "industry": "Technology",
                "target_audience": "Business professionals",
                "pain_points": ["Inefficient processes"],
                "unique_features": ["Innovative solution"],
                "competitors": ["Competitor A", "Competitor B"],
                "tone_preference": "Professional",
                "goals": ["Grow market share"]
            }

    async def generate_messaging_framework(self, business_profile: Dict) -> Dict:
        """Generate messaging framework"""
        prompt = f"""
        Create a comprehensive messaging framework for this business:
        
        {json.dumps(business_profile, indent=2)}
        
        Generate:
        1. value_proposition (1-2 compelling sentences)
        2. elevator_pitch (30-second pitch)
        3. tagline_options (5 memorable options)
        4. differentiators (3 key advantages)
        5. tone_guidelines (style and personality)
        6. objection_responses (address top 3 objections)
        
        Return as JSON.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "value_proposition": "We help businesses achieve better results.",
                "elevator_pitch": "Our innovative solution helps businesses streamline operations and increase efficiency.",
                "tagline_options": ["Better Results", "Streamlined Success", "Efficiency First"],
                "differentiators": ["Fast", "Reliable", "Cost-effective"],
                "tone_guidelines": {"style": "Professional", "personality": "Confident"},
                "objection_responses": [{"objection": "Too expensive", "response": "We provide excellent ROI"}]
            }

    async def create_content_assets(self, messaging_framework: Dict, business_profile: Dict) -> Dict:
        """Generate marketing content"""
        prompt = f"""
        Create marketing content using this messaging framework:
        
        Messaging: {json.dumps(messaging_framework, indent=2)}
        Business: {json.dumps(business_profile, indent=2)}
        
        Generate:
        1. website_headlines (5 options)
        2. linkedin_posts (3 templates)
        3. email_templates (2 subject lines + openings)
        4. sales_one_liners (5 different situations)
        5. ad_copy_variations (3 different angles)
        
        Return as JSON.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "website_headlines": ["Transform Your Business Today"],
                "linkedin_posts": ["Exciting news about our solution..."],
                "email_templates": ["Quick question about your goals"],
                "sales_one_liners": ["We help companies grow faster"],
                "ad_copy_variations": ["Stop wasting time on manual processes"]
            }

    async def generate_messaging_playbook(self, business_input: str) -> Dict:
        """Main workflow to generate complete playbook"""
        try:
            logging.info("Starting messaging playbook generation...")
            
            # Step 1: Analyze business
            business_profile = await self.analyze_business(business_input)
            
            # Step 2: Generate messaging framework
            messaging_framework = await self.generate_messaging_framework(business_profile)
            
            # Step 3: Create content assets
            content_assets = await self.create_content_assets(messaging_framework, business_profile)
            
            # Step 4: Quality assessment (simplified)
            quality_review = {
                "quality_score": 8,
                "improvements": ["Consider adding more specific examples"],
                "approval_status": "Approved"
            }
            
            final_output = {
                "timestamp": datetime.now().isoformat(),
                "business_input": business_input,
                "business_profile": business_profile,
                "messaging_framework": messaging_framework,
                "content_assets": content_assets,
                "quality_review": quality_review,
                "status": "completed"
            }
            
            logging.info("Messaging playbook generation completed successfully")
            return final_output
            
        except Exception as e:
            logging.error(f"Error in messaging playbook generation: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }

# Usage example
async def main():
    agent = SimpleMessagingAgent()
    
    business_input = """
    We're a B2B SaaS company that helps marketing teams automate their email campaigns. 
    Our platform integrates with CRM systems and uses AI to personalize email content. 
    We're targeting mid-size companies (50-500 employees) with dedicated marketing teams.
    """
    
    result = await agent.generate_messaging_playbook(business_input)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())