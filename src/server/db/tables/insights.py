from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text

from src.server.db.database import Base


class AIInsightSnapshot(Base):
    __tablename__ = "ai_insight_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    provider = Column(String, nullable=False, default="minimax")
    model = Column(String, nullable=True)
    status = Column(String, nullable=False, default="error")
    recommendations_json = Column(Text, nullable=True)
    source_context_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


Index("idx_ai_insight_user_generated", AIInsightSnapshot.user_id, AIInsightSnapshot.generated_at.desc())
Index("idx_ai_insight_user_status_generated", AIInsightSnapshot.user_id, AIInsightSnapshot.status, AIInsightSnapshot.generated_at.desc())
