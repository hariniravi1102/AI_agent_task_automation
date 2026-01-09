from abc import ABC, abstractmethod
from typing import Dict, Any


class AgentResult:
    def __init__(self, success: bool, output: Dict[str, Any] = None, error: str = None):
        self.success = success
        self.output = output or {}
        self.error = error


class BaseAgent(ABC):


    name: str = "base_agent"

    @abstractmethod
    def run(self, payload: Dict[str, Any]) -> AgentResult:

        pass
