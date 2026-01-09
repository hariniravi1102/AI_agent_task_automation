from db.session import SessionLocal
from db.models import LLMDecision


def log_llm_decision(
    job_id,
    step_name,
    agent,
    decision,
    confidence,
    reasoning,
    trigger_type,
    source
):
    db = SessionLocal()
    try:
        entry = LLMDecision(
            job_id=job_id,
            step_name=step_name,
            agent=agent,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            trigger_type = trigger_type,
            source = source
        )
        db.add(entry)
        db.commit()
    finally:
        db.close()
