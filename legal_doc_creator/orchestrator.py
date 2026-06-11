"""Document processing orchestrator that coordinates between agents."""
import os
from typing import Optional
from agents.drafting_agent import DraftingAgent
from agents.editing_agent import EditingAgent
from models.document import LegalDocument


class DocumentOrchestrator:
    """Orchestrates the multi-agent legal document creation process."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        draft_model: str = "gpt-4",
        edit_model: str = "gpt-4",
        draft_temp: float = 0.7,
        edit_temp: float = 0.5,
        num_edit_passes: int = 1
    ):
        """
        Initialize the orchestrator.
        
        Args:
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
            draft_model: Model to use for drafting
            edit_model: Model to use for editing
            draft_temp: Temperature for draft agent
            edit_temp: Temperature for edit agent
            num_edit_passes: Number of editing passes to perform
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not provided and not found in environment")
        
        self.drafting_agent = DraftingAgent(api_key, draft_model, draft_temp)
        self.editing_agent = EditingAgent(api_key, edit_model, edit_temp)
        self.num_edit_passes = num_edit_passes
    
    def create_document(self, document: LegalDocument) -> LegalDocument:
        """
        Create a legal document through the multi-agent pipeline.
        
        Process:
        1. Draft the document
        2. Edit the document (configurable number of passes)
        3. Return the final document
        
        Args:
            document: The legal document to process
            
        Returns:
            LegalDocument: The document with all revisions
        """
        print(f"Starting document creation for: {document.document_type}")
        
        # Step 1: Draft
        print("\n[DRAFT AGENT] Drafting document...")
        document.status = "drafting"
        drafted_content, _ = self.drafting_agent.process(document)
        document.add_revision(drafted_content, "draft")
        print(f"Draft completed. Version: {document.current_version}")
        
        # Step 2: Edit (multiple passes)
        print("\n[EDIT AGENT] Editing document...")
        document.status = "editing"
        
        for pass_num in range(self.num_edit_passes):
            print(f"  Edit pass {pass_num + 1}/{self.num_edit_passes}...")
            edited_content, feedback = self.editing_agent.process(document)
            document.add_revision(edited_content, "edit", feedback)
            print(f"  Edit pass {pass_num + 1} completed. Version: {document.current_version}")
        
        # Step 3: Mark as completed
        document.status = "completed"
        print("\n[COMPLETE] Document creation finished!")
        
        return document
    
    def save_document(self, document: LegalDocument, output_dir: str = "./output") -> str:
        """
        Save the document to a file.
        
        Args:
            document: The legal document to save
            output_dir: Directory to save the document in
            
        Returns:
            str: Path to the saved file
        """
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{document.id}_{document.document_type.replace(' ', '_')}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Document Type: {document.document_type}\n")
            f.write(f"Status: {document.status}\n")
            f.write(f"Final Version: {document.current_version}\n")
            f.write("=" * 80 + "\n\n")
            f.write(document.get_current_content())
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("REVISION HISTORY\n")
            f.write("=" * 80 + "\n\n")
            
            for revision in document.get_history():
                f.write(f"Version {revision['version']} ({revision['agent']}) - {revision['timestamp']}\n")
                if revision['feedback']:
                    f.write(f"Feedback: {revision['feedback']}\n")
                f.write("-" * 40 + "\n")
        
        return filepath
