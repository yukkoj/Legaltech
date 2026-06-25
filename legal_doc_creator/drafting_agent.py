"""
Enhanced Drafting Agent - Generates documents from JSON data using templates
Uses validated questionnaire data to fill in templates
Focus: Technical rendering, not content creation
"""

from typing import Dict, Any, Optional
try:
    from legal_doc_creator.template_system import TemplateManager, DraftingWorkflow
except ImportError:
    from template_system import TemplateManager, DraftingWorkflow
import logging

logger = logging.getLogger(__name__)


class DraftingAgent:
    """
    Generates legal documents from validated questionnaire data using templates.
    
    Workflow:
    1. Receives validated questionnaire JSON data
    2. Selects appropriate template
    3. Renders template with data
    4. Returns formatted document
    
    This agent is TEMPLATE + DATA focused, not content-focused.
    Content quality is ensured by InputEditorAgent before this stage.
    """
    
    def __init__(self):
        self.template_manager = TemplateManager()
        self.workflow = DraftingWorkflow()
    
    def generate_advance_directive(self, questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an Advance Directive document from questionnaire data
        
        Args:
            questionnaire_data: Validated questionnaire responses as dict/JSON
        
        Returns:
            {
                'document': rendered document text,
                'document_type': 'advance_directive',
                'status': 'success' or 'error',
                'error_message': if status is error,
                'template_used': 'advance_directive.jinja2'
            }
        """
        
        try:
            # Use the workflow to render
            result = self.workflow.workflow_questionnaire_to_draft(
                questionnaire_data,
                document_type='advance_directive'
            )
            
            if result.get('draft'):
                return {
                    'document': result['draft'],
                    'document_type': 'advance_directive',
                    'status': 'success',
                    'template_used': 'advance_directive.jinja2',
                    'json_file': result.get('json_file'),
                    'data_quality_notes': result.get('validation_issues', [])
                }
            else:
                return {
                    'status': 'error',
                    'error_message': 'Template not found',
                    'document_type': 'advance_directive'
                }
        
        except Exception as e:
            logger.error(f"Error generating advance directive: {e}")
            return {
                'status': 'error',
                'error_message': str(e),
                'document_type': 'advance_directive'
            }
    
    def generate_document(self, questionnaire_data: Dict[str, Any], 
                         document_type: str = "advance_directive") -> Dict[str, Any]:
        """
        Generic document generation method
        
        Args:
            questionnaire_data: Validated questionnaire data
            document_type: Type of document to generate
        
        Returns:
            Dict with generated document or error
        """
        
        document_generators = {
            'advanced_directive': self.generate_advance_directive,
            'advance_directive': self.generate_advance_directive,
            'living_will': self.generate_advance_directive,
        }
        
        generator = document_generators.get(document_type.lower())
        if not generator:
            return {
                'status': 'error',
                'error_message': f'Unknown document type: {document_type}'
            }
        
        return generator(questionnaire_data)
    
    def save_document(self, document_text: str, filename: str, 
                     output_format: str = 'txt') -> str:
        """
        Save generated document to file
        
        Args:
            document_text: The rendered document
            filename: Output filename (without extension)
            output_format: 'txt', 'md', 'docx'
        
        Returns:
            Path to saved file
        """
        from pathlib import Path
        
        output_dir = Path('legal_doc_creator/output')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if output_format == 'txt':
            filepath = output_dir / f"{filename}.txt"
            filepath.write_text(document_text, encoding='utf-8')
        elif output_format == 'md':
            filepath = output_dir / f"{filename}.md"
            filepath.write_text(document_text, encoding='utf-8')
        else:
            raise NotImplementedError(f"Format '{output_format}' not yet supported")
        
        logger.info(f"Document saved: {filepath}")
        return str(filepath)


class RefinedDraftingWorkflow:
    """
    Complete end-to-end workflow:
    Questionnaire → Input Validation → JSON Save → Document Generation
    """
    
    def __init__(self):
        self.drafting_agent = DraftingAgent()
    
    def generate_from_questionnaire(self, questionnaire_data: Dict[str, Any],
                                    document_type: str = "advance_directive",
                                    save_to_file: bool = True) -> Dict[str, Any]:
        """
        Generate document from questionnaire data
        Assumes data has already been validated by InputEditorAgent
        
        Returns:
            {
                'status': 'success' or 'error',
                'document': rendered text,
                'document_type': type,
                'file_path': path if saved,
                'messages': list of info messages
            }
        """
        messages = []
        
        # Generate document
        result = self.drafting_agent.generate_document(questionnaire_data, document_type)
        
        if result.get('status') != 'success':
            return result
        
        messages.append(f"✅ Document generated successfully")
        
        # Optionally save to file
        if save_to_file:
            try:
                filepath = self.drafting_agent.save_document(
                    result['document'],
                    f"{document_type}_draft",
                    output_format='txt'
                )
                result['file_path'] = filepath
                messages.append(f"✅ Saved to: {filepath}")
            except Exception as e:
                messages.append(f"⚠️ Could not save file: {e}")
        
        result['messages'] = messages
        return result


def print_document_summary(generation_result: Dict[str, Any]):
    """Pretty print document generation results"""
    
    print("\n" + "="*70)
    print("DOCUMENT GENERATION RESULT")
    print("="*70 + "\n")
    
    if generation_result.get('status') == 'success':
        print(f"✅ Status: SUCCESS")
        print(f"📄 Document Type: {generation_result.get('document_type')}")
        print(f"📋 Template: {generation_result.get('template_used')}")
        if generation_result.get('file_path'):
            print(f"💾 Saved to: {generation_result.get('file_path')}")
        
        if generation_result.get('data_quality_notes'):
            print(f"\n⚠️ Data Quality Notes:")
            for note in generation_result['data_quality_notes']:
                print(f"   - {note}")
        
        # Show preview of document
        doc_preview = generation_result.get('document', '')
        lines = doc_preview.split('\n')[:15]
        print(f"\n--- Document Preview (first 15 lines) ---\n")
        print('\n'.join(lines))
        if len(doc_preview.split('\n')) > 15:
            print(f"\n... ({len(doc_preview.split(chr(10))) - 15} more lines)")
    
    else:
        print(f"❌ Status: ERROR")
        print(f"Error Message: {generation_result.get('error_message')}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # Example usage
    sample_questionnaire = {
        'full_name': 'Sarah Johnson',
        'date_of_birth': '05/20/1960',
        'state_of_residence': 'New York',
        'healthcare_agent_name': 'Michael Johnson',
        'healthcare_agent_relationship': 'Son',
        'healthcare_agent_phone': '212-555-0123',
        'healthcare_agent_email': 'michael@email.com',
        'want_cpr': 'yes',
        'want_mechanical_ventilation': 'only_if_recovery',
        'want_feeding_tube': 'only_if_recovery',
        'personal_values': 'Family, dignity, and meaningful relationships',
        'quality_of_life_definition': 'Able to spend time with loved ones and have meaningful conversations',
        'witness_1_name': 'Robert Williams',
        'witness_1_phone': '212-555-0456',
        'witness_2_name': 'Patricia Davis',
        'witness_2_phone': '212-555-0789',
    }
    
    workflow = RefinedDraftingWorkflow()
    result = workflow.generate_from_questionnaire(sample_questionnaire)
    print_document_summary(result)
