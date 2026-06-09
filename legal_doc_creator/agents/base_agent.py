"""Base agent class for legal document processing."""
from abc import ABC, abstractmethod
from typing import Optional
from models.document import LegalDocument


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, name: str, model: str, temperature: float = 0.7):
        self.name = name
        self.model = model
        self.temperature = temperature
    
    @abstractmethod
    def process(self, document: LegalDocument) -> tuple[str, Optional[str]]:
        """
        Process a document and return the result and any feedback.
        
        Args:
            document: The legal document to process
            
        Returns:
            tuple: (processed_content, feedback)
        """
        pass
    
    @abstractmethod
    def _build_prompt(self, document: LegalDocument) -> str:
        """Build the prompt for the LLM."""
        pass
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt."""
        raise NotImplementedError("Subclasses must implement _call_llm")
