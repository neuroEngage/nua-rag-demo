from datetime import datetime
import json
import logging
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from database.pinecone_db import VectorDBWrapper

logger = logging.getLogger(__name__)

class ProductAgent:
    """
    Handles product recommendations and specifications
    Refined with real RAG logic
    """
    
    def __init__(self):
        self.vector_db = VectorDBWrapper()
        self.llm = ChatOpenAI(temperature=0.5, model="gpt-4-turbo")
    
    async def initialize(self):
        await self.vector_db.initialize()
        
    async def handle(self, query: str, context: dict) -> str:
        """
        Retrieve relevant products and generate recommendation
        """
        # 1. Search vector DB for product matches
        # Filter could be extracted from context or query classification
        relevant_products = await self.vector_db.search(
            query=query,
            namespace="products",
            top_k=3
        )
        
        # 2. Format context for LLM
        products_context = "\n\n".join([
            f"Product: {p.metadata.get('name', 'Nua Product')}\nDetails: {p.page_content}" 
            for p in relevant_products
        ])
        
        # 3. Generate response
        prompt = f"""
        You are Nua's Product Specialist. Recommend products based STRICTLY on the context below.
        
        CUSTOMER QUERY: "{query}"
        
        AVAILABLE PRODUCTS CONTEXT:
        {products_context}
        
        GUIDELINES:
        - Be helpful and specific.
        - Mention specific product features (e.g., "wider back", "rash-free").
        - If the user has a specific concern (like leakage or pain), explain WHY the product helps.
        - Keep the tone warm and professional.
        """
        
        response = await self.llm.apredict_messages([
            SystemMessage(content="You are a helpful product expert for Nua Woman."),
            HumanMessage(content=prompt)
        ])
        
        return response.content
