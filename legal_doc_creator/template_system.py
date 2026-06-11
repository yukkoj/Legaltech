"""
Template-based document generation system using JSON data
Integrates questionnaire data with Jinja2 templates for document drafting
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template, TemplateError, select_autoescape
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TemplateManager:
    """Manages document templates and rendering"""
    
    def __init__(self, template_dir: str = "legal_doc_creator/templates"):
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        # Added select_autoescape for security best practices
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            keep_trailing_newline=True,
            autoescape=select_autoescape(['html', 'xml'])
        )
        # Add custom filters
        self._register_filters()

    def _register_filters(self):
        """Register custom Jinja2 filters"""
        self.env.filters['yesno'] = lambda v: 'Yes' if v else 'No'
        self.env.filters['capitalize_words'] = lambda v: v.title() if v else ''
        self.env.filters['join_list'] = lambda lst: ', '.join(lst) if lst else ''
        self.env.globals['now'] = datetime.now # Make datetime.now available as 'now()' in templates
    
    def render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Render template with JSON data"""
        try:
            template = self.env.get_template(template_name)
            return template.render(**data)
        except TemplateError as e:
            logger.error(f"Template error in {template_name}: {e}")
            raise
    
    def create_template(self, name: str, content: str):
        """Create a new template file"""
        template_path = self.template_dir / name
        template_path.write_text(content)
        logger.info(f"Template created: {template_path}")


class JSONDataManager:
    """Manages questionnaire data as JSON"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_questionnaire_json(self, data: Dict[str, Any], filename: str = "questionnaire.json") -> Path:
        """Save questionnaire responses as JSON"""
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Questionnaire saved: {filepath}")
        return filepath
    
    def load_questionnaire_json(self, filename: str = "questionnaire.json") -> Dict[str, Any]:
        """Load questionnaire from JSON"""
        filepath = self.output_dir / filename
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: list) -> tuple[bool, list]:
        """Validate that all required fields are present and non-empty"""
        missing = []
        for field in required_fields:
            if not data.get(field) or (isinstance(data.get(field), str) and not data.get(field).strip()):
                missing.append(field)
        return len(missing) == 0, missing
    
    def validate_conditional_fields(self, data: Dict[str, Any], conditions: Dict[str, list]) -> tuple[bool, list]:
        """Validate conditional required fields"""
        issues = []
        for trigger_field, required_fields in conditions.items():
            if data.get(trigger_field) in ["yes", True]:
                for field in required_fields:
                    if not data.get(field):
                        issues.append(f"Field '{field}' is required when '{trigger_field}' is yes")
        return len(issues) == 0, issues


class DraftingWorkflow:
    """Orchestrates the questionnaire → JSON → draft workflow"""
    
    def __init__(self):
        self.template_manager = TemplateManager()
        self.data_manager = JSONDataManager()
    
    def workflow_questionnaire_to_draft(self, questionnaire_data: Dict[str, Any], 
                                       document_type: str = "advanced_directive") -> Dict[str, Any]:
        """
        Complete workflow from questionnaire to draft
        
        Returns:
            {
                'json_file': path to saved JSON,
                'json_data': the questionnaire data,
                'validation_issues': list of data quality issues,
                'draft': rendered document (if no critical issues)
            }
        """
        result = {
            'json_file': None,
            'json_data': questionnaire_data,
            'validation_issues': [],
            'draft': None
        }
        
        # Step 1: Save questionnaire as JSON
        result['json_file'] = self.data_manager.save_questionnaire_json(
            questionnaire_data, 
            f"{document_type}_questionnaire.json"
        )
        
        # Step 2: Validate data quality
        validation_issues = self._validate_data(questionnaire_data, document_type)
        result['validation_issues'] = validation_issues
        
        if validation_issues:
            logger.warning(f"Data quality issues found: {validation_issues}")
            # Don't block drafting, but flag for editor review
        
        # Step 3: Draft document using template
        try:
            template_name = f"{document_type}.jinja2"
            draft = self.template_manager.render_template(template_name, questionnaire_data)
            result['draft'] = draft
        except FileNotFoundError:
            logger.error(f"Template not found: {template_name}")
            result['draft'] = None
        
        return result
    
    def _validate_data(self, data: Dict[str, Any], document_type: str) -> list:
        """Validate questionnaire data for completeness"""
        issues = []
        
        # Define required fields by document type
        required_by_type = {
            'advanced_directive': [
                'full_name', 'date_of_birth', 'state_of_residence',
                'healthcare_agent_name', 'healthcare_agent_relationship',
                'witness_1_name', 'witness_2_name'
            ]
        }
        
        # Define conditional requirements
        conditionals = {
            'advanced_directive': {
                'want_organ_donation': ['organ_donation_types'],
                'want_tissue_donation': ['tissue_donation_types']
            }
        }
        
        required_fields = required_by_type.get(document_type, [])
        is_complete, missing = self.data_manager.validate_required_fields(data, required_fields)
        if not is_complete:
            issues.extend([f"Missing required field: {field}" for field in missing])
        
        conditional_reqs = conditionals.get(document_type, {})
        is_conditional_ok, conditional_issues = self.data_manager.validate_conditional_fields(
            data, conditional_reqs
        )
        if not is_conditional_ok:
            issues.extend(conditional_issues)
        
        return issues


# Example: Sample Advanced Directive Template
ADVANCED_DIRECTIVE_TEMPLATE = '''
{# Advanced Directive Template using Jinja2 #}
{% set today = now() %}

ADVANCE DIRECTIVE FOR HEALTH CARE
STATE OF {{ state_of_residence | upper }}

I, {{ full_name }}, being of sound mind and at least eighteen (18) years of age, execute this Advance Directive for Health Care.

PURPOSE:
This document allows me to make known my wishes regarding my medical treatment if I become unable to communicate them. I have the right to refuse any medical treatment.

PART I: DESIGNATION OF HEALTHCARE AGENT

I designate {{ healthcare_agent_name }} ({{ healthcare_agent_relationship }}) as my healthcare agent to make medical decisions on my behalf if I am unable to do so.

Phone: {{ healthcare_agent_phone }}
Email: {{ healthcare_agent_email }}

{% if alternate_agent_name %}
FIRST ALTERNATE HEALTHCARE AGENT:
If {{ healthcare_agent_name }} is unable or unwilling to serve, I designate {{ alternate_agent_name }} ({{ alternate_agent_relationship }}) as my first alternate healthcare agent.
Phone: {{ alternate_agent_phone }}
Email: {{ alternate_agent_email }}
{% endif %}

{% if alternate_agent_2_name %}
SECOND ALTERNATE HEALTHCARE AGENT:
If my primary and first alternate agents are unable or unwilling to serve, I designate {{ alternate_agent_2_name }} ({{ alternate_agent_2_relationship }}) as my second alternate healthcare agent.
Phone: {{ alternate_agent_2_phone }}
Email: {{ alternate_agent_2_email }}
{% endif %}

PART II: LIFE-SUSTAINING TREATMENT PREFERENCES

A. Cardiopulmonary Resuscitation (CPR):
I request CPR: {{ want_cpr | yesno }}

B. Mechanical Ventilation:
I request mechanical ventilation (breathing machine): {{ want_mechanical_ventilation | yesno }}

C. Artificial Feeding and Hydration:
I request feeding tube or artificial nutrition: {{ want_feeding_tube | yesno }}

D. Dialysis:
I request dialysis: {{ want_dialysis | yesno }}

E. Antibiotics:
I request antibiotics for infections: {{ want_antibiotics | yesno }}

F. Blood Transfusions:
I request blood transfusions: {{ want_blood_transfusions | yesno }}

PART III: CONDITION-SPECIFIC INSTRUCTIONS

{% if condition_permanently_unconscious %}
If I am permanently unconscious (persistent vegetative state):
My preference: {{ condition_permanently_unconscious }}
{% endif %}

{% if condition_terminal_illness %}
If I have a terminal illness:
My preference: {{ condition_terminal_illness }}
{% endif %}

{% if condition_severe_dementia %}
If I have advanced dementia:
My preference: {{ condition_severe_dementia }}
{% endif %}

PART IV: PAIN MANAGEMENT

I request that pain management and comfort be prioritized: {{ pain_management_priority | yesno }}
I accept medications that may hasten death if necessary for comfort: {{ accept_medication_side_effects | yesno }}

{% if personal_values %}
PART V: PERSONAL VALUES AND BELIEFS

What matters most to me: {{ personal_values }}

Quality of life considerations: {{ quality_of_life_definition }}

My main concerns: {{ fears_and_concerns }}
{% endif %}

{% if religious_affiliation %}
PART VI: RELIGIOUS AND CULTURAL CONSIDERATIONS

Religious affiliation: {{ religious_affiliation }}

{% if religious_instructions %}
Religious instructions: {{ religious_instructions }}
{% endif %}

{% if cultural_considerations %}
Cultural considerations: {{ cultural_considerations }}
{% endif %}
{% endif %}

{% if want_organ_donation == 'yes' %}
PART VII: ORGAN AND TISSUE DONATION

I wish to donate the following organs: {{ organ_donation_types | join_list }}
I wish to donate tissue: {{ want_tissue_donation | yesno }}
{% if tissue_donation_types %}
Types: {{ tissue_donation_types | join_list }}
{% endif %}
{% endif %}

PART VIII: BODY DISPOSITION

Preference for my body: {{ body_disposition | replace('_', ' ') | capitalize_words }}

{% if specific_wishes_body %}
Special wishes: {{ specific_wishes_body }}
{% endif %}

PART IX: SIGNATURE AND VALIDATION

I acknowledge this is my wishes regarding health care and authorize my healthcare agent to act according to this document.

_____________________________
{{ full_name }}
Date: _______________
{% if notary_required %}


NOTARIZATION

A notary public or other officer completing this certificate verifies only the identity of the individual who signed the document to which this certificate is attached, and not the truthfulness, accuracy, or validity of that document.

State of ____________________, County of __________________.

On ____________________ before me, ________________________________, personally appeared {{ full_name }}, who proved to me on the basis of satisfactory evidence to be the person whose name is subscribed to the within instrument and acknowledged to me that he/she executed the same in his/her authorized capacity, and that by his/her signature on the instrument the person, or the entity upon behalf of which the person acted, executed the instrument.

I certify under PENALTY OF PERJURY under the laws of the State of California that the foregoing paragraph is true and correct.

WITNESS my hand and official seal.
_____________________________ (Signature of Notary Public)
(Seal)
{% endif %}
{% if witness_1_name and witness_2_name %}


STATEMENT OF WITNESSES

I certify that the above person signed this document in my presence and appears to be of sound mind.

Witness 1: {{ witness_1_name }} ({{ witness_1_phone }})
Date: _______________

Witness 2: {{ witness_2_name }} ({{ witness_2_phone }})
Date: _______________
{% endif %}
'''


def setup_example_template():
    """Create example template for testing"""
    manager = TemplateManager()
    manager.create_template("advanced_directive.jinja2", ADVANCED_DIRECTIVE_TEMPLATE)


if __name__ == "__main__":
    setup_example_template()
    print("Template system ready!")
