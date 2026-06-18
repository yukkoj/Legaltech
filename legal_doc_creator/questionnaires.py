"""
Questionnaire modules for gathering user information for legal documents.
Each questionnaire guides users through the information needed for a specific document type.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class AdvancedDirectiveQuestionnaire:
    """Questionnaire for Advanced Directive (Advance Directive/Living Will)"""
    
    # Personal Information
    full_name: str = ""
    date_of_birth: str = ""
    state_of_residence: str = "California"
    
    # Healthcare Agent/Proxy
    healthcare_agent_name: str = ""
    healthcare_agent_phone: str = ""
    healthcare_agent_email: str = ""
    healthcare_agent_relationship: str = ""
    
    # Alternate Healthcare Agent
    alternate_agent_name: str = ""
    alternate_agent_phone: str = ""
    alternate_agent_email: str = ""
    alternate_agent_relationship: str = ""
    
    # Second Alternate Healthcare Agent
    alternate_agent_2_name: str = ""
    alternate_agent_2_phone: str = ""
    alternate_agent_2_email: str = ""
    alternate_agent_2_relationship: str = ""
    
    # Signature Method
    signature_method: str = ""  # "witnesses" or "notary"
    
    # Life-Sustaining Treatment Preferences
    # Responses: "yes", "no", "only_if", "uncertain"
    want_cpr: str = ""  # Cardiopulmonary resuscitation
    want_mechanical_ventilation: str = ""  # Breathing machine
    want_feeding_tube: str = ""  # Artificial nutrition/hydration
    want_dialysis: str = ""  # Kidney machine
    want_antibiotics: str = ""  # For infections
    want_blood_transfusions: str = ""
    
    # Conditions-based preferences
    condition_permanently_unconscious: str = ""  # Persistent vegetative state
    condition_terminal_illness: str = ""
    condition_severe_dementia: str = ""
    condition_other_incurable: str = ""
    
    # Pain Management
    pain_management_priority: bool = False  # Prioritize comfort over life extension
    accept_medication_side_effects: bool = False  # Accept drugs that may hasten death
    
    # Organ/Tissue Donation
    want_organ_donation: str = ""  # "yes", "no", "uncertain"
    organ_donation_types: List[str] = None  # ["heart", "lungs", "kidney", "liver", "all"]
    
    # Tissue Donation
    want_tissue_donation: str = ""  # "yes", "no", "uncertain"
    tissue_donation_types: List[str] = None  # ["cornea", "bone", "skin", "all"]
    
    # Body Disposition
    body_disposition: str = ""  # "burial", "cremation", "donation_to_science", "no_preference"
    specific_wishes_body: str = ""
    
    # Religious/Cultural Considerations
    religious_affiliation: str = ""
    religious_instructions: str = ""
    cultural_considerations: str = ""
    
    # Mental Health Preferences
    psychiatric_medications_preference: str = ""  # "continue", "discontinue", "case_by_case"
    mental_health_instructions: str = ""
    
    # Personal Values
    personal_values: str = ""  # Free text: what matters most to you in life
    quality_of_life_definition: str = ""  # What makes life worth living for you
    fears_and_concerns: str = ""
    
    # Additional Instructions
    other_instructions: str = ""
    
    # Witnesses/Notarization
    witness_1_name: str = ""
    witness_1_phone: str = ""
    witness_2_name: str = ""
    witness_2_phone: str = ""
    notary_required: bool = False
    
    # Review and Updates
    last_review_date: str = ""
    annual_review_planned: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert questionnaire to dictionary"""
        data = asdict(self)
        # Convert lists to strings for storage if needed
        if self.organ_donation_types:
            data['organ_donation_types'] = ", ".join(self.organ_donation_types)
        if self.tissue_donation_types:
            data['tissue_donation_types'] = ", ".join(self.tissue_donation_types)
        return data


class AdvancedDirectiveQuestionnaireFlow:
    """Interactive questionnaire flow for advanced directive"""
    
    def __init__(self):
        self.responses = AdvancedDirectiveQuestionnaire()
    
    def run_interactive(self) -> AdvancedDirectiveQuestionnaire:
        """Run interactive questionnaire and collect responses"""
        print("\n" + "="*70)
        print("ADVANCED DIRECTIVE QUESTIONNAIRE")
        print("="*70)
        print("\nThis questionnaire will guide you through creating an Advanced Directive.")
        print("An Advanced Directive allows you to specify your healthcare preferences")
        print("in advance, in case you become unable to communicate your wishes.\n")
        
        # Personal Information
        self._collect_personal_info()
        
        # Signature Method - moved up
        self._collect_signature_method()
        
        # Healthcare Agent
        self._collect_healthcare_agent()
        
        # Alternate Agent
        if self._ask_yes_no("Do you want to designate an alternate healthcare agent?"):
            self._collect_alternate_agent()
            if self._ask_yes_no("Do you want to designate a second alternate healthcare agent?"):
                self._collect_second_alternate_agent()
        
        # Life-Sustaining Treatment
        self._collect_treatment_preferences()
        
        # Organ Donation
        self._collect_organ_donation()
        
        # Body Disposition
        self._collect_body_disposition()
        
        # Personal Values
        self._collect_personal_values()
        
        # Witnesses
        if self.responses.signature_method == "witnesses":
            self._collect_witnesses()
        
        print("\n" + "="*70)
        print("Questionnaire Complete!")
        print("="*70 + "\n")
        
        return self.responses
    
    def _collect_personal_info(self):
        """Collect personal information"""
        print("\n--- SECTION 1: PERSONAL INFORMATION ---\n")
        self.responses.full_name = input("Full Legal Name: ").strip()
        self.responses.date_of_birth = input("Date of Birth (MM/DD/YYYY): ").strip()
        self.responses.state_of_residence = "California"
        print("State of Residence: California (This form is for California residents)")
    
    def _collect_healthcare_agent(self):
        """Collect healthcare agent information"""
        print("\n--- SECTION 2: HEALTHCARE AGENT (PROXY) ---\n")
        print("Designate someone to make healthcare decisions on your behalf if needed.")
        
        self.responses.healthcare_agent_name = input("Healthcare Agent Full Name: ").strip()
        self.responses.healthcare_agent_relationship = input("Relationship to you: ").strip()
        self.responses.healthcare_agent_phone = input("Phone Number: ").strip()
        self.responses.healthcare_agent_email = input("Email Address: ").strip()
    
    def _collect_alternate_agent(self):
        """Collect alternate healthcare agent information"""
        print("\n--- FIRST ALTERNATE HEALTHCARE AGENT ---\n")
        self.responses.alternate_agent_name = input("First Alternate Agent Full Name: ").strip()
        self.responses.alternate_agent_relationship = input("Relationship to you: ").strip()
        self.responses.alternate_agent_phone = input("Phone Number: ").strip()
        self.responses.alternate_agent_email = input("Email Address: ").strip()
    
    def _collect_second_alternate_agent(self):
        """Collect second alternate healthcare agent information"""
        print("\n--- SECOND ALTERNATE HEALTHCARE AGENT ---\n")
        self.responses.alternate_agent_2_name = input("Second Alternate Agent Full Name: ").strip()
        self.responses.alternate_agent_2_relationship = input("Relationship to you: ").strip()
        self.responses.alternate_agent_2_phone = input("Phone Number: ").strip()
        self.responses.alternate_agent_2_email = input("Email Address: ").strip()
    
    def _collect_signature_method(self):
        """Collect signature preference for California."""
        print("\n--- SECTION 2: DOCUMENT VALIDATION (SIGNATURES) ---\n")
        
        print("In California, an Advanced Directive must be signed with either:")
        print("  1. A notary public")
        print("  2. Two qualified witnesses")
        prompt = "\nHow would you like to validate your document? (Enter 1 or 2): "

        while True:
            choice = input(prompt).strip()
            if choice == '1':
                self.responses.signature_method = "notary"
                self.responses.notary_required = True
                print("\nYou have chosen to use a notary public.")
                break
            elif choice == '2':
                self.responses.signature_method = "witnesses"
                self.responses.notary_required = False
                print("\nYou have chosen to use two witnesses.")
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
    
    def _collect_treatment_preferences(self):
        """Collect preferences for life-sustaining treatments"""
        print("\n--- SECTION 3: LIFE-SUSTAINING TREATMENT PREFERENCES ---\n")
        print("Indicate your preferences for the following treatments:")
        print("(Use: Y=Yes, N=No, C=Only in case of recovery, U=Uncertain)\n")
        
        self.responses.want_cpr = self._get_treatment_preference(
            "Cardiopulmonary Resuscitation (CPR) if heart stops?"
        )
        self.responses.want_mechanical_ventilation = self._get_treatment_preference(
            "Mechanical ventilation (breathing machine)?"
        )
        self.responses.want_feeding_tube = self._get_treatment_preference(
            "Feeding tube (artificial nutrition/hydration)?"
        )
        self.responses.want_dialysis = self._get_treatment_preference(
            "Dialysis (kidney machine)?"
        )
        self.responses.want_antibiotics = self._get_treatment_preference(
            "Antibiotics for infections?"
        )
        self.responses.want_blood_transfusions = self._get_treatment_preference(
            "Blood transfusions?"
        )
        
        print("\n--- CONDITION-SPECIFIC PREFERENCES ---\n")
        print("If you develop these conditions, would you want life-sustaining treatment?\n")
        
        self.responses.condition_permanently_unconscious = self._get_treatment_preference(
            "If permanently unconscious (persistent vegetative state)?"
        )
        self.responses.condition_terminal_illness = self._get_treatment_preference(
            "If diagnosed with a terminal illness?"
        )
        self.responses.condition_severe_dementia = self._get_treatment_preference(
            "If diagnosed with severe dementia?"
        )
        self.responses.condition_other_incurable = self._get_treatment_preference(
            "If diagnosed with another incurable condition?"
        )
        
        print("\n--- PAIN MANAGEMENT & COMFORT ---\n")
        self.responses.pain_management_priority = self._ask_yes_no(
            "Should pain management and comfort be the priority, even if it might shorten life?"
        )
        self.responses.accept_medication_side_effects = self._ask_yes_no(
            "Are you willing to accept medications that may have side effects or may hasten death if needed for comfort?"
        )
    
    def _collect_organ_donation(self):
        """Collect organ and tissue donation preferences"""
        print("\n--- SECTION 4: ORGAN & TISSUE DONATION ---\n")
        
        if self._ask_yes_no("Do you wish to donate organs?"):
            self.responses.want_organ_donation = "yes"
            print("\nWhich organs would you like to donate?")
            organs = []
            if self._ask_yes_no("  Donate all organs for transplant?"):
                organs.append("all")
            else:
                print("\nPlease select which specific organs you wish to donate:")
                for organ in ["Heart", "Lungs", "Liver", "Kidneys", "Pancreas", "Corneas"]:
                    if self._ask_yes_no(f"  {organ}?"):
                        organs.append(organ.lower())
            self.responses.organ_donation_types = organs
        else:
            self.responses.want_organ_donation = "no"
        
        if self._ask_yes_no("\nDo you wish to donate tissue (skin, bone, etc.)?"):
            self.responses.want_tissue_donation = "yes"
            print("\nWhich tissues would you like to donate?")
            tissues = []
            if self._ask_yes_no("  Donate all tissues for transplant?"):
                tissues.append("all")
            else:
                print("\nPlease select which specific tissues you wish to donate:")
                for tissue in ["Skin", "Bone", "Corneas", "Heart Valves"]:
                    if self._ask_yes_no(f"  {tissue}?"):
                        tissues.append(tissue.lower())
            self.responses.tissue_donation_types = tissues
        else:
            self.responses.want_tissue_donation = "no"
    
    def _collect_body_disposition(self):
        """Collect preferences for body after death"""
        print("\n--- SECTION 5: BODY DISPOSITION ---\n")
        print("What are your preferences for your body after death?")
        print("1. Burial")
        print("2. Cremation")
        print("3. Donation to medical science")
        print("4. No preference")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        disposition_map = {
            "1": "burial",
            "2": "cremation",
            "3": "donation_to_science",
            "4": "no_preference"
        }
        self.responses.body_disposition = disposition_map.get(choice, "no_preference")
        
        special_wishes = input("\nAny special wishes or instructions? (optional): ").strip()
        if special_wishes:
            self.responses.specific_wishes_body = special_wishes
    
    def _collect_personal_values(self):
        """Collect personal values and life preferences"""
        print("\n--- SECTION 6: PERSONAL VALUES & BELIEFS ---\n")
        
        self.responses.religious_affiliation = input("Religious affiliation (if any): ").strip()
        
        if self.responses.religious_affiliation:
            self.responses.religious_instructions = input(
                "Any religious instructions or practices important to your care? "
            ).strip()
        
        self.responses.cultural_considerations = input(
            "Any cultural considerations important to you? "
        ).strip()
        
        self.responses.personal_values = input(
            "\nWhat matters most to you in life? (e.g., family, independence, creativity): "
        ).strip()
        
        self.responses.quality_of_life_definition = input(
            "What would make life not worth living for you? "
        ).strip()
        
        self.responses.fears_and_concerns = input(
            "What are your main fears or concerns about end-of-life care? "
        ).strip()
        
        self.responses.other_instructions = input(
            "\nAny other instructions or wishes? (optional): "
        ).strip()
    
    def _collect_witnesses(self):
        """Collect witness information for California."""
        print("\n--- SECTION 7: WITNESSES ---\n")
        print("Your document requires 2 witnesses. In California, witnesses generally cannot be:")
        print("  - Your healthcare agent or alternate agent")
        print("  - Your healthcare provider or their employee")
        print("  - An operator or employee of a care facility where you live")
        print("  - At least one witness must NOT be related to you or benefit from your estate.\n")
        
        self.responses.witness_1_name = input("Witness 1 Full Name: ").strip()
        self.responses.witness_1_phone = input("Witness 1 Phone Number: ").strip()
        
        self.responses.witness_2_name = input("Witness 2 Full Name: ").strip()
        self.responses.witness_2_phone = input("Witness 2 Phone Number: ").strip()
    
    def _get_treatment_preference(self, question: str) -> str:
        """Get treatment preference response"""
        while True:
            response = input(f"{question} (Y/N/C/U): ").strip().upper()
            if response in ["Y", "N", "C", "U"]:
                preference_map = {"Y": "yes", "N": "no", "C": "only_if_recovery", "U": "uncertain"}
                return preference_map[response]
            print("Please enter Y, N, C, or U.")
    
    def _ask_yes_no(self, question: str) -> bool:
        """Ask a yes/no question"""
        while True:
            response = input(f"{question} (Y/N): ").strip().upper()
            if response in ["Y", "N"]:
                return response == "Y"
            print("Please enter Y or N.")


# Questionnaire registry for document types
QUESTIONNAIRE_REGISTRY = {
    "advanced_directive": AdvancedDirectiveQuestionnaire,
    "advance_directive": AdvancedDirectiveQuestionnaire,
    "living_will": AdvancedDirectiveQuestionnaire,
}


def get_questionnaire(document_type: str) -> Optional[AdvancedDirectiveQuestionnaire]:
    """Get questionnaire instance for document type"""
    questionnaire_class = QUESTIONNAIRE_REGISTRY.get(document_type.lower())
    if questionnaire_class:
        return questionnaire_class()
    return None
