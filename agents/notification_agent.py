from agents.base import BaseAgent, AgentResult
from llm.ollama_client import OllamaClient
from llm.logger import log_llm_decision


class NotificationAgent(BaseAgent):
    name = "notification_agent"

    def llm_prompt(self, summary, risk_level):
        return f"""
You are preparing a notification for internal operations.

Summary:
{summary}

Risk level: {risk_level}

Write a clear, concise notification message for a human.
Adjust tone based on risk level.

Respond ONLY in JSON:
{{
  "message": "notification text",
  "urgency": "low, medium, or high"
}}
"""

    def run(self, payload):

        summary = payload.get("summary")
        risk_level = payload.get("risk_level", "unknown")
        job_id = payload.get("job_id")

        if not summary:
            return AgentResult(
                success=False,
                error="Missing summary for notification"
            )


        llm_response = OllamaClient.run(
            self.llm_prompt(summary, risk_level)
        )

        if llm_response:
            message = llm_response.get("message")
            urgency = llm_response.get("urgency")


            log_llm_decision(
                job_id=job_id,
                step_name="notify",
                agent=self.name,
                decision=urgency,
                confidence=None,
                reasoning=message
            )

            return AgentResult(
                success=True,
                output={
                    "message": message,
                    "urgency": urgency,
                    "llm_used": True
                }
            )


        fallback_message = f"Workflow completed. Risk level: {risk_level}."

        return AgentResult(
            success=True,
            output={
                "message": fallback_message,
                "urgency": "unknown",
                "llm_used": False
            }
        )
