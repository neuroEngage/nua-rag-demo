NUAT_DATA_SOURCES = {
    "primary": {
        "website": "https://nuawoman.com",
        "pages_to_crawl": [
            "/", "/products", "/about", "/blog",
            "/faq", "/sustainability", "/period-tracker"
        ]
    },
    "secondary": {
        "social_media": ["Instagram", "LinkedIn", "Twitter"],
        "reviews": ["Trustpilot", "IndiaCommerce", "Google Reviews"],
        "press": ["TechCrunch", "YourStory", "Mint"]
    },
    "internal": {
        "product_specs": "Database of product details",
        "customer_feedback": "Support tickets + surveys",
        "campaign_data": "Email, ads, landing pages"
    }
}

CONTENT_CHUNKING_STRATEGY = {
    "approach": "Semantic chunking with overlap",
    "chunk_size": 500,
    "overlap": 100,
    "separators": [".", "\n\n", "\n", " "],
    
    "metadata_extraction": {
        "product_category": ["pads", "wipes", "wash", "patches", "panties"],
        "topic": ["safety", "comfort", "hygiene", "health", "sustainability"],
        "concern": ["discomfort", "irritation", "leakage", "odor", "confidence"],
        "funnel_stage": ["awareness", "consideration", "purchase", "retention"],
        "confidence_score": "1.0"  # 0-1 based on source reliability
    }
}

EMBEDDING_CONFIG = {
    "model": "text-embedding-3-small",  # OpenAI
    "dimension": 1536,
    "batch_size": 100,
    "normalize": True
}

VECTOR_DB_CONFIG = {
    "provider": "Pinecone",
    "index_name": "nua-rag-knowledge",
    "dimension": 1536,
    "metric": "cosine",
    "regions": ["us-west-1"],
    
    "namespaces": {
        "products": "product_recommendations",
        "education": "health_information",
        "reassurance": "emotional_support",
        "faq": "frequently_asked_questions",
        "safety": "safety_guidelines"
    }
}
