import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Make asyncpg optional for lightweight demo deployment
try:
    import asyncpg
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False
    logger.warning("⚠️ asyncpg not installed. Running in Mock Mode only.")

class PostgresDB:
    """
    PostgreSQL database connection and operations
    """
    
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.pool = None
    
    async def initialize(self):
        """Create connection pool"""
        if self.db_url and HAS_POSTGRES:
            try:
                self.pool = await asyncpg.create_pool(self.db_url)
                await self._create_tables()
                logger.info("✓ Database initialized")
            except Exception as e:
                logger.error(f"DB Init Failed: {e}. Switching to Mock Mode.")
        else:
            logger.warning("DATABASE_URL not set or driver missing, running in memory-only mode")
    
    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
    
    async def _create_tables(self):
        """Create tables if they don't exist"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id SERIAL PRIMARY KEY,
                interaction_id UUID UNIQUE,
                user_id VARCHAR(255),
                session_id UUID,
                query TEXT,
                response TEXT,
                classification JSONB,
                ab_variant VARCHAR(50),
                feedback_rating INT,
                timestamp TIMESTAMP DEFAULT NOW()
            );
            
            CREATE TABLE IF NOT EXISTS insights (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255),
                query_type VARCHAR(100),
                emotional_trigger JSONB,
                product_interest VARCHAR(100),
                funnel_signal VARCHAR(50),
                timestamp TIMESTAMP DEFAULT NOW()
            );
            
            CREATE TABLE IF NOT EXISTS ab_tests (
                id UUID PRIMARY KEY,
                name VARCHAR(255),
                status VARCHAR(20),
                created_at TIMESTAMP,
                variants JSONB,
                metrics JSONB
            );
            
            CREATE TABLE IF NOT EXISTS test_assignments (
                id SERIAL PRIMARY KEY,
                test_id UUID,
                user_id VARCHAR(255),
                variant VARCHAR(50),
                UNIQUE(test_id, user_id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_interactions_user ON interactions(user_id);
            CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp);
            CREATE INDEX IF NOT EXISTS idx_insights_user ON insights(user_id);
            """)
    
    async def log_interaction(self, data: Dict):
        """Log chat interaction"""
        if not self.pool: return
        async with self.pool.acquire() as conn:
            await conn.execute("""
            INSERT INTO interactions 
            (interaction_id, user_id, session_id, query, response, classification, ab_variant, timestamp)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, 
            data.get("interaction_id"),
            data.get("user_id"),
            data.get("session_id"),
            data.get("query"),
            data.get("response"),
            data.get("classification"),
            data.get("ab_variant"),
            data.get("timestamp", datetime.now())
            )
    
    async def get_user_history(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get recent interactions for user"""
        if not self.pool: return []
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
            SELECT query, response, timestamp
            FROM interactions
            WHERE user_id = $1
            ORDER BY timestamp DESC
            LIMIT $2
            """, user_id, limit)
            
            return [dict(row) for row in rows]
    
    async def get_top_concerns(self, period: str = "weekly", limit: int = 10) -> List[Dict]:
        """Get top customer concerns"""
        if not self.pool: return []
        days = 7 if period == "weekly" else 30
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"""
            SELECT 
                query_type,
                COUNT(*) as frequency,
                AVG(CAST(emotional_trigger->>'intensity' AS FLOAT)) as emotional_intensity
            FROM insights
            WHERE timestamp > NOW() - INTERVAL '{days} days'
            GROUP BY query_type
            ORDER BY frequency DESC
            LIMIT $1
            """, limit)
            
            return [dict(row) for row in rows]
            
    async def get_user_segment(self, user_id: str):
        return "new_user"

    async def get_conversation_stage(self, user_id: str):
        return "awareness"

    async def get_system_stats(self):
        return {"interactions": 100, "insights": 50}

    async def log_feedback(self, feedback: Dict):
        pass # Placeholder
