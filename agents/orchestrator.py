import json
import logging
from datetime import datetime
from typing import Dict, Any
import asyncio

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from .product_agent import ProductAgent
from .education_agent import EducationAgent
from .reassurance_agent import ReassuranceAgent
from .tone_guardian import ToneGuardianAgent
from .safety_agent import SafetyAgent
from .insight_extractor import InsightExtractorAgent

logger = logging.getLogger(__name__)

class NuaOrchestrator:
    """
    Primary orchestrator that routes queries to specialized agents
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.7, model="gpt-4-turbo")
        
        self.agents = {
            "product": ProductAgent(),
            "education": EducationAgent(),
            "reassurance": ReassuranceAgent(),
            "tone_guardian": ToneGuardianAgent(),
            "safety": SafetyAgent(),
            "insight_extractor": InsightExtractorAgent()
        }
    
    async def initialize(self):
        """Initialize all agents"""
        for agent_name, agent in self.agents.items():
            await agent.initialize()
            logger.info(f"✓ Initialized {agent_name} agent")
    
    async def process_query(self, user_query: str, user_context: Dict[str, Any]) -> Dict:
        """
        Main processing pipeline
        """
        try:
            # Step 1: Classify query
            classification = await self._classify_query(user_query)
            logger.info(f"Classification: {classification}")
            
            # Step 2: Route to primary agent based on classification
            primary_agent_name = classification["primary_agent"]
            primary_agent = self.agents[primary_agent_name]
            
            primary_response = await primary_agent.handle(user_query, user_context)
            
            # Step 3: Validate with tone guardian
            validated_response = await self.agents["tone_guardian"].validate(
                primary_response,
                classification
            )
            
            # Step 4: Safety check
            safety_check = await self.agents["safety"].validate(
                validated_response,
                user_query
            )
            
            if not safety_check["is_safe"]:
                logger.warning(f"Safety issue detected: {safety_check['reason']}")
                validated_response = safety_check["fallback_response"]
            
            # Step 5: Extract insights
            insights = await self.agents["insight_extractor"].extract(
                user_query=user_query,
                response=validated_response,
                classification=classification,
                user_context=user_context
            )
            
            return {
                "response": validated_response,
                "classification": classification,
                "insights": insights,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Orchestration error: {str(e)}", exc_info=True)
            return {
                "response": "I'm having trouble processing your question right now. Please try again in a moment.",
                "classification": {"error": str(e)},
                "insights": {}
            }
    
    async def _classify_query(self, query: str) -> Dict:
        """
        Classify query using LLM
        """
        classification_prompt = f"""
        Analyze this customer query from a women's health platform (Nua).
        
        Customer Query: "{query}"
        
        Determine:
        1. PRIMARY_AGENT: Choose one - "product" (product recommendation), "education" (health info), "reassurance" (emotional support)
        2. INTENT: "question" | "concern" | "comparison" | "complaint"
        3. EMOTION: "anxious" | "embarrassed" | "curious" | "confident" | "frustrated"
        4. URGENCY: "low" | "medium" | "high"
        5. FUNNEL_STAGE: "awareness" | "consideration" | "purchase" | "retention"
        6. CONCERNS: List specific concerns (e.g., "discomfort", "irritation", "leakage")
        
        Respond as JSON only.
        """
        
        try:
            response = await self.llm.apredict(classification_prompt)
            classification = json.loads(response)
        except:
            # Fallback classification
            classification = {
                "primary_agent": "reassurance",
                "intent": "question",
                "emotion": "curious",
                "urgency": "medium",
                "funnel_stage": "consideration",
                "concerns": []
            }
        
        return classification
