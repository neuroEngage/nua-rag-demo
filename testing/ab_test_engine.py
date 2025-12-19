class ABTestEngine:
    async def get_active_test(self, user_id):
        return None
        
    async def assign_variant(self, test_id, user_id):
        return "control"
        
    async def track_outcome(self, test_id, user_id, outcome_metric, value):
        pass
        
    async def create_test(self, config):
        return {"id": "test-id-123"}
        
    async def get_active_tests(self):
        return []
        
    async def calculate_results(self, test_id):
        return {}
