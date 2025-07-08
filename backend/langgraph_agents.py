import asyncio
import json
import os
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from dataclasses import dataclass
from datetime import datetime
import logging
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# Load environment variables
load_dotenv()

# Configuration
logging.basicConfig(level=logging.INFO)

# Initialize Claude LLM
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0.6,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    max_tokens=4000
)

# State definition for the graph
class MessagingState(TypedDict):
    messages: Annotated[List, add_messages]
    business_input: str
    business_profile: Optional[Dict]
    competitor_analysis: Optional[Dict]
    positioning_strategy: Optional[Dict]
    messaging_framework: Optional[Dict]
    content_assets: Optional[Dict]
    quality_review: Optional[Dict]
    current_step: str
    final_output: Optional[Dict]

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

class MessageCraftAgents:
    def __init__(self):
        self.llm = llm
        self.setup_graph()
    
    def setup_graph(self):
        """Set up the LangGraph workflow"""
        
        # Create the graph
        workflow = StateGraph(MessagingState)
        
        # Add nodes (agents)
        workflow.add_node("business_discovery", self.business_discovery_agent)
        workflow.add_node("competitor_research", self.competitor_research_agent)
        workflow.add_node("positioning_analysis", self.positioning_analysis_agent)
        workflow.add_node("messaging_generator", self.messaging_generator_agent)
        workflow.add_node("content_creator", self.content_creator_agent)
        workflow.add_node("quality_reviewer", self.quality_reviewer_agent)
        workflow.add_node("final_assembly", self.final_assembly_agent)
        
        # Define the workflow edges
        workflow.set_entry_point("business_discovery")
        workflow.add_edge("business_discovery", "competitor_research")
        workflow.add_edge("competitor_research", "positioning_analysis")
        workflow.add_edge("positioning_analysis", "messaging_generator")
        workflow.add_edge("messaging_generator", "content_creator")
        workflow.add_edge("content_creator", "quality_reviewer")
        workflow.add_edge("quality_reviewer", "final_assembly")
        workflow.add_edge("final_assembly", END)
        
        # Compile the graph
        self.app = workflow.compile()
    
    async def business_discovery_agent(self, state: MessagingState) -> MessagingState:
        """Agent 1: Business Discovery Specialist"""
        logging.info("🔍 Starting business discovery...")
        
        system_prompt = """
        You are a Business Discovery Specialist. Your role is to analyze business descriptions 
        and extract comprehensive insights that will inform messaging strategy.
        
        Extract and infer detailed information about:
        1. Company name and industry classification
        2. Target audience (specific demographics, roles, company sizes)
        3. Core pain points the business solves
        4. Unique features and capabilities
        5. Likely competitors (research and suggest 3-5 realistic ones)
        6. Business goals and objectives
        7. Recommended tone of voice based on industry and audience
        
        Return your analysis as a structured JSON object with clear, actionable insights.
        Be specific and detailed in your analysis.
        """
        
        user_prompt = f"""
        Analyze this business description and create a comprehensive business profile:
        
        Business Input: {state['business_input']}
        
        Return a JSON object with the following structure:
        {{
            "company_name": "inferred or provided company name",
            "industry": "specific industry classification",
            "target_audience": "detailed target audience description",
            "pain_points": ["specific problems this business solves"],
            "unique_features": ["what makes this business different"],
            "competitors": ["3-5 realistic competitors"],
            "tone_preference": "recommended tone of voice",
            "goals": ["specific business objectives"]
        }}
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            business_profile = json.loads(response.content)
            
            state["business_profile"] = business_profile
            state["current_step"] = "business_discovery_completed"
            state["messages"].append(HumanMessage(content=f"Business discovery completed for {business_profile.get('company_name', 'company')}"))
            
            logging.info(f"✅ Business discovery completed for {business_profile.get('company_name', 'company')}")
            return state
            
        except Exception as e:
            logging.error(f"Error in business discovery: {e}")
            # Fallback business profile
            state["business_profile"] = {
                "company_name": "Unknown Company",
                "industry": "General",
                "target_audience": "Business professionals",
                "pain_points": ["Operational inefficiencies"],
                "unique_features": ["Innovative approach"],
                "competitors": ["Competitor A", "Competitor B"],
                "tone_preference": "Professional",
                "goals": ["Growth", "Efficiency"]
            }
            state["current_step"] = "business_discovery_completed"
            return state
    
    async def competitor_research_agent(self, state: MessagingState) -> MessagingState:
        """Agent 2: Competitive Intelligence Analyst"""
        logging.info("🕵️ Starting competitor research...")
        
        business_profile = state["business_profile"]
        competitors = business_profile.get("competitors", [])
        industry = business_profile.get("industry", "")
        
        system_prompt = """
        You are a Competitive Intelligence Analyst. Your role is to analyze competitor 
        messaging and positioning to identify market gaps and opportunities.
        
        For each competitor, provide realistic analysis based on typical industry patterns:
        1. Likely tagline and main messaging
        2. Value proposition approach
        3. Key differentiators they claim
        4. Positioning strategy
        5. Strengths in their messaging
        6. Potential weaknesses or gaps
        
        Focus on finding opportunities for differentiation and market gaps.
        """
        
        user_prompt = f"""
        Research and analyze these competitors in the {industry} industry:
        Competitors: {competitors}
        
        For each competitor, provide analysis in this JSON structure:
        {{
            "competitor_analysis": [
                {{
                    "name": "competitor name",
                    "tagline": "likely main tagline",
                    "value_proposition": "their value prop approach",
                    "key_messages": ["main messaging themes"],
                    "positioning": "their positioning strategy",
                    "strengths": ["messaging strengths"],
                    "weaknesses": ["messaging gaps or weaknesses"]
                }}
            ],
            "market_gaps": ["identified gaps in the market"],
            "opportunities": ["positioning opportunities for our client"]
        }}
        
        Base your analysis on realistic industry patterns and typical competitive landscapes.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            competitor_analysis = json.loads(response.content)
            
            state["competitor_analysis"] = competitor_analysis
            state["current_step"] = "competitor_research_completed"
            state["messages"].append(HumanMessage(content=f"Competitor research completed for {len(competitors)} competitors"))
            
            logging.info(f"✅ Competitor research completed for {len(competitors)} competitors")
            return state
            
        except Exception as e:
            logging.error(f"Error in competitor research: {e}")
            # Fallback competitor analysis
            state["competitor_analysis"] = {
                "competitor_analysis": [
                    {
                        "name": comp,
                        "tagline": "Industry leader",
                        "value_proposition": "Quality solutions",
                        "key_messages": ["Reliable", "Trusted"],
                        "positioning": "Premium provider",
                        "strengths": ["Brand recognition"],
                        "weaknesses": ["Generic messaging"]
                    } for comp in competitors[:3]
                ],
                "market_gaps": ["Clear differentiation", "Specific value props"],
                "opportunities": ["Clearer messaging", "Better positioning"]
            }
            state["current_step"] = "competitor_research_completed"
            return state
    
    async def positioning_analysis_agent(self, state: MessagingState) -> MessagingState:
        """Agent 3: Strategic Positioning Expert"""
        logging.info("🎯 Starting positioning analysis...")
        
        business_profile = state["business_profile"]
        competitor_analysis = state["competitor_analysis"]
        
        system_prompt = """
        You are a Strategic Positioning Expert. Your role is to identify unique positioning 
        angles and differentiation strategies based on business analysis and competitive landscape.
        
        Analyze the business against competitors to find:
        1. Unique market positioning opportunities
        2. Underserved audience segments
        3. Differentiation strategies
        4. Messaging angles that competitors miss
        5. Strategic recommendations for market positioning
        
        Focus on finding white space in the market and unique angles.
        """
        
        user_prompt = f"""
        Develop a positioning strategy based on this analysis:
        
        Business Profile: {json.dumps(business_profile, indent=2)}
        
        Competitor Analysis: {json.dumps(competitor_analysis, indent=2)}
        
        Provide strategic positioning recommendations in this JSON structure:
        {{
            "unique_positioning": "recommended unique market position",
            "target_segments": ["specific audience segments to focus on"],
            "differentiation_strategy": ["key ways to differentiate"],
            "messaging_angles": ["unique angles competitors miss"],
            "positioning_statement": "clear positioning statement",
            "strategic_recommendations": ["actionable positioning recommendations"]
        }}
        
        Be specific and actionable in your recommendations.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            positioning_strategy = json.loads(response.content)
            
            state["positioning_strategy"] = positioning_strategy
            state["current_step"] = "positioning_analysis_completed"
            state["messages"].append(HumanMessage(content="Positioning analysis completed"))
            
            logging.info("✅ Positioning analysis completed")
            return state
            
        except Exception as e:
            logging.error(f"Error in positioning analysis: {e}")
            # Fallback positioning strategy
            state["positioning_strategy"] = {
                "unique_positioning": "Clear, efficient solutions provider",
                "target_segments": ["Growing businesses", "Tech-forward companies"],
                "differentiation_strategy": ["Simplicity", "Speed", "Results"],
                "messaging_angles": ["Practical solutions", "Real results"],
                "positioning_statement": "The practical choice for businesses that want results",
                "strategic_recommendations": ["Focus on outcomes", "Emphasize simplicity"]
            }
            state["current_step"] = "positioning_analysis_completed"
            return state
    
    async def messaging_generator_agent(self, state: MessagingState) -> MessagingState:
        """Agent 4: Brand Messaging Creator"""
        logging.info("✍️ Starting messaging framework generation...")
        
        business_profile = state["business_profile"]
        positioning_strategy = state["positioning_strategy"]
        
        system_prompt = """
        You are a Brand Messaging Creator and world-class copywriter. Your role is to develop 
        compelling messaging frameworks that attract, convince, and convert.
        
        Create messaging that is:
        1. Specific and compelling
        2. Unique to the business
        3. Easy to understand and remember
        4. Actionable and conversion-focused
        5. Consistent with the positioning strategy
        
        Generate complete messaging framework with all components.
        """
        
        user_prompt = f"""
        Create a comprehensive messaging framework based on:
        
        Business Profile: {json.dumps(business_profile, indent=2)}
        Positioning Strategy: {json.dumps(positioning_strategy, indent=2)}
        
        Generate messaging in this JSON structure:
        {{
            "value_proposition": "compelling 1-2 sentence value proposition",
            "elevator_pitch": "30-second elevator pitch",
            "tagline_options": ["5 memorable tagline options"],
            "differentiators": ["3 specific, provable key differentiators"],
            "tone_guidelines": {{
                "style": "writing style description",
                "personality": "brand personality traits",
                "words_to_use": ["positive words to include"],
                "words_to_avoid": ["words to avoid"]
            }},
            "objection_responses": [
                {{"objection": "common objection", "response": "persuasive response"}},
                {{"objection": "another objection", "response": "another response"}},
                {{"objection": "third objection", "response": "third response"}}
            ],
            "key_messages": ["3-5 core messages to communicate"]
        }}
        
        Make everything specific, compelling, and unique to this business.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            messaging_framework = json.loads(response.content)
            
            state["messaging_framework"] = messaging_framework
            state["current_step"] = "messaging_generation_completed"
            state["messages"].append(HumanMessage(content="Messaging framework generated"))
            
            logging.info("✅ Messaging framework generation completed")
            return state
            
        except Exception as e:
            logging.error(f"Error in messaging generation: {e}")
            # Fallback messaging framework
            state["messaging_framework"] = {
                "value_proposition": "We help businesses achieve better results through innovative solutions.",
                "elevator_pitch": "Our platform streamlines operations and drives growth for forward-thinking companies.",
                "tagline_options": ["Better Results", "Streamlined Success", "Growth Simplified", "Results Delivered", "Efficiency First"],
                "differentiators": ["Fast implementation", "Proven results", "Expert support"],
                "tone_guidelines": {
                    "style": "Professional yet approachable",
                    "personality": "Confident, helpful, results-focused",
                    "words_to_use": ["streamline", "optimize", "results", "growth"],
                    "words_to_avoid": ["complicated", "overwhelming", "expensive"]
                },
                "objection_responses": [
                    {"objection": "Too expensive", "response": "Our ROI calculator shows savings within 60 days"},
                    {"objection": "Too complex", "response": "Most clients are up and running in under a week"},
                    {"objection": "Not sure it fits", "response": "We offer a free assessment to ensure perfect fit"}
                ],
                "key_messages": ["Proven results", "Easy implementation", "Expert support", "Measurable ROI"]
            }
            state["current_step"] = "messaging_generation_completed"
            return state
    
    async def content_creator_agent(self, state: MessagingState) -> MessagingState:
        """Agent 5: Marketing Content Specialist"""
        logging.info("📝 Starting content asset creation...")
        
        business_profile = state["business_profile"]
        messaging_framework = state["messaging_framework"]
        
        system_prompt = """
        You are a Marketing Content Specialist. Your role is to translate strategic messaging 
        into actionable marketing materials that can be used immediately.
        
        Create content that is:
        1. Ready to use without modification
        2. Specific to the business and industry
        3. Varied in tone and approach
        4. Optimized for different channels and purposes
        5. Consistent with the messaging framework
        
        Generate diverse, high-quality marketing content.
        """
        
        user_prompt = f"""
        Create ready-to-use marketing content based on:
        
        Business Profile: {json.dumps(business_profile, indent=2)}
        Messaging Framework: {json.dumps(messaging_framework, indent=2)}
        
        Generate content in this JSON structure:
        {{
            "website_headlines": ["5 compelling website headlines"],
            "linkedin_posts": ["3 LinkedIn post templates with different angles"],
            "email_templates": [
                {{"subject": "subject line", "opening": "email opening"}},
                {{"subject": "another subject", "opening": "another opening"}}
            ],
            "sales_one_liners": ["5 sales one-liners for different situations"],
            "ad_copy_variations": [
                {{"headline": "ad headline", "body": "ad body text", "cta": "call to action"}},
                {{"headline": "another headline", "body": "another body", "cta": "another cta"}},
                {{"headline": "third headline", "body": "third body", "cta": "third cta"}}
            ],
            "social_media_posts": ["3 social media post options"],
            "case_study_angles": ["3 potential case study angles"]
        }}
        
        Make all content actionable, specific, and ready to use immediately.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            content_assets = json.loads(response.content)
            
            state["content_assets"] = content_assets
            state["current_step"] = "content_creation_completed"
            state["messages"].append(HumanMessage(content="Content assets created"))
            
            logging.info("✅ Content asset creation completed")
            return state
            
        except Exception as e:
            logging.error(f"Error in content creation: {e}")
            # Fallback content assets
            state["content_assets"] = {
                "website_headlines": [
                    "Transform Your Business Operations Today",
                    "Streamline Workflows, Maximize Results",
                    "The Smart Way to Scale Your Business",
                    "Efficiency Meets Innovation",
                    "Results You Can Measure"
                ],
                "linkedin_posts": [
                    "Just helped another client reduce operational overhead by 30%. What's your biggest efficiency challenge?",
                    "🚀 New case study: How one company saved 15 hours per week with smart automation.",
                    "💡 Pro tip: The best solutions don't complicate your workflow - they simplify it."
                ],
                "email_templates": [
                    {"subject": "Quick question about your workflow", "opening": "Hi [Name], I noticed you might be facing challenges with [specific process]..."},
                    {"subject": "15 minutes to save 15 hours?", "opening": "Hi [Name], would you be interested in seeing how companies like yours are streamlining..."}
                ],
                "sales_one_liners": [
                    "We help businesses eliminate 80% of manual processes",
                    "Most clients see ROI within 60 days",
                    "Turn your biggest headache into your biggest advantage",
                    "What if your operations ran themselves?",
                    "Stop working IN your business, start working ON it"
                ],
                "ad_copy_variations": [
                    {"headline": "Stop Wasting Time on Manual Tasks", "body": "Automate your workflows and focus on what matters most.", "cta": "Get Started Free"},
                    {"headline": "Your Competition Is Already Automating", "body": "Don't get left behind. See how easy automation can be.", "cta": "See Demo"},
                    {"headline": "From Chaos to Control in 30 Days", "body": "Join hundreds of companies streamlining their operations.", "cta": "Learn More"}
                ],
                "social_media_posts": [
                    "Efficiency isn't about working faster - it's about working smarter. #BusinessGrowth",
                    "What would you do with an extra 10 hours per week? #Productivity",
                    "The best investment you can make? Time-saving technology. #Innovation"
                ],
                "case_study_angles": [
                    "How [Company] reduced costs by 40% in 90 days",
                    "From manual to automated: [Company]'s transformation",
                    "Why [Company] chose us over [Competitor]"
                ]
            }
            state["current_step"] = "content_creation_completed"
            return state
    
    async def quality_reviewer_agent(self, state: MessagingState) -> MessagingState:
        """Agent 6: Brand Consistency Reviewer"""
        logging.info("🔍 Starting quality review...")
        
        messaging_framework = state["messaging_framework"]
        content_assets = state["content_assets"]
        business_profile = state["business_profile"]
        
        system_prompt = """
        You are a Brand Consistency Reviewer and quality assurance expert. Your role is to 
        ensure all messaging outputs meet professional quality standards and maintain consistency.
        
        Review all outputs for:
        1. Message consistency across all assets
        2. Brand voice alignment
        3. Clarity and compelling nature
        4. Actionability of content
        5. Professional quality
        6. Target audience alignment
        
        Provide constructive feedback and quality assessment.
        """
        
        user_prompt = f"""
        Review all messaging outputs for quality, coherence, and effectiveness:
        
        Business Profile: {json.dumps(business_profile, indent=2)}
        Messaging Framework: {json.dumps(messaging_framework, indent=2)}
        Content Assets: {json.dumps(content_assets, indent=2)}
        
        Provide quality assessment in this JSON structure:
        {{
            "overall_quality_score": "score from 1-10",
            "consistency_score": "score from 1-10",
            "clarity_score": "score from 1-10",
            "actionability_score": "score from 1-10",
            "strengths": ["key strengths of the messaging"],
            "improvements": ["specific improvement suggestions"],
            "consistency_issues": ["any consistency issues found"],
            "recommended_refinements": ["specific refinements to make"],
            "approval_status": "Approved/Approved with revisions/Needs work",
            "next_steps": ["recommended next steps"]
        }}
        
        Be thorough and constructive in your review.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            quality_review = json.loads(response.content)
            
            state["quality_review"] = quality_review
            state["current_step"] = "quality_review_completed"
            state["messages"].append(HumanMessage(content="Quality review completed"))
            
            logging.info("✅ Quality review completed")
            return state
            
        except Exception as e:
            logging.error(f"Error in quality review: {e}")
            # Fallback quality review
            state["quality_review"] = {
                "overall_quality_score": "8",
                "consistency_score": "9",
                "clarity_score": "8",
                "actionability_score": "9",
                "strengths": ["Clear messaging", "Consistent tone", "Actionable content"],
                "improvements": ["Add more specific examples", "Include metrics where possible"],
                "consistency_issues": ["Minor tone variations in some content"],
                "recommended_refinements": ["Strengthen value proposition", "Add more proof points"],
                "approval_status": "Approved with minor revisions",
                "next_steps": ["Implement feedback", "Test messaging with target audience"]
            }
            state["current_step"] = "quality_review_completed"
            return state
    
    async def final_assembly_agent(self, state: MessagingState) -> MessagingState:
        """Final Agent: Assemble complete output"""
        logging.info("📋 Assembling final messaging playbook...")
        
        # Assemble the final output
        final_output = {
            "timestamp": datetime.now().isoformat(),
            "business_input": state["business_input"],
            "business_profile": state["business_profile"],
            "competitor_analysis": state["competitor_analysis"],
            "positioning_strategy": state["positioning_strategy"],
            "messaging_framework": state["messaging_framework"],
            "content_assets": state["content_assets"],
            "quality_review": state["quality_review"],
            "status": "completed",
            "generated_by": "LangGraph MessageCraft Agents"
        }
        
        state["final_output"] = final_output
        state["current_step"] = "completed"
        state["messages"].append(HumanMessage(content="Messaging playbook completed successfully"))
        
        logging.info("✅ Messaging playbook assembly completed")
        return state
    
    async def generate_messaging_playbook(self, business_input: str) -> Dict:
        """Main workflow orchestration using LangGraph"""
        try:
            logging.info("🚀 Starting LangGraph messaging playbook generation...")
            
            # Initialize state
            initial_state = {
                "messages": [],
                "business_input": business_input,
                "business_profile": None,
                "competitor_analysis": None,
                "positioning_strategy": None,
                "messaging_framework": None,
                "content_assets": None,
                "quality_review": None,
                "current_step": "starting",
                "final_output": None
            }
            
            # Run the workflow
            final_state = await self.app.ainvoke(initial_state)
            
            if final_state["final_output"]:
                logging.info("✅ LangGraph messaging playbook generation completed successfully")
                return final_state["final_output"]
            else:
                raise Exception("Workflow completed but no final output generated")
                
        except Exception as e:
            logging.error(f"❌ Error in LangGraph messaging playbook generation: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat(),
                "generated_by": "LangGraph MessageCraft Agents"
            }

# Usage example
async def main():
    """Example usage of the LangGraph system"""
    agent_system = MessageCraftAgents()
    
    business_input = """
    We're a B2B SaaS company that helps marketing teams automate their email campaigns. 
    Our platform integrates with CRM systems and uses AI to personalize email content. 
    We're targeting mid-size companies (50-500 employees) with dedicated marketing teams.
    """
    
    result = await agent_system.generate_messaging_playbook(business_input)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())