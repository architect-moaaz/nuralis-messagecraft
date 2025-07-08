import asyncio
import json
import os
from openai import OpenAI
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logging.basicConfig(level=logging.INFO)

# Data Models
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

@dataclass
class CompetitorData:
    name: str
    tagline: str
    value_proposition: str
    key_messages: List[str]
    positioning: str
    strengths: List[str]
    weaknesses: List[str]

@dataclass
class MessagingFramework:
    elevator_pitch: str
    value_proposition: str
    tagline_options: List[str]
    differentiators: List[str]
    tone_guidelines: Dict[str, str]
    target_objections: List[Dict[str, str]]

@dataclass
class ContentAssets:
    website_headlines: List[str]
    linkedin_posts: List[str]
    email_templates: List[str]
    sales_one_liners: List[str]
    ad_copy_variations: List[str]

# Custom Tools
class BusinessDiscoveryTool(BaseTool):
    name: str = "business_discovery"
    description: str = "Conducts intelligent questioning to extract business insights"
    
    def _run(self, business_input: str) -> Dict:
        """Enhanced discovery with intelligent follow-up questions"""
        discovery_prompt = f"""
        As a business discovery expert, analyze this initial business description and create a comprehensive business profile:
        
        Business Input: {business_input}
        
        Extract and infer:
        1. Company name and industry
        2. Target audience (be specific about demographics, role, company size)
        3. Core pain points the business solves
        4. Unique features or capabilities
        5. Likely competitors (research and suggest 3-5)
        6. Business goals and objectives
        7. Recommended tone of voice based on industry and audience
        
        Return structured JSON with detailed insights.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": discovery_prompt}],
            temperature=0.3
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            return result
        except:
            # Fallback parsing if JSON fails
            return self._parse_discovery_fallback(response.choices[0].message.content)
    
    def _parse_discovery_fallback(self, content: str) -> Dict:
        """Backup parsing method"""
        return {
            "company_name": "Unknown",
            "industry": "General",
            "target_audience": "Business owners",
            "pain_points": ["Unclear messaging"],
            "unique_features": ["To be determined"],
            "competitors": [],
            "tone_preference": "Professional",
            "goals": ["Better messaging"]
        }

class CompetitorResearchTool(BaseTool):
    name: str = "competitor_research"
    description: str = "Analyzes competitor messaging and positioning"
    
    def _run(self, competitors: List[str], industry: str) -> List[Dict]:
        """Research competitor messaging"""
        competitor_data = []
        
        for competitor in competitors[:5]:  # Limit to 5 competitors
            try:
                # Simulate web scraping (replace with actual implementation)
                data = self._analyze_competitor(competitor, industry)
                competitor_data.append(data)
            except Exception as e:
                logging.warning(f"Failed to analyze {competitor}: {e}")
                continue
                
        return competitor_data
    
    def _analyze_competitor(self, competitor: str, industry: str) -> Dict:
        """Analyze individual competitor (mock implementation)"""
        # In production, use web scraping tools like Apify, SerpAPI, or Scrapy
        analysis_prompt = f"""
        As a competitive intelligence expert, provide analysis for competitor: {competitor} in {industry} industry.
        
        Provide realistic analysis including:
        1. Likely tagline/main message
        2. Value proposition approach
        3. Key differentiators they claim
        4. Positioning strategy
        5. Strengths in messaging
        6. Potential weaknesses or gaps
        
        Base this on typical patterns for companies in {industry}.
        Return as structured JSON.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0.4
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "name": competitor,
                "tagline": "Industry leader",
                "value_proposition": "Quality solutions",
                "key_messages": ["Reliable", "Trusted"],
                "positioning": "Premium provider",
                "strengths": ["Brand recognition"],
                "weaknesses": ["Generic messaging"]
            }

class PositioningAnalysisTool(BaseTool):
    name: str = "positioning_analysis"
    description: str = "Identifies positioning gaps and opportunities"
    
    def _run(self, business_profile: Dict, competitor_data: List[Dict]) -> Dict:
        """Analyze positioning opportunities"""
        analysis_prompt = f"""
        As a positioning strategist, analyze this business against competitors to find unique positioning opportunities.
        
        Business Profile: {json.dumps(business_profile, indent=2)}
        
        Competitor Analysis: {json.dumps(competitor_data, indent=2)}
        
        Identify:
        1. Market gaps competitors are missing
        2. Unique angles this business could own
        3. Underserved audience segments
        4. Messaging opportunities
        5. Differentiation strategies
        6. Positioning recommendations
        
        Return strategic insights as structured JSON.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0.5
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "gaps": ["Clear communication"],
                "opportunities": ["Simpler messaging"],
                "recommendations": ["Focus on clarity"]
            }

class MessagingGeneratorTool(BaseTool):
    name: str = "messaging_generator"
    description: str = "Creates comprehensive messaging framework"
    
    def _run(self, business_profile: Dict, positioning_analysis: Dict) -> Dict:
        """Generate complete messaging framework"""
        messaging_prompt = f"""
        As a world-class copywriter and messaging expert, create a comprehensive messaging framework.
        
        Business Profile: {json.dumps(business_profile, indent=2)}
        Positioning Strategy: {json.dumps(positioning_analysis, indent=2)}
        
        Create:
        1. One compelling elevator pitch (30 seconds)
        2. Clear value proposition (1-2 sentences)
        3. Five tagline options (short, memorable)
        4. Three key differentiators (specific, provable)
        5. Tone of voice guidelines (personality, style, words to use/avoid)
        6. Responses to top 3 customer objections
        
        Make everything specific, compelling, and unique to this business.
        Return as structured JSON.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": messaging_prompt}],
            temperature=0.6
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "elevator_pitch": "We help businesses communicate better.",
                "value_proposition": "Clear messaging that converts.",
                "tagline_options": ["Better messaging", "Clear communication"],
                "differentiators": ["Fast", "Easy", "Effective"],
                "tone_guidelines": {"style": "Professional", "personality": "Helpful"},
                "objection_responses": []
            }

class ContentCreatorTool(BaseTool):
    name: str = "content_creator"
    description: str = "Generates marketing content assets"
    
    def _run(self, messaging_framework: Dict, business_profile: Dict) -> Dict:
        """Create ready-to-use marketing content"""
        content_prompt = f"""
        As a marketing content specialist, create diverse marketing assets using this messaging framework.
        
        Messaging Framework: {json.dumps(messaging_framework, indent=2)}
        Business Context: {json.dumps(business_profile, indent=2)}
        
        Generate:
        1. 5 website headline options
        2. 3 LinkedIn post templates
        3. 2 email template subject lines and openings
        4. 5 sales one-liners for different situations
        5. 3 ad copy variations (different angles)
        
        Make content actionable, specific, and ready to use.
        Return as structured JSON.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": content_prompt}],
            temperature=0.7
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "website_headlines": ["Transform Your Business"],
                "linkedin_posts": ["Here's what we learned..."],
                "email_templates": ["Quick question about your goals"],
                "sales_one_liners": ["We help companies grow"],
                "ad_copy_variations": ["Stop wasting time"]
            }

class QualityReviewerTool(BaseTool):
    name: str = "quality_reviewer"
    description: str = "Reviews and refines all messaging outputs"
    
    def _run(self, all_outputs: Dict) -> Dict:
        """Quality check and refinement"""
        review_prompt = f"""
        As a brand consistency expert, review all messaging outputs for quality, coherence, and effectiveness.
        
        All Outputs: {json.dumps(all_outputs, indent=2)}
        
        Check for:
        1. Message consistency across all assets
        2. Brand voice alignment
        3. Clarity and compelling nature
        4. Actionability of content
        5. Professional quality
        
        Provide:
        1. Quality score (1-10)
        2. Improvement suggestions
        3. Refined versions of weak elements
        4. Final approval status
        
        Return as structured JSON with recommendations.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": review_prompt}],
            temperature=0.3
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "quality_score": 8,
                "improvements": ["More specific examples"],
                "approval_status": "Approved with minor revisions"
            }

# Main Agent System
class MessagingAgentSystem:
    def __init__(self):
        self.setup_agents()
        
    def setup_agents(self):
        """Initialize all 6 agents with their tools"""
        
        # Agent 1: Discovery Agent
        self.discovery_agent = Agent(
            role="Business Discovery Specialist",
            goal="Extract comprehensive business insights through intelligent analysis",
            backstory="You are an expert business consultant who quickly identifies what makes companies unique and valuable.",
            tools=[BusinessDiscoveryTool()],
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 2: Research Agent
        self.research_agent = Agent(
            role="Competitive Intelligence Analyst",
            goal="Analyze competitor messaging and identify market positioning opportunities",
            backstory="You are a competitive intelligence expert who uncovers market gaps and positioning opportunities.",
            tools=[CompetitorResearchTool()],
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 3: Analysis Agent
        self.analysis_agent = Agent(
            role="Strategic Positioning Expert",
            goal="Identify unique positioning angles and differentiation strategies",
            backstory="You are a positioning strategist who finds untapped market opportunities and unique angles.",
            tools=[PositioningAnalysisTool()],
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 4: Messaging Agent
        self.messaging_agent = Agent(
            role="Brand Messaging Creator",
            goal="Develop compelling messaging frameworks that convert",
            backstory="You are a world-class copywriter who creates messaging that attracts, convinces, and converts.",
            tools=[MessagingGeneratorTool()],
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 5: Content Agent
        self.content_agent = Agent(
            role="Marketing Content Specialist",
            goal="Create ready-to-use marketing assets and content",
            backstory="You are a marketing content expert who translates strategy into actionable marketing materials.",
            tools=[ContentCreatorTool()],
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 6: Quality Agent
        self.quality_agent = Agent(
            role="Brand Consistency Reviewer",
            goal="Ensure all outputs meet professional quality standards",
            backstory="You are a brand expert who ensures consistency, quality, and effectiveness across all messaging.",
            tools=[QualityReviewerTool()],
            verbose=True,
            allow_delegation=False
        )

    async def generate_messaging_playbook(self, business_input: str) -> Dict:
        """Main workflow orchestration"""
        try:
            logging.info("Starting messaging playbook generation...")
            
            # Task 1: Business Discovery
            discovery_task = Task(
                description=f"Analyze this business and extract comprehensive insights: {business_input}",
                agent=self.discovery_agent,
                expected_output="Detailed business profile with target audience, pain points, and competitive landscape"
            )
            
            # Task 2: Competitor Research
            research_task = Task(
                description="Research competitor messaging and positioning strategies based on the discovered business profile",
                agent=self.research_agent,
                expected_output="Comprehensive competitor analysis with messaging patterns and gaps"
            )
            
            # Task 3: Positioning Analysis
            analysis_task = Task(
                description="Analyze positioning opportunities and develop differentiation strategy",
                agent=self.analysis_agent,
                expected_output="Strategic positioning recommendations with unique angles and market opportunities"
            )
            
            # Task 4: Messaging Creation
            messaging_task = Task(
                description="Create comprehensive messaging framework with value propositions, taglines, and guidelines",
                agent=self.messaging_agent,
                expected_output="Complete messaging framework ready for implementation"
            )
            
            # Task 5: Content Generation
            content_task = Task(
                description="Generate ready-to-use marketing content and assets",
                agent=self.content_agent,
                expected_output="Marketing content library with headlines, posts, emails, and sales materials"
            )
            
            # Task 6: Quality Review
            quality_task = Task(
                description="Review all outputs for quality, consistency, and effectiveness",
                agent=self.quality_agent,
                expected_output="Quality assessment with final recommendations and approval"
            )
            
            # Create crew and execute
            crew = Crew(
                agents=[
                    self.discovery_agent,
                    self.research_agent, 
                    self.analysis_agent,
                    self.messaging_agent,
                    self.content_agent,
                    self.quality_agent
                ],
                tasks=[
                    discovery_task,
                    research_task,
                    analysis_task,
                    messaging_task,
                    content_task,
                    quality_task
                ],
                process=Process.sequential,
                verbose=True
            )
            
            # Execute the workflow
            result = crew.kickoff()
            
            # Structure the final output
            final_output = {
                "timestamp": datetime.now().isoformat(),
                "business_input": business_input,
                "results": result,
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

# Usage Example
async def main():
    """Example usage of the complete system"""
    agent_system = MessagingAgentSystem()
    
    business_input = """
    We're a B2B SaaS company that helps marketing teams automate their email campaigns. 
    Our platform integrates with CRM systems and uses AI to personalize email content. 
    We're targeting mid-size companies (50-500 employees) with dedicated marketing teams.
    """
    
    result = await agent_system.generate_messaging_playbook(business_input)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())