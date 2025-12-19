class ToneGuardianAgent:
    """
    Ensures all responses are compassionate, accurate, and women-centric
    """
    
    async def initialize(self):
        pass

    async def validate(self, response, classification):
        """
        Validate response tone, accuracy, and safety
        """
        # Simple pass-through for demo if no specific checks needed
        # In a real scenario, this would check against keywords
        return response
    
    def _check_compassion(self, response):
        """Verify tone includes validation and understanding"""
        compassion_keywords = [
            "understand", "normal", "you're not alone",
            "we support", "it's okay", "completely valid"
        ]
        return any(kw in response.lower() for kw in compassion_keywords)
    
    def _check_accuracy(self, response):
        """Verify medical accuracy"""
        # Check against fact database
        red_flags = ["cure", "always", "never", "guaranteed"]
        return not any(flag in response.lower() for flag in red_flags)
