from fastapi import FastAPI, HTTPException, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import asyncio
import logging
import uuid
from datetime import datetime
import json

# Import custom modules
from agents.orchestrator import NuaOrchestrator
from analytics.engine import NuaAnalyticsEngine
from testing.ab_test_engine import ABTestEngine
from database.postgres_db import PostgresDB
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# ============================================
# LIFESPAN MANAGEMENT
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Nua RAG Backend...")
    app.state.orchestrator = NuaOrchestrator()
    app.state.analytics_engine = NuaAnalyticsEngine()
    app.state.ab_test_engine = ABTestEngine()
    app.state.db = PostgresDB()
    
    # Initialize vector DB
    await app.state.orchestrator.initialize()
    
    yield
    
    # Shutdown
    logger.info("Shutting down gracefully...")
    await app.state.db.close()

app = FastAPI(
    title="Nua AI Assistant API",
    description="Multi-agent RAG system for women's health",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://nuawoman.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# PYDANTIC MODELS
# ============================================

class ChatMessage(BaseModel):
    user_id: str
    message: str
    session_id: str
    metadata: dict = {}

class AnalyticsRequest(BaseModel):
    time_period: str = "weekly"

class ABTestConfig(BaseModel):
    name: str
    description: str
    control_template: str
    treatment_template: str
    sample_size: int = 1000

class FeedbackMessage(BaseModel):
    interaction_id: str
    rating: int  # 1-5
    feedback_text: str = ""

# ============================================
# CHAT ENDPOINTS
# ============================================

@app.post("/api/v1/chat")
async def handle_chat(message: ChatMessage):
    """
    Main chat endpoint with full RAG pipeline
    """
    try:
        logger.info(f"Chat received from user {message.user_id}")
        
        # Get user context
        user_context = await get_user_context(message.user_id, app.state.db)
        
        # Check active A/B test
        ab_test = await app.state.ab_test_engine.get_active_test(message.user_id)
        if ab_test:
            variant = await app.state.ab_test_engine.assign_variant(
                ab_test["id"], 
                message.user_id
            )
            user_context["ab_variant"] = variant
        else:
            user_context["ab_variant"] = None
        
        # Process through orchestrator
        result = await app.state.orchestrator.process_query(
            message.message, 
            user_context
        )
        
        # Log to database
        interaction_id = str(uuid.uuid4())
        await app.state.db.log_interaction({
            "interaction_id": interaction_id,
            "user_id": message.user_id,
            "session_id": message.session_id,
            "query": message.message,
            "response": result["response"],
            "classification": result["classification"],
            "ab_variant": user_context.get("ab_variant"),
            "timestamp": datetime.now()
        })
        
        # Extract and log insights
        insights = await app.state.analytics_engine.extract_insights(
            user_id=message.user_id,
            query=message.message,
            response=result["response"],
            classification=result["classification"]
        )
        
        # Track A/B test outcome if applicable
        if ab_test:
            await app.state.ab_test_engine.track_outcome(
                test_id=ab_test["id"],
                user_id=message.user_id,
                outcome_metric="response_generated",
                value=1
            )
        
        return {
            "success": True,
            "interaction_id": interaction_id,
            "response": result["response"],
            "timestamp": datetime.now().isoformat(),
            "ab_variant": user_context.get("ab_variant"),
            "insights_tracked": True
        }
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: str):
    """
    WebSocket for streaming responses
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())
    
    try:
        while True:
            data = await websocket.receive_text()
            
            user_context = await get_user_context(user_id, app.state.db)
            result = await app.state.orchestrator.process_query(data, user_context)
            
            # Stream response
            for chunk in result["response"].split():
                await websocket.send_text(chunk + " ")
                await asyncio.sleep(0.05)
            
            await websocket.send_text("\n[END]")
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1000)

@app.post("/api/v1/feedback")
async def submit_feedback(feedback: FeedbackMessage):
    """
    Log user feedback on responses
    """
    try:
        await app.state.db.log_feedback({
            "interaction_id": feedback.interaction_id,
            "rating": feedback.rating,
            "feedback_text": feedback.feedback_text,
            "timestamp": datetime.now()
        })
        
        return {
            "success": True,
            "message": "Feedback recorded, thank you!"
        }
    
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ANALYTICS ENDPOINTS
# ============================================

@app.get("/api/v1/analytics/insights")
async def get_insights(period: str = "weekly"):
    """
    Get comprehensive business intelligence
    """
    try:
        insights = await app.state.analytics_engine.generate_insights(
            time_period=period
        )
        
        return {
            "period": period,
            "generated_at": datetime.now().isoformat(),
            "insights": insights
        }
    
    except Exception as e:
        logger.error(f"Insights error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/concerns")
async def get_top_concerns(limit: int = 10, period: str = "weekly"):
    """
    Top customer concerns by frequency and emotion
    """
    try:
        concerns = await app.state.analytics_engine.get_top_concerns(
            period=period,
            limit=limit
        )
        return {"concerns": concerns}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/ad-copy")
async def get_ad_copy():
    """
    Suggested ad copy from real customer language
    """
    try:
        suggestions = await app.state.analytics_engine.generate_ad_copy()
        return {"suggestions": suggestions}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/faq-gaps")
async def get_faq_gaps():
    """
    Identify FAQ gaps
    """
    try:
        gaps = await app.state.analytics_engine.identify_faq_gaps()
        return {"gaps": gaps}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/funnel")
async def get_funnel_analysis():
    """
    Customer journey funnel analysis
    """
    try:
        analysis = await app.state.analytics_engine.analyze_funnel()
        return {"funnel": analysis}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/sentiment-trends")
async def get_sentiment_trends(days: int = 7):
    """
    Sentiment trends over time
    """
    try:
        trends = await app.state.analytics_engine.get_sentiment_trends(days=days)
        return {"trends": trends}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/customer-segments")
async def get_customer_segments():
    """
    Segmentation of customers
    """
    try:
        segments = await app.state.analytics_engine.segment_customers()
        return {"segments": segments}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# A/B TESTING ENDPOINTS
# ============================================

@app.post("/api/v1/testing/create")
async def create_ab_test(config: ABTestConfig):
    """
    Create new A/B test for response variants
    """
    try:
        test = await app.state.ab_test_engine.create_test(config.dict())
        logger.info(f"Created test: {test['id']}")
        
        return {
            "success": True,
            "test_id": test["id"],
            "status": "created"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/testing/active")
async def get_active_tests():
    """
    List all active A/B tests
    """
    try:
        tests = await app.state.ab_test_engine.get_active_tests()
        return {"tests": tests}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/testing/results/{test_id}")
async def get_test_results(test_id: str):
    """
    Get statistical results for A/B test
    """
    try:
        results = await app.state.ab_test_engine.calculate_results(test_id)
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ADMIN ENDPOINTS
# ============================================

@app.get("/api/v1/admin/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "orchestrator": "ready",
            "analytics": "ready",
            "database": "ready"
        }
    }

@app.get("/api/v1/admin/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        stats = await app.state.db.get_system_stats()
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_user_context(user_id: str, db: PostgresDB):
    """Get user context from database"""
    return {
        "user_id": user_id,
        "previous_interactions": await db.get_user_history(user_id, limit=5),
        "user_segment": await db.get_user_segment(user_id),
        "conversation_stage": await db.get_conversation_stage(user_id)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
