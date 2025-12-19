import os
import logging
from typing import List, Dict, Any
import json
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.schema import Document
import pinecone

logger = logging.getLogger(__name__)

class VectorDBWrapper:
    """
    Wrapper for Vector Database (Pinecone) with fallback to in-memory mock for demo/testing
    """
    
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.env = os.getenv("PINECONE_ENVIRONMENT", "us-west-1")
        self.index_name = "nua-rag-knowledge"
        self.use_mock = not self.api_key or self.api_key == "your_pinecone_key"
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small") if os.getenv("OPENAI_API_KEY") else None
        self.vectorstore = None

    async def initialize(self):
        """Initialize connection to Pinecone or setup mock"""
        if self.use_mock:
            logger.warning("⚠️ No valid Pinecone API Key found. Using MOCK Vector DB mode.")
            return

        try:
            pinecone.init(api_key=self.api_key, environment=self.env)
            if self.index_name not in pinecone.list_indexes():
                logger.warning(f"Index {self.index_name} does not exist. Please create it.")
                self.use_mock = True
            else:
                self.vectorstore = Pinecone.from_existing_index(
                    index_name=self.index_name,
                    embedding=self.embeddings
                )
                logger.info("✓ Connected to Pinecone Vector DB")
        except Exception as e:
            logger.error(f"Failed to connect to Pinecone: {str(e)}. Falling back to mock.")
            self.use_mock = True

    async def search(self, query: str, namespace: str, top_k: int = 3, metadata_filter: Dict = None) -> List[Document]:
        """
        Search for documents relevant to query
        """
        if self.use_mock:
            return self._mock_search(query, namespace, top_k)
            
        try:
            # Real search
            return self.vectorstore.similarity_search(
                query, 
                k=top_k, 
                namespace=namespace,
                filter=metadata_filter
            )
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return self._mock_search(query, namespace, top_k)

    def _mock_search(self, query: str, namespace: str, top_k: int) -> List[Document]:
        """Return dummy data for demo purposes based on namespace"""
        logger.info(f"Returning MOCK results for query: '{query}' in namespace: '{namespace}'")
        
        mock_data = {
            "products": [
                Document(page_content="Nua Sanitary Pads are designed with a wider back for leak-proof nights. They are super soft and rash-free.", metadata={"name": "Nua Sanitary Pads", "price": "Affordable"}),
                Document(page_content="Nua Cramp Comfort Heat Patches provide up to 8 hours of relief from period pain without any medication.", metadata={"name": "Cramp Comfort Patches", "price": "Premium"}),
                Document(page_content="Nua Intimate Wash is balanced for vaginal pH and contains no harsh chemicals.", metadata={"name": "Intimate Wash", "price": "Standard"})
            ],
            "education": [
                Document(page_content="Period blood color can vary from bright red to dark brown. Brown blood is usually just older blood oxidizing.", metadata={"topic": "Health"}),
                Document(page_content="Irregular periods (PCOS) affect 1 in 5 women. Symptoms include weight gain, acne, and missed periods.", metadata={"topic": "PCOS"}),
                Document(page_content="Menstrual hygiene is crucial. Change pads every 4-6 hours to prevent infection and odor.", metadata={"topic": "Hygiene"})
            ],
            "reassurance": [
                Document(page_content="It is completely normal to feel tired and emotional during your period. Your body is doing hard work.", metadata={"tone": "supportive"}),
                Document(page_content="You are not alone in feeling anxious about leaks. It happens to almost everyone at some point.", metadata={"tone": "validating"})
            ]
        }
        
        # Simple keyword matching for better mock experience
        candidates = mock_data.get(namespace, [])
        results = [doc for doc in candidates if any(word in doc.page_content.lower() for word in query.lower().split())]
        
        return results[:top_k] if results else candidates[:top_k]
