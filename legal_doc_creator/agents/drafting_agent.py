"""Agent responsible for drafting legal documents."""
from typing import Optional
import google.generativeai as genai
from agents.base_agent import BaseAgent
from models.document import LegalDocument


class DraftingAgent(BaseAgent):
    """Agent that drafts legal documents based on requirements."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-pro-latest", temperature: float = 0.7):
        super().__init__(name="Draft Agent", model=model, temperature=temperature)
        # The API key is configured globally by the orchestrator
        self.model_instance = genai.GenerativeModel(model)

    def process(self, document: LegalDocument) -> tuple[str, Optional[str]]:
        """
        Draft a legal document based on requirements.

        Args:
            document: The legal document with requirements
            
        Returns:
            tuple: (drafted_content, None)
        """
        prompt = self._build_prompt(document)
        drafted_content = self._call_llm(prompt)
        return drafted_content, None

    def _build_prompt(self, document: LegalDocument) -> str:
        """Build the drafting prompt."""
        return f"""You are an expert legal document drafter. Create a professional legal document based on the following requirements:

Document Type: {document.document_type}

Requirements:
{document.requirements}

Please draft a comprehensive, legally sound document that meets all the requirements. The document should be:
- Clear and professional
- Legally compliant
- Well-structured with appropriate sections
- Comprehensive but concise

Draft the document now:"""

    def _call_llm(self, prompt: str) -> str:
        """Call Gemini API to draft the document."""
        # The system prompt is combined with the user prompt for Gemini's API
        response = self.model_instance.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=8192  # Gemini 1.5 has a large context window
            )
        )
        return response.text
