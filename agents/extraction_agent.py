import csv
from agents.base import BaseAgent, AgentResult
from llm.ollama_client import OllamaClient
from llm.logger import log_llm_decision


class ExtractionAgent(BaseAgent):
    name = "extraction_agent"

    def llm_prompt(self, headers: list) -> str:
        return f"""
You are mapping CSV column headers to canonical internal fields.

Headers:
{headers}

Respond ONLY in JSON:
{{
  "field_mapping": {{"source_field": "target_field"}},
  "confidence": 0.0,
  "notes": "short explanation"
}}
"""

    def run(self, payload):

        file_path = payload.get("path")
        job_id = payload.get("job_id")

        if not file_path:
            return AgentResult(
                success=False,
                error="Missing file path for extraction"
            )


        try:
            with open(file_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                headers = reader.fieldnames or []
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Failed to read CSV: {e}"
            )

        if not headers:
            return AgentResult(
                success=False,
                error="CSV has no headers"
            )


        llm_response = OllamaClient.run(self.llm_prompt(headers))

        field_mapping = {}
        confidence = None
        notes = None

        if llm_response:
            field_mapping = llm_response.get("field_mapping", {})
            confidence = llm_response.get("confidence")
            notes = llm_response.get("notes")


            log_llm_decision(
                job_id=job_id,
                step_name="extract",
                agent=self.name,
                decision=str(field_mapping),
                confidence=confidence,
                reasoning=notes
            )


        extracted = []

        for row in rows:
            new_row = {}
            for k, v in row.items():
                target_key = field_mapping.get(k, k)
                new_row[target_key] = v
            extracted.append(new_row)


        return AgentResult(
            success=True,
            output={
                "rows": extracted,
                "columns": list(extracted[0].keys()) if extracted else [],
                "llm_used": bool(llm_response),
                "confidence": confidence
            }
        )
