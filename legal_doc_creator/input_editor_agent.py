"""
Input Editing Agent - Validates and refines questionnaire data BEFORE drafting
Focused on data quality, completeness, and consistency
Does NOT touch the generated document
"""

from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class InputEditorAgent:
    """
    Reviews and refines questionnaire data before it goes to the drafting agent.
    Ensures data is complete, consistent, and high-quality.
    """
    
    def __init__(self):
        self.feedback = []
        self.suggestions = []
    
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

        # Conditionally check for witnesses based on signature method
        if document_type == 'advanced_directive' and data.get('signature_method') == 'witnesses':
            if not data.get('witness_1_name', '').strip():
                self.feedback.append("❌ MISSING: First witness name is required when using witnesses.")
            if not data.get('witness_2_name', '').strip():
                self.feedback.append("❌ MISSING: Second witness name is required when using witnesses.")

    def _check_consistency(self, data: Dict[str, Any]):
        """Check for logical consistency in responses"""
        
        # If healthcare agent is designated, they should have contact info
        if data.get('healthcare_agent_name'):
            if not data.get('healthcare_agent_phone') and not data.get('healthcare_agent_email'):
                self.feedback.append(
                    "❌ INCONSISTENT: Healthcare agent designated but no contact information provided"
                )
        if data.get('alternate_agent_name'):
            if not data.get('alternate_agent_phone') and not data.get('alternate_agent_email'):
                self.feedback.append(
                    "❌ INCONSISTENT: First alternate agent is designated but no contact information is provided."
                )
        if data.get('alternate_agent_2_name'):
            if not data.get('alternate_agent_2_phone') and not data.get('alternate_agent_2_email'):
                self.feedback.append(
                    "❌ INCONSISTENT: Second alternate agent is designated but no contact information is provided."
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
            self.suggestions.append(
                f"⚠️ Date of birth '{dob}' - please verify format is MM/DD/YYYY"
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
            
            # State-specific requirements
            state = data.get('state_of_residence', '').lower()
            witness_count = sum(1 for i in [1, 2] if data.get(f'witness_{i}_name', '').strip())
            signature_method = data.get('signature_method')

            if not signature_method:
                self.feedback.append("❌ MISSING: A signature method (witnesses or notary) must be chosen.")
                return  # Can't validate further without this

            if signature_method == 'witnesses':
                # Notary recommendation for interstate if not already chosen
                if not data.get('notary_required'):
                    self.suggestions.append(
                        f"💡 For {state.capitalize() if state else 'your state'} - Consider also having the document notarized for better validity across states."
                    )
            
            if signature_method == 'notary':
                if not data.get('notary_required'):
                    # This is an inconsistency, but we can suggest a fix or auto-fix.
                    self.suggestions.append("💡 'Notary' was selected as the signature method; the document will be set up for notarization.")
                    data['notary_required'] = True  # Auto-correct
                if witness_count > 0:
                    self.suggestions.append("💡 You chose to use a notary, but also provided witness information. The witness info will be ignored in the final document unless you also opted for witnesses.")

            if state == 'california':
                # California-specific checks can be added here if they are more detailed
                # The witness restrictions are already checked in _check_consistency
                pass
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """Check if date string is reasonable format"""
        # Simple check for MM/DD/YYYY or similar
        parts = date_str.split('/')
        if len(parts) != 3:
            return False
        try:
            month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
            return 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2025
        except (ValueError, TypeError):
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
