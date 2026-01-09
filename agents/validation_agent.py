from agents.base import BaseAgent, AgentResult
from llm.ollama_client import OllamaClient
from llm.logger import log_llm_decision


class ValidationAgent(BaseAgent):
    name = "validation_agent"

    def llm_prompt(self, payload: dict) -> str:
        filename = payload.get("filename", "unknown")
        columns = payload.get("columns", [])

        return f"""
You are validating a document for internal operations.

Filename: {filename}
Columns: {columns}

Respond ONLY in JSON:
{{
  "decision": "valid or invalid",
  "confidence": 0.0,
  "reasoning": "short explanation",
  "suggestions": []
}}
"""

    def run(self, payload):

        if "filename" not in payload:
            return AgentResult(
                success=False,
                error="Missing filename in payload"
            )


        llm_response = OllamaClient.run(self.llm_prompt(payload))

        if llm_response is None:
            return AgentResult(
                success=True,
                output={"validated": True, "llm_used": False}
            )

        decision = (llm_response.get("decision") or "").lower()
        confidence = llm_response.get("confidence", 0.0)
        reasoning = llm_response.get("reasoning", "")

        if decision not in ["valid", "invalid"]:
            decision = "valid"


        log_llm_decision(
            job_id=payload.get("job_id"),
            step_name="validate",
            agent=self.name,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            trigger_type = payload.get("trigger_type"),
        source = payload.get("source")
        )

        if decision == "invalid":
            return AgentResult(
                success=False,
                error=reasoning,
                output={
                    "confidence": confidence,
                    "suggestions": llm_response.get("suggestions", [])
                }
            )

        return AgentResult(
            success=True,
            output={
                "validated": True,
                "confidence": confidence,
                "llm_used": True
            }
        )
