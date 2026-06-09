"""
UPDATED ORCHESTRATOR - Complete workflow coordination
Manages the full pipeline: Questionnaire → Input Review → Draft → Ready to Edit

Architecture (NEW):
1. COLLECT: User fills questionnaire via AdvancedDirectiveQuestionnaireFlow
2. REVIEW: InputEditorAgent validates & suggests improvements on USER DATA
3. REFINE: Save questionnaire as JSON
4. DRAFT: DraftingAgent renders template with JSON data
5. OUTPUT: Document ready for user editing (user revises INPUT, not the generated document)

Key Change:
- Editor now focuses on INPUT QUALITY, not document polishing
- Document is generated from template + valid JSON
- Separation of concerns: Input validation vs. Document generation
"""

import json
from typing import Dict, Any, Tuple, Optional
from pathlib import Path

try:
    from legal_doc_creator.questionnaires import AdvancedDirectiveQuestionnaireFlow, get_questionnaire
    from legal_doc_creator.input_editor_agent import InputEditorWorkflow
    from legal_doc_creator.drafting_agent import RefinedDraftingWorkflow, print_document_summary
except ImportError:
    # Fallback for relative imports
    from questionnaires import AdvancedDirectiveQuestionnaireFlow, get_questionnaire
    from input_editor_agent import InputEditorWorkflow
    from drafting_agent import RefinedDraftingWorkflow, print_document_summary


class DocumentOrchestrator:
    """
    Main orchestrator that manages the complete document generation pipeline.
    
    New Workflow (Updated):
    - Questionnaire Collection → Input Validation → Document Generation
    - Separation: Input Editor validates DATA, Drafting Agent renders TEMPLATE
    """
    
    def __init__(self):
        """Initialize orchestrator with sub-workflows"""
        self.input_editor_workflow = InputEditorWorkflow()
        self.drafting_workflow = RefinedDraftingWorkflow()
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_advanced_directive(self, interactive: bool = True) -> Dict[str, Any]:
        """
        Complete workflow to create an Advanced Directive
        
        Pipeline:
        1. Collect questionnaire responses (interactive)
        2. Validate input data quality
        3. Save questionnaire as JSON
        4. Generate document from template + JSON
        5. Return ready-to-use document
        
        Args:
            interactive: If True, collects user input via questionnaire
                        If False, expects questionnaire data elsewhere
        
        Returns:
            {
                'status': 'success' | 'review_required' | 'generation_error',
                'questionnaire_data': collected data dict,
                'validation_result': input validation results,
                'document': generated document text,
                'document_file': path to saved document,
                'questionnaire_file': path to saved questionnaire JSON
            }
        """
        
        result = {
            'status': None,
            'questionnaire_data': None,
            'validation_result': None,
            'document': None,
            'document_file': None,
            'questionnaire_file': None,
        }
        
        # STEP 1: COLLECT - Get questionnaire responses
        print("\n" + "="*70)
        print("STEP 1: QUESTIONNAIRE COLLECTION")
        print("="*70)
        
        if interactive:
            flow = AdvancedDirectiveQuestionnaireFlow()
            questionnaire_responses = flow.run_interactive()
            questionnaire_data = questionnaire_responses.to_dict()
        else:
            questionnaire_data = {}
        
        result['questionnaire_data'] = questionnaire_data
        
        # STEP 2: VALIDATE & REVIEW INPUT
        print("\n" + "="*70)
        print("STEP 2: INPUT REVIEW & VALIDATION")
        print("="*70)
        
        is_valid, review_result = self.input_editor_workflow.review_and_request_changes(
            questionnaire_data,
            document_type='advanced_directive'
        )
        
        result['validation_result'] = review_result
        
        if not is_valid:
            result['status'] = 'review_required'
            print("\n❌ Please address the issues above and try again.")
            return result
        
        # STEP 3: SAVE QUESTIONNAIRE AS JSON
        print("\n" + "="*70)
        print("STEP 3: SAVING DATA")
        print("="*70)
        
        questionnaire_file = self.output_dir / "advanced_directive_questionnaire.json"
        with open(questionnaire_file, 'w') as f:
            json.dump(questionnaire_data, f, indent=2, default=str)
        print(f"✅ Questionnaire saved: {questionnaire_file}")
        result['questionnaire_file'] = str(questionnaire_file)
        
        # STEP 4: GENERATE DOCUMENT
        print("\n" + "="*70)
        print("STEP 4: GENERATING DOCUMENT FROM TEMPLATE")
        print("="*70)
        
        generation_result = self.drafting_workflow.generate_from_questionnaire(
            questionnaire_data,
            document_type='advanced_directive',
            save_to_file=True
        )
        
        if generation_result.get('status') != 'success':
            result['status'] = 'generation_error'
            return result
        
        result['document'] = generation_result.get('document')
        result['document_file'] = generation_result.get('file_path')
        result['status'] = 'success'
        
        # Print summary
        print_document_summary(generation_result)
        
        # STEP 5: READY FOR USER REVIEW
        print("\n" + "="*70)
        print("STEP 5: DOCUMENT READY FOR REVIEW")
        print("="*70)
        print(f"""
✅ Your Advanced Directive has been generated!

📄 Document Location: {result['document_file']}
📋 Questionnaire Data: {result['questionnaire_file']}

NEXT STEPS:
1. Review the generated document carefully
2. Make any REFINEMENTS TO THE USER DATA (in JSON) if needed
3. Regenerate the document to see changes
4. Once satisfied, add signatures and witness information
5. Obtain witness signatures and notarization if desired

ARCHITECTURE NOTE:
- Input Editor validates USER DATA QUALITY only
- Drafting Agent renders the template (no content decisions)
- User edits the INPUT, not the generated document structure
""")
        
        return result
    
    def reload_and_regenerate(self, questionnaire_file: str) -> Dict[str, Any]:
        """
        Reload a previously saved questionnaire and regenerate document
        Useful if user wants to make changes and see updated output
        
        Args:
            questionnaire_file: Path to saved questionnaire JSON
        
        Returns:
            Generation result dict
        """
        try:
            with open(questionnaire_file, 'r') as f:
                questionnaire_data = json.load(f)
        except FileNotFoundError:
            return {
                'status': 'error',
                'error_message': f'File not found: {questionnaire_file}'
            }
        
        # Skip collection, go straight to validation
        is_valid, review_result = self.input_editor_workflow.review_and_request_changes(
            questionnaire_data,
            document_type='advanced_directive'
        )
        
        if not is_valid:
            return {
                'status': 'review_required',
                'validation_result': review_result
            }
        
        # Generate document with updated data
        generation_result = self.drafting_workflow.generate_from_questionnaire(
            questionnaire_data,
            document_type='advanced_directive',
            save_to_file=True
        )
        
        return generation_result


def main_interactive_menu():
    """Interactive main menu for document creation"""
    orchestrator = DocumentOrchestrator()
    
    while True:
        print("\n" + "="*70)
        print("LEGAL DOCUMENT CREATOR - ADVANCED DIRECTIVE")
        print("="*70)
        print("""
1. Create New Advanced Directive
2. Regenerate from Existing Questionnaire
3. Exit

Choose an option (1-3): """)
        
        choice = input().strip()
        
        if choice == '1':
            result = orchestrator.create_advanced_directive(interactive=True)
            if result['status'] == 'success':
                print("\n✅ Advanced Directive created successfully!")
            else:
                print(f"\n⚠️  Status: {result['status']}")
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            questionnaire_file = input("\nEnter questionnaire JSON file path: ").strip()
            result = orchestrator.reload_and_regenerate(questionnaire_file)
            
            if result.get('status') == 'success':
                print(f"\n✅ Document regenerated: {result.get('file_path')}")
            else:
                print(f"\n❌ Error: {result.get('error_message', 'Unknown error')}")
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    # Run interactive menu
    main_interactive_menu()
