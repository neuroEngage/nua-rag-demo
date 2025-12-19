from datetime import datetime
import logging
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from database.pinecone_db import VectorDBWrapper

logger = logging.getLogger(__name__)

class EducationAgent:
    """
    Handles health education and information queries
    """
    
    def __init__(self):
        self.vector_db = VectorDBWrapper()
        self.llm = ChatOpenAI(temperature=0.3, model="gpt-4-turbo") # Lower temp for factual info
    
    async def initialize(self):
        await self.vector_db.initialize()
        
    async def handle(self, query: str, context: dict) -> str:
        """
        Retrieve educational content and explain clearly
        """
        # 1. Search vector DB for health topics
        relevant_info = await self.vector_db.search(
            query=query,
            namespace="education",
            top_k=2
        )
        
        # 2. Format context
        info_context = "\n\n".join([doc.page_content for doc in relevant_info])
        
        # 3. Generate response
        prompt = f"""
        You are Nua's Health Educator. Answer the customer's question using the scientific context provided.
        
        CUSTOMER QUERY: "{query}"
        
        SCIENTIFIC CONTEXT:
        {info_context}
        
        GUIDELINES:
        - Be factual but accessible (no jargon without explanation).
        - Debunk myths if relevant.
        - Focus on women's health education.
        - Avoid giving medical advice (don't diagnose). 
        - If the context doesn't answer it fully, use general medical knowledge but add a disclaimer.
        """
        
        response = await self.llm.apredict_messages([
            SystemMessage(content="You are a knowledgeable, trustworthy health educator."),
            HumanMessage(content=prompt)
        ])
        
        return response.content
