from datetime import datetime

class InsightExtractorAgent:
    """
    Extracts business intelligence from conversations
    """
    
    async def initialize(self):
        pass

    async def extract(self, user_query, response, classification, user_context):
        """
        Extract and log insights from interaction
        """
        insights = {
            "query_type": classification.get("intent", "unknown"),
            "emotional_trigger": await self._detect_emotion(user_query),
            "language_pattern": user_query,
            "timestamp": datetime.now()
        }
        
        return insights
    
    async def _detect_emotion(self, query):
        """Detect emotional state from query"""
        emotions = {
            "anxious": ["worried", "scared", "concerned", "afraid"],
            "embarrassed": ["awkward", "shy", "uncomfortable", "private"],
            "curious": ["wondering", "what is", "how does", "explain"],
            "confident": ["best", "recommend", "should i", "can i"],
            "frustrated": ["doesn't work", "hate", "problem", "issue"]
        }
        
        detected = {}
        for emotion, keywords in emotions.items():
            if any(kw in query.lower() for kw in keywords):
                detected[emotion] = True
        
        return detected
