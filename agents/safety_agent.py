import logging

class SafetyAgent:
    """
    Prevents medical overreach and ensures safety guidelines
    """
    
    def __init__(self):
        self.medical_disclaimer = "\n\n(Note: I am an AI assistant, not a doctor. Please consult a healthcare professional for specific medical advice.)"
        
    async def initialize(self):
        pass
        
    async def validate(self, response: str, query: str) -> dict:
        """
        Check response for safety violations
        """
        is_safe = True
        reason = None
        fallback_response = response
        
        lower_response = response.lower()
        
        # 1. Check for absolute medical claims
        high_risk_claims = ["guarantee cure", "will cure", "100% effective against infection", "stop taking medication"]
        for claim in high_risk_claims:
            if claim in lower_response:
                is_safe = False
                reason = f"Contains high-risk medical claim: {claim}"
                fallback_response = "I cannot provide medical guarantees. Please consult a doctor for treatment."
                break
        
        # 2. Check for serious symptoms in Query that require immediate doctor attention
        emergency_keywords = ["severe bleeding", "fainted", "unbearable pain", "high fever"]
        if any(kw in query.lower() for kw in emergency_keywords):
            # We don't block the response, but we MUST append a strong warning
            if "doctor" not in lower_response and "healthcare" not in lower_response:
                 fallback_response = response + "\n\n⚠️ Given strictly what you described, please visit a doctor immediately."
        
        # 3. Append disclaimer if it looks sufficiently medical but safe
        medical_topics = ["pcod", "pcos", "infection", "rash", "cramps", "period"]
        if any(topic in lower_response for topic in medical_topics) and "doctor" not in lower_response:
            fallback_response += self.medical_disclaimer
            
        return {
            "is_safe": is_safe,
            "reason": reason,
            "fallback_response": fallback_response
        }
