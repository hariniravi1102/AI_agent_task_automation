from agents.base import BaseAgent, AgentResult


class DummyAgent(BaseAgent):
    name = "dummy_agent"

    def run(self, payload):
        return AgentResult(
            success=True,
            output={"message": f"{self.name} executed"}
        )
