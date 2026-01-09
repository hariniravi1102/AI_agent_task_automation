from agents.base import BaseAgent, AgentResult
from llm.ollama_client import OllamaClient
from llm.logger import log_llm_decision


class ProcessingAgent(BaseAgent):
    name = "processing_agent"

    def llm_prompt(self, rows: list) -> str:
        # Keep prompt small & safe
        sample = rows[:5]

        return f"""
You are analyzing structured data for internal operations.

Here is a sample of the data:
{sample}

Look for anomalies, unusual values, or potential issues.

Respond ONLY in JSON:
{{
  "anomalies": [
    {{
      "row_index": number,
      "field": "field_name",
      "issue": "short description"
    }}
  ],
  "confidence": 0.0,
  "summary": "short explanation"
}}
"""

    def run(self, payload):

        rows = payload.get("rows")
        job_id = payload.get("job_id")

        if not rows or not isinstance(rows, list):
            return AgentResult(
                success=False,
                error="No structured rows available for processing"
            )


        processed_rows = rows.copy()
        issues = []

        for idx, row in enumerate(processed_rows):
            for key, value in row.items():
                if isinstance(value, str) and value.isdigit():
                    num = int(value)
                    if num > 10000:
                        issues.append({
                            "row_index": idx,
                            "field": key,
                            "issue": "Value exceeds expected threshold"
                        })


        llm_response = OllamaClient.run(
            self.llm_prompt(processed_rows)
        )

        if llm_response:
            anomalies = llm_response.get("anomalies", [])
            confidence = llm_response.get("confidence")
            summary = llm_response.get("summary")

            log_llm_decision(
                job_id=job_id,
                step_name="process",
                agent=self.name,
                decision=str(anomalies),
                confidence=confidence,
                reasoning=summary
            )


            issues.extend(anomalies)


        return AgentResult(
            success=True,
            output={
                "processed_rows": processed_rows,
                "issues": issues,
                "issue_count": len(issues),
                "llm_used": bool(llm_response)
            }
        )
