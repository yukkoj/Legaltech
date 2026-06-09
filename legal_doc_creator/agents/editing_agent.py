"""Agent responsible for editing and improving legal documents."""
from typing import Optional
from openai import OpenAI
from agents.base_agent import BaseAgent
from models.document import LegalDocument


class EditingAgent(BaseAgent):
    """Agent that reviews and edits legal documents for improvement."""
    
    def __init__(self, api_key: str, model: str = "gpt-4", temperature: float = 0.5):
        super().__init__(name="Edit Agent", model=model, temperature=temperature)
        self.client = OpenAI(api_key=api_key)
    
    def process(self, document: LegalDocument) -> tuple[str, Optional[str]]:
        """
        Review and edit a legal document.
        
        Args:
            document: The legal document to edit
            
        Returns:
            tuple: (edited_content, feedback)
        """
        prompt = self._build_prompt(document)
        edited_content, feedback = self._call_llm(prompt)
        return edited_content, feedback
    
    def _build_prompt(self, document: LegalDocument) -> str:
        """Build the editing prompt."""
        current_content = document.get_current_content()
        
        return f"""You are an expert legal document editor and reviewer. Review and improve the following legal document:

Document Type: {document.document_type}

Original Requirements:
{document.requirements}

Current Document:
{current_content}

Please:
1. Review the document for legal accuracy and completeness
2. Improve clarity, grammar, and professional language
3. Ensure all requirements are addressed
4. Identify any missing sections or potential issues
5. Provide an improved version of the document

Format your response as follows:
FEEDBACK:
[Your feedback and identified issues]

IMPROVED DOCUMENT:
[The improved document]"""
    
    def _call_llm(self, prompt: str) -> tuple[str, str]:
        """Call OpenAI API to edit the document."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert legal document editor and reviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=4500
        )
        
        content = response.choices[0].message.content
        
        # Parse feedback and document from response
        if "IMPROVED DOCUMENT:" in content:
            parts = content.split("IMPROVED DOCUMENT:")
            feedback = parts[0].replace("FEEDBACK:", "").strip()
            edited_document = parts[1].strip()
        else:
            feedback = "No specific feedback provided"
            edited_document = content
        
        return edited_document, feedback
