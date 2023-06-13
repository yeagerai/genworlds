from abc import ABC, abstractmethod

class Brain(ABC):
    @abstractmethod
    def run(self, llm_params: dict) -> str:
        """Run the brain with the given parameters and produce a response."""