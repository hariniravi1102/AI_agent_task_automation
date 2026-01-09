from agents.base import BaseAgent, AgentResult
from llm.ollama_client import OllamaClient
from llm.logger import log_llm_decision


class ReportAgent(BaseAgent):
    name = "report_agent"

    def llm_prompt(self, processed_rows, issues):
        return f"""
You are generating a report for internal operations.

Facts (do NOT invent data):
- Total rows processed: {len(processed_rows)}
- Issues detected: {len(issues)}
- Issue details: {issues[:5]}

Write a concise executive report.

Respond ONLY in JSON:
{{
  "summary": "short paragraph",
  "highlights": [
    "bullet point",
    "bullet point"
  ],
  "risk_level": "low, medium, or high"
}}
"""

    def run(self, payload):

        processed_rows = payload.get("processed_rows")
        issues = payload.get("issues", [])
        job_id = payload.get("job_id")

        if processed_rows is None:
            return AgentResult(
                success=False,
                error="Missing processed data for report generation"
            )


        llm_response = OllamaClient.run(
            self.llm_prompt(processed_rows, issues)
        )

        if llm_response:
            summary = llm_response.get("summary")
            highlights = llm_response.get("highlights", [])
            risk_level = llm_response.get("risk_level")


            log_llm_decision(
                job_id=job_id,
                step_name="report",
                agent=self.name,
                decision=risk_level,
                confidence=None,
                reasoning=summary
            )

            return AgentResult(
                success=True,
                output={
                    "summary": summary,
                    "highlights": highlights,
                    "risk_level": risk_level,
                    "llm_used": True
                }
            )


        fallback_summary = (
            f"Processed {len(processed_rows)} records "
            f"with {len(issues)} issues detected."
        )

        return AgentResult(
            success=True,
            output={
                "summary": fallback_summary,
                "highlights": [],
                "risk_level": "unknown",
                "llm_used": False
            }
        )
