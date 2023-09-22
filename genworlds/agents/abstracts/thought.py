from abc import ABC, abstractmethod

class AbstractThought(ABC):

    @abstractmethod
    def run(self) -> str:
        """Calls an LLM and gets its output"""
        pass