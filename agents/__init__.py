from agents.validation_agent import ValidationAgent
from agents.dummy_agent import DummyAgent

AGENT_REGISTRY = {
    ValidationAgent.name: ValidationAgent(),
    "extraction_agent": DummyAgent(),
    "processing_agent": DummyAgent(),
    "report_agent": DummyAgent(),
    "notification_agent": DummyAgent()
}
