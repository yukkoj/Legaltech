"""Agent responsible for drafting legal documents."""
from typing import Optional
from openai import OpenAI
from agents.base_agent import BaseAgent
from models.document import LegalDocument


class DraftingAgent(BaseAgent):
    """Agent that drafts legal documents based on requirements."""
    
    def __init__(self, api_key: str, model: str = "gpt-4", temperature: float = 0.7):
        super().__init__(name="Draft Agent", model=model, temperature=temperature)
        self.client = OpenAI(api_key=api_key)
    
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
        """Call OpenAI API to draft the document."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert legal document drafter."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=4000
        )
        return response.choices[0].message.content
