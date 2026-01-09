import requests
import json
from typing import Optional, Dict

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"


class OllamaClient:
    @staticmethod
    def run(prompt: str, temperature: float = 0.2) -> Optional[Dict]:
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9
            }
        }

        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=30)
            resp.raise_for_status()

            raw = resp.json().get("response", "").strip()

            return json.loads(raw)

        except Exception as e:
            print(f"LLM call failed: {e}")
            return None
