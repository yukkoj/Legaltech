"""
Input Editing Agent - Validates and refines questionnaire data BEFORE drafting
Focused on data quality, completeness, and consistency
Does NOT touch the generated document
"""

from typing import Dict, List, Any, Tuple, Optional
import logging
from datetime import datetime
import os
import json
try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)


class InputEditorAgent:
    """
    Reviews and refines questionnaire data before it goes to the drafting agent.
    Ensures data is complete, consistent, and high-quality.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.feedback = []
        self.suggestions = []
        
        if genai is None:
            self.model = None
            logger.warning("google-generativeai client not installed. Skipping LLM-based analysis.")
            return
            
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            logger.warning("InputEditorAgent: No Gemini API key provided. LLM-based analysis will be skipped.")
    
    def review_input(self, questionnaire_data: Dict[str, Any], document_type: str = "advanced_directive") -> Dict[str, Any]:
        """
        Complete review of questionnaire input
        
        Returns:
            {
                'original_data': original input,
                'refined_data': updated input with corrections,
                'issues_found': list of issues,
                'suggestions': list of suggestions,
                'is_ready_to_draft': bool
            }
        """
        self.feedback = []
        self.suggestions = []
        
        refined_data = questionnaire_data.copy()
        
        # Run all validation checks
        self._check_completeness(refined_data, document_type)
        self._check_consistency(refined_data)
        self._check_clarity(refined_data)
        self._check_legal_validity(refined_data, document_type)
        
        # Add LLM-based analysis for free-text fields
        if self.model:
            self._analyze_free_text_with_llm(refined_data)
        
        is_ready = len(self.feedback) == 0  # Only issues block drafting, suggestions don't
        
        return {
            'original_data': questionnaire_data,
            'refined_data': refined_data,
            'issues_found': self.feedback,
            'suggestions': self.suggestions,
            'is_ready_to_draft': is_ready
        }
    
    def _check_completeness(self, data: Dict[str, Any], document_type: str):
        """Check for missing or incomplete information"""
        
        # Required fields that cannot be empty
        required_fields = {
            'advanced_directive': [
                ('full_name', 'Full legal name'),
                ('date_of_birth', 'Date of birth'),
                ('state_of_residence', 'State of residence'),
                ('healthcare_agent_name', 'Healthcare agent name'),
                ('healthcare_agent_relationship', 'Healthcare agent relationship'),
            ]
        }
        
        for field, label in required_fields.get(document_type, []):
            value = data.get(field, '').strip() if isinstance(data.get(field), str) else data.get(field)
            if not value:
                self.feedback.append(f"❌ MISSING: {label} (required)")
        
        # Check signature method: Either notary OR 2 witnesses required
        if document_type == 'advanced_directive':
            witness_1 = data.get('witness_1_name', '').strip()
            witness_2 = data.get('witness_2_name', '').strip()
            notary_required = data.get('notary_required')
            
            has_witnesses = witness_1 and witness_2
            has_notary = notary_required in [True, 'true']
            
            if not has_witnesses and not has_notary:
                self.feedback.append(
                    "❌ MISSING: Either notarization OR 2 witnesses are required. Please provide at least one."
                )
            
            # Check for partial witness information
            if (witness_1 and not witness_2) or (not witness_1 and witness_2):
                self.feedback.append("❌ INCOMPLETE: Both Witness 1 and Witness 2 names are required if providing witness information.")

    def _check_consistency(self, data: Dict[str, Any]):
        """Check for logical consistency in responses"""
        
        # If healthcare agent is designated, they should have contact info
        if data.get('healthcare_agent_name'):
            if not (data.get('healthcare_agent_phone') or data.get('healthcare_agent_email') or data.get('healthcare_agent_address')):
                self.feedback.append(
                    "❌ INCONSISTENT: Healthcare agent designated but no contact information (phone, email, or address) provided."
                )
        if data.get('alternate_agent_name'):
            if not (data.get('alternate_agent_phone') or data.get('alternate_agent_email') or data.get('alternate_agent_address')):
                self.feedback.append(
                    "❌ INCONSISTENT: First alternate agent is designated but no contact information (phone, email, or address) is provided."
                )
        if data.get('alternate_agent_2_name'):
            if not (data.get('alternate_agent_2_phone') or data.get('alternate_agent_2_email') or data.get('alternate_agent_2_address')):
                self.feedback.append(
                    "❌ INCONSISTENT: Second alternate agent is designated but no contact information (phone, email, or address) is provided."
                )
        
        # If organ donation is yes, donation types should be specified
        if data.get('want_organ_donation') in ['yes', True]:
            if not data.get('organ_donation_types'):
                self.suggestions.append(
                    "💡 If wanting organ donation, specify which organs (heart, lungs, etc.)"
                )

        # Agents must be unique individuals
        agent_name = data.get('healthcare_agent_name', '').lower().strip()
        alt1_name = data.get('alternate_agent_name', '').lower().strip()
        alt2_name = data.get('alternate_agent_2_name', '').lower().strip()

        if alt1_name and alt1_name == agent_name:
            self.feedback.append("❌ INCONSISTENT: First alternate agent cannot be the same person as the primary agent.")
        if alt2_name and alt2_name == agent_name:
            self.feedback.append("❌ INCONSISTENT: Second alternate agent cannot be the same person as the primary agent.")
        if alt1_name and alt2_name and alt1_name == alt2_name:
            self.feedback.append("❌ INCONSISTENT: Second alternate agent cannot be the same person as the first alternate agent.")
        
        # Witnesses cannot be the same person
        if data.get('witness_1_name') and data.get('witness_2_name'):
            if data.get('witness_1_name').lower() == data.get('witness_2_name').lower():
                self.feedback.append(
                    "❌ INCONSISTENT: Witnesses must be two different people"
                )

        # Witnesses cannot be any of the designated agents
        agent_names = {
            name for name in [
                data.get('healthcare_agent_name', '').lower().strip(),
                data.get('alternate_agent_name', '').lower().strip(),
                data.get('alternate_agent_2_name', '').lower().strip()
            ] if name
        }
        w1_name = data.get('witness_1_name', '').lower().strip()
        if w1_name and w1_name in agent_names:
            self.feedback.append("❌ INVALID: Witness 1 cannot be a designated healthcare agent (primary or alternate).")
        w2_name = data.get('witness_2_name', '').lower().strip()
        if w2_name and w2_name in agent_names:
            self.feedback.append("❌ INVALID: Witness 2 cannot be a designated healthcare agent (primary or alternate).")
    
    def _check_clarity(self, data: Dict[str, Any]):
        """Check for unclear or ambiguous responses"""
        
        # Check date format
        dob = data.get('date_of_birth', '').strip()
        if dob and not self._is_valid_date_format(dob):
            self.feedback.append(
                f"❌ INVALID: Date of birth '{dob}' is not a valid date. Please use the date picker to select a valid date."
            )
        
        # Check for very short text fields that should be longer
        if data.get('personal_values'):
            if len(data.get('personal_values', '').strip()) < 10:
                self.suggestions.append(
                    "💡 Personal values field is quite brief - consider adding more detail about what matters most to you"
                )
        
        if data.get('quality_of_life_definition'):
            if len(data.get('quality_of_life_definition', '').strip()) < 10:
                self.suggestions.append(
                    "💡 Quality of life definition is brief - consider elaborating what makes life worth living for you"
                )
        
        # Check treatment preferences - flag if ALL are "no"
        treatment_fields = [
            'want_cpr', 'want_mechanical_ventilation', 'want_feeding_tube',
            'want_dialysis', 'want_antibiotics', 'want_blood_transfusions'
        ]
        no_count = sum(1 for f in treatment_fields if data.get(f) == 'no')
        if no_count == len(treatment_fields):
            self.suggestions.append(
                "⚠️ All life-sustaining treatments marked as 'no' - verify this reflects your true wishes"
            )
    
    def _check_legal_validity(self, data: Dict[str, Any], document_type: str):
        """Check for legal requirements that might affect validity"""
        
        if document_type == 'advanced_directive':
            # Age requirement (typically 18+)
            # Note: Can't validate exact age without doing calculation
            dob = data.get('date_of_birth', '')
            if dob:
                logger.info(f"Age verification: User provided DOB {dob}")
            
            # Check signature method: Either notary OR witnesses
            witness_1 = data.get('witness_1_name', '').strip()
            witness_2 = data.get('witness_2_name', '').strip()
            notary_required = data.get('notary_required')
            
            has_witnesses = witness_1 and witness_2
            has_notary = notary_required in [True, 'true']
            
            state = data.get('state_of_residence', '').lower()
            
            # Provide suggestions based on signature method chosen
            if has_witnesses and not has_notary:
                self.suggestions.append(
                    f"💡 For {state.capitalize() if state else 'your state'} - Consider also having the document notarized for better validity across states."
                )
            
            if has_notary and not has_witnesses:
                self.suggestions.append(
                    f"💡 Notarization provides strong validity across all states including {state.capitalize() if state else 'your state'}."
                )
            
            if has_witnesses and has_notary:
                self.suggestions.append(
                    "💡 Providing both witnesses and notarization provides excellent protection for document validity."
                )

    def _analyze_free_text_with_llm(self, data: Dict[str, Any]):
        """Use an LLM to analyze free-text fields for clarity and consistency."""
        
        if not self.model:
            return

        # Gather the free-text fields
        free_text_data = {
            "personal_values": data.get("personal_values", ""),
            "quality_of_life_definition": data.get("quality_of_life_definition", ""),
            "fears_and_concerns": data.get("fears_and_concerns", ""),
            "other_instructions": data.get("other_instructions", "")
        }
        
        # Only proceed if there is content to analyze
        if not any(free_text_data.values()):
            return

        prompt = f"""
        You are a helpful assistant reviewing a user's input for a legal document (an Advance Directive).
        Your goal is to help the user make their wishes as clear and unambiguous as possible.
        Analyze the following user-provided statements for potential issues.
        
        User Statements:
        - What matters most to me: "{free_text_data['personal_values']}"
        - What makes life not worth living: "{free_text_data['quality_of_life_definition']}"
        - Main fears and concerns: "{free_text_data['fears_and_concerns']}"
        - Other instructions: "{free_text_data['other_instructions']}"

        Review these statements and identify:
        1.  **Ambiguities**: Phrases that are unclear or could be interpreted in multiple ways (e.g., "be comfortable").
        2.  **Contradictions**: Statements that seem to conflict with each other.

        Provide your feedback in a JSON format with two keys: "issues" and "suggestions".
        - "issues" should be a list of strings for critical problems that might block drafting.
        - "suggestions" should be a list of objects, where each object provides advice for improving clarity. Each object should have three keys:
            - "original_text": The specific vague phrase from the user's input.
            - "suggestion": A gentle explanation of why the phrase is ambiguous and what the user should consider.
            - "example_revision": A concrete example of how the user could rephrase their wish to be clearer.

        If there are no problems, return empty lists for both "issues" and "suggestions".
        IMPORTANT: Your entire response must be a single valid JSON object.

        Example of a good object inside the "suggestions" list:
        {{
            "original_text": "I want to be comfortable.",
            "suggestion": "The term 'comfortable' can be interpreted in many ways. It's helpful to specify what comfort means to you.",
            "example_revision": "For example, you could write: 'I want to be kept clean, in a quiet room, with my favorite music playing, and receive medication to be free from pain, even if it makes me drowsy.'"
        }}

        Your JSON response:
        """

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            
            llm_feedback = json.loads(response.text)

            if llm_feedback.get("issues"):
                for issue in llm_feedback["issues"]:
                    self.feedback.append(f"❌ LLM REVIEW: {issue}")
            
            if llm_feedback.get("suggestions"):
                for suggestion in llm_feedback.get("suggestions", []):
                    if isinstance(suggestion, dict) and all(k in suggestion for k in ["original_text", "suggestion", "example_revision"]):
                        formatted_suggestion = (
                            f"Regarding \"{suggestion['original_text']}\": {suggestion['suggestion']} "
                            f"For example: \"{suggestion['example_revision']}\""
                        )
                        self.suggestions.append(f"💡 LLM SUGGESTION: {formatted_suggestion}")
                    else:
                        # Fallback for old format (string) or malformed object
                        self.suggestions.append(f"💡 LLM SUGGESTION: {str(suggestion)}")

        except Exception as e:
            logger.error(f"LLM analysis failed in InputEditorAgent: {e}")
            self.suggestions.append("⚠️ Could not perform LLM-based analysis of free-text fields.")
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """Check if date string is a valid date in YYYY-MM-DD format."""
        if not isinstance(date_str, str):
            return False
        try:
            # The HTML <input type="date"> provides date in 'YYYY-MM-DD' format.
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            # Check for a reasonable year range (e.g., not in the future).
            if 1900 <= dt.year <= datetime.now().year:
                return True
        except (ValueError, TypeError):
            # This will catch invalid dates like '2023-02-30'
            return False
        return False
    
    def generate_review_report(self, review_result: Dict[str, Any]) -> str:
        """Generate human-readable review report"""
        
        issues = review_result['issues_found']
        suggestions = review_result['suggestions']
        is_ready = review_result['is_ready_to_draft']
        
        report = "\n" + "="*70
        report += "\nQUESTIONNAIRE REVIEW REPORT\n"
        report += "="*70 + "\n"
        
        if is_ready:
            report += "\n✅ STATUS: READY FOR DRAFTING\n"
        else:
            report += "\n❌ STATUS: ISSUES FOUND - PLEASE REVIEW BELOW\n"
        
        if issues:
            report += "\n--- CRITICAL ISSUES (Must fix before drafting) ---\n"
            for issue in issues:
                report += f"  {issue}\n"
        else:
            report += "\n--- Critical Issues: None ---\n"
        
        if suggestions:
            report += "\n--- SUGGESTIONS (Optional improvements) ---\n"
            for suggestion in suggestions:
                report += f"  {suggestion}\n"
        else:
            report += "\n--- Suggestions: None ---\n"
        
        report += "\n" + "="*70 + "\n"
        
        return report


class InputEditorWorkflow:
    """Complete workflow: Collect → Review → Refine → Ready to Draft"""
    
    def __init__(self):
        self.editor = InputEditorAgent()
    
    def review_and_request_changes(self, questionnaire_data: Dict[str, Any], 
                                   document_type: str = "advanced_directive") -> Tuple[bool, Dict[str, Any]]:
        """
        Review questionnaire and return whether it's ready or needs changes
        
        Returns:
            (is_ready_bool, review_result_dict)
        """
        review_result = self.editor.review_input(questionnaire_data, document_type)
        report = self.editor.generate_review_report(review_result)
        
        print(report)
        
        if not review_result['is_ready_to_draft']:
            print("\n⚠️  Please address the critical issues above and resubmit.\n")
            return False, review_result
        else:
            print("\n✅ All checks passed! Ready to proceed to drafting.\n")
            return True, review_result


if __name__ == "__main__":
    # Example usage
    sample_data = {
        'full_name': 'John Smith',
        'date_of_birth': '01/15/1950',
        'state_of_residence': 'California',
        'healthcare_agent_name': 'Jane Smith',
        'healthcare_agent_relationship': 'Daughter',
        'healthcare_agent_phone': '555-0123',
        'witness_1_name': 'Bob Johnson',
        'witness_1_phone': '555-0456',
        'witness_2_name': 'Alice Brown',
        'witness_2_phone': '555-0789',
        'personal_values': 'Family, independence, and living with dignity',
        'quality_of_life_definition': 'Able to recognize family and engage in meaningful activities',
    }
    
    workflow = InputEditorWorkflow()
    is_ready, result = workflow.review_and_request_changes(sample_data)
