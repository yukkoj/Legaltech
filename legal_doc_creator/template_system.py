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

        def format_phone(s):
            """Formats a 10-digit phone number string."""
            if not s:
                return ''
            digits = ''.join(filter(str.isdigit, str(s)))
            if len(digits) == 10:
                return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
            return s
        self.env.filters['format_phone'] = format_phone
    
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
        template_path.write_text(content, encoding='utf-8')
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
STATE OF CALIFORNIA

I, {{ full_name }}, being of sound mind and at least eighteen (18) years of age, execute this Advance Directive for Health Care. 
I revoke any prior advance directives I have made. This document reflects my healthcare preferences as of {{ today.strftime("%B %d, %Y") }}.

PURPOSE:
This document allows me to make known my wishes regarding my medical treatment if I become unable to communicate them. I have the right to refuse any medical treatment.

PART I: DESIGNATION OF HEALTHCARE AGENT

I designate {{ healthcare_agent_name }} ({{ healthcare_agent_relationship }}) as my healthcare agent to make medical decisions on my behalf if I am unable to do so.

Phone: {{ healthcare_agent_phone | format_phone }}
Email: {{ healthcare_agent_email }}
Address: {{ healthcare_agent_address }}

{% if alternate_agent_name %}
FIRST ALTERNATE HEALTHCARE AGENT:
If {{ healthcare_agent_name }} is unable or unwilling to serve, 
I designate {{ alternate_agent_name }} ({{ alternate_agent_relationship }}) as my first alternate healthcare agent.

Phone: {{ alternate_agent_phone | format_phone }}
Email: {{ alternate_agent_email }}
Address: {{ alternate_agent_address }}
{% endif %}

{% if alternate_agent_2_name %}
SECOND ALTERNATE HEALTHCARE AGENT:
If my primary and first alternate agents are unable or unwilling to serve, 
I designate {{ alternate_agent_2_name }} ({{ alternate_agent_2_relationship }}) as my second alternate healthcare agent.

Phone: {{ alternate_agent_2_phone | format_phone }}
Email: {{ alternate_agent_2_email }}
Address: {{ alternate_agent_2_address }}
{% endif %}

PART II: LIFE-SUSTAINING TREATMENT PREFERENCES
A. Cardiopulmonary Resuscitation (CPR)
{% if want_cpr == 'yes' %}
I request that cardiopulmonary resuscitation (CPR) be administered if my heart stops beating or I stop breathing.
{% elif want_cpr == 'no' %}
I do not want cardiopulmonary resuscitation (CPR). I wish for a natural death.
{% elif want_cpr == 'only_if_recovery' %}
I request CPR only if my medical team believes recovery to a meaningful quality of life is likely.
{% else %}
My preference regarding CPR is uncertain, and I leave this decision to my healthcare agent.
{% endif %}

B. Mechanical Ventilation
{% if want_mechanical_ventilation == 'yes' %}
I request the use of mechanical ventilation (a breathing machine) if I am unable to breathe on my own.
{% elif want_mechanical_ventilation == 'no' %}
I do not want to be placed on a mechanical ventilator.
{% elif want_mechanical_ventilation == 'only_if_recovery' %}
I request mechanical ventilation only as a temporary measure while it is determined if I can recover.
{% else %}
My preference regarding mechanical ventilation is uncertain, and I leave this decision to my healthcare agent.
{% endif %}

C. Artificial Feeding and Hydration
{% if want_feeding_tube == 'yes' %}
I request the use of a feeding tube for artificial nutrition and hydration if I am unable to eat or drink.
{% elif want_feeding_tube == 'no' %}
I do not want a feeding tube for artificial nutrition and hydration.
{% elif want_feeding_tube == 'only_if_recovery' %}
I request a feeding tube only if it is needed temporarily for my recovery.
{% else %}
My preference regarding a feeding tube is uncertain, and I leave this decision to my healthcare agent.
{% endif %}

D. Dialysis
{% if want_dialysis == 'yes' %}
I request dialysis if my kidneys fail.
{% elif want_dialysis == 'no' %}
I do not want dialysis.
{% elif want_dialysis == 'only_if_recovery' %}
I request dialysis only as a temporary measure to aid in my recovery.
{% else %}
My preference regarding dialysis is uncertain, and I leave this decision to my healthcare agent.
{% endif %}

E. Antibiotics
{% if want_antibiotics == 'yes' %}
I request antibiotics to treat infections.
{% elif want_antibiotics == 'no' %}
I do not want antibiotics to prolong my life, but I accept them for comfort.
{% elif want_antibiotics == 'only_if_recovery' %}
I request antibiotics only if the infection is treatable and I am expected to recover.
{% else %}
My preference regarding antibiotics is uncertain, and I leave this decision to my healthcare agent.
{% endif %}

F. Blood Transfusions
{% if want_blood_transfusions == 'yes' %}
I request blood transfusions if needed.
{% elif want_blood_transfusions == 'no' %}
I do not want blood transfusions.
{% elif want_blood_transfusions == 'only_if_recovery' %}
I request blood transfusions only if they are necessary for my recovery from a temporary condition.
{% else %}
My preference regarding blood transfusions is uncertain, and I leave this decision to my healthcare agent.
{% endif %}

PART III: CONDITION-SPECIFIC INSTRUCTIONS

{% if condition_permanently_unconscious %}
If I am permanently unconscious (e.g., a persistent vegetative state), my preference regarding life-sustaining treatment is as follows:
{% if condition_permanently_unconscious == 'yes' %}
I want life-sustaining treatment.
{% elif condition_permanently_unconscious == 'no' %}
I do NOT want life-sustaining treatment.
{% elif condition_permanently_unconscious == 'only_if_recovery' %}
I want life-sustaining treatment only if my medical team believes recovery to a meaningful quality of life is likely.
{% else %}
My preference is uncertain, and I leave this decision to my healthcare agent.
{% endif %}
{% endif %}

{% if condition_terminal_illness %}
If I am diagnosed with a terminal illness, my preference regarding life-sustaining treatment is as follows:
{% if condition_terminal_illness == 'yes' %}
I want life-sustaining treatment.
{% elif condition_terminal_illness == 'no' %}
I do NOT want life-sustaining treatment.
{% elif condition_terminal_illness == 'only_if_recovery' %}
I want life-sustaining treatment only if my medical team believes recovery to a meaningful quality of life is likely.
{% else %}
My preference is uncertain, and I leave this decision to my healthcare agent.
{% endif %}
{% endif %}

{% if condition_severe_dementia %}
If I am diagnosed with severe dementia or another irreversible cognitive condition, my preference regarding life-sustaining treatment is as follows:
{% if condition_severe_dementia == 'yes' %}
I want life-sustaining treatment.
{% elif condition_severe_dementia == 'no' %}
I do NOT want life-sustaining treatment.
{% elif condition_severe_dementia == 'only_if_recovery' %}
I want life-sustaining treatment only if my medical team believes recovery to a meaningful quality of life is likely.
{% else %}
My preference is uncertain, and I leave this decision to my healthcare agent.
{% endif %}
{% endif %}

{% if condition_other_incurable %}
If I am diagnosed with another incurable condition, my preference regarding life-sustaining treatment is as follows:
{% if condition_other_incurable == 'yes' %}
I want life-sustaining treatment.
{% elif condition_other_incurable == 'no' %}
I do NOT want life-sustaining treatment.
{% elif condition_other_incurable == 'only_if_recovery' %}
I want life-sustaining treatment only if my medical team believes recovery to a meaningful quality of life is likely.
{% else %}
My preference is uncertain, and I leave this decision to my healthcare agent.
{% endif %}
{% endif %}

PART IV: PAIN MANAGEMENT

{% if pain_management_priority %}
I direct that my comfort and pain management be prioritized, even if it might shorten my life.
{% else %}
While I want to be comfortable, I prioritize extending my life.
{% endif %}

{% if accept_medication_side_effects %}
I am willing to accept medications that may have side effects or may hasten death if they are necessary for my comfort.
{% else %}
I am not willing to accept medications that may hasten death, even if they are for comfort.
{% endif %}

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

{% if want_organ_donation == 'yes' or want_tissue_donation == 'yes' %}
PART VII: ORGAN AND TISSUE DONATION

{% if want_organ_donation == 'yes' %}
I wish to donate my organs for transplant. The specific organs I wish to donate are: {{ organ_donation_types | join_list }}.
{% else %}
I do not wish to donate organs.
{% endif %}

{% if want_tissue_donation == 'yes' %}
I wish to donate tissue for transplant. {% if tissue_donation_types %}The specific tissues are: {{ tissue_donation_types | join_list }}.{% else %}This includes skin, bone, and corneas as needed.{% endif %}
{% else %}
I do not wish to donate tissue.
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

State of California, County of __________________.

On ____________________ before me, ________________________________, personally appeared {{ full_name }}, who proved to me on the basis of satisfactory evidence to be the person whose name is subscribed to the within instrument and acknowledged to me that he/she executed the same in his/her authorized capacity, and that by his/her signature on the instrument the person, or the entity upon behalf of which the person acted, executed the instrument.

I certify under PENALTY OF PERJURY under the laws of the State of California that the foregoing paragraph is true and correct.

WITNESS my hand and official seal.


_____________________________ (Signature of Notary Public)

(Seal)

{% endif %}
{% if witness_1_name and witness_2_name %}


STATEMENT OF WITNESSES

I declare under penalty of perjury under the laws of California that
(1) the individual who signed or acknowledged this advance health care directive is personally known to me, 
or that the individual’s identity was proven to me by convincing evidence, 
(2) the individual signed or acknowledged this advance directive in my presence, 
(3) the individual appears to be of sound mind and under no duress, fraud, or undue influence, 
(4) I am not a person appointed as agent by this advance health care directive, and 
(5) I am not the individual’s health care provider, an employee of the individual’s health care provider, 
the operator of a community care facility, an employee of an operator of a community care facility, 
the operator of a residential care facility for the elderly, 
nor an employee of an operator of a residential care facility for the elderly.

Witness 1: {{ witness_1_name }} ({{ witness_1_phone | format_phone }})
Address: {{ witness_1_address }}

Signature: _______________

Date: _______________

I further declare under penalty of perjury under the laws of California that 
I am not related to the individual executing this advance health care directive by blood, marriage, or adoption, and, 
to the best of my knowledge, I am not entitled to any part of the individual’s estate upon his or her death under a will now existing or by operation of law.

Witness 2: {{ witness_2_name }} ({{ witness_2_phone | format_phone }})
Address: {{ witness_2_address }}

Signature: _______________

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
