from datetime import datetime
import logging
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from database.pinecone_db import VectorDBWrapper

logger = logging.getLogger(__name__)

class ReassuranceAgent:
    """
    Handles emotional support and reassurance queries.
    Focuses on tone, validation, and community connection.
    """
    
    def __init__(self):
        self.vector_db = VectorDBWrapper()
        self.llm = ChatOpenAI(temperature=0.8, model="gpt-4-turbo") # Higher temp for empathy
    
    async def initialize(self):
        # Even reassurance might fetch "community stories" from DB
        await self.vector_db.initialize()
        
    async def handle(self, query: str, context: dict) -> str:
        """
        Provide a compassionate, validating response
        """
        # 1. Search for similar community stories/feelings
        related_stories = await self.vector_db.search(
            query=query,
            namespace="reassurance",
            top_k=2
        )
        
        stories_context = "\n".join([doc.page_content for doc in related_stories])
        
        # 2. Generate Empathetic Response
        prompt = f"""
        You are Nua's 'Big Sister' agent. The user is expressing a concern or emotion.
        Your goal is to validate their feelings and make them feel heard and safe.
        
        USER EXPRESSION: "{query}"
        
        COMMUNITY CONTEXT (Similar feelings):
        {stories_context}
        
        GUIDELINES:
        - START with validation ("I hear you," "It's completely normal to feel...").
        - Use warm, safe language (emojis like 💙 are okay).
        - Connect them to the fact that many women feel this way (using the context).
        - Do not push products unless they solve a direct pain point mentioned.
        - Be comforting, not clinical.
        """
        
        response = await self.llm.apredict_messages([
            SystemMessage(content="You are a compassionate, empathetic friend who listens."),
            HumanMessage(content=prompt)
        ])
        
        return response.content
