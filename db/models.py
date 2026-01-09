import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from db.session import Base



class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String, nullable=False)
    source = Column(String, nullable=True)
    status = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)



class Step(Base):
    __tablename__ = "steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))

    step_name = Column(String, nullable=False)
    agent = Column(String, nullable=False)
    status = Column(String, nullable=False)

    attempts = Column(Integer, default=0)
    error = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)




class LLMDecision(Base):
    __tablename__ = "llm_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=True)
    step_name = Column(String, nullable=False)
    agent = Column(String, nullable=False)
    trigger_type = Column(String)
    source = Column(String)
    decision = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    reasoning = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
