"""
Example usage of the Advanced Directive questionnaire
Shows how to integrate the questionnaire into the document creation workflow
"""

from legal_doc_creator.questionnaires import AdvancedDirectiveQuestionnaireFlow
import json


def example_collect_advanced_directive_info():
    """
    Example: Collect user information for an Advanced Directive
    """
    # Create and run the questionnaire
    flow = AdvancedDirectiveQuestionnaireFlow()
    responses = flow.run_interactive()
    
    # Convert to dictionary for processing
    questionnaire_data = responses.to_dict()
    
    print("\n" + "="*70)
    print("SUMMARY OF YOUR RESPONSES")
    print("="*70)
    print(json.dumps(questionnaire_data, indent=2, default=str))
    
    return responses


def example_with_orchestrator():
    """
    Example: How to integrate questionnaire into orchestrator workflow
    """
    # This is how you would use it in orchestrator.py
    from legal_doc_creator.questionnaires import get_questionnaire
    
    document_type = "advanced_directive"
    
    # Get the questionnaire
    questionnaire = get_questionnaire(document_type)
    
    if questionnaire is None:
        print(f"No questionnaire found for document type: {document_type}")
        return
    
    # Create flow and collect responses
    flow = AdvancedDirectiveQuestionnaireFlow()
    responses = flow.run_interactive()
    
    # Now you can pass responses to agents for document generation
    document_data = responses.to_dict()
    
    # Example: Pass to drafting agent
    # draft = drafting_agent.generate_advanced_directive(document_data)
    
    return document_data


if __name__ == "__main__":
    # Run the questionnaire
    print("Starting Advanced Directive Questionnaire...")
    responses = example_collect_advanced_directive_info()
    
    # Optional: Save responses to file
    import json
    with open("legal_doc_creator/output/questionnaire_responses.json", "w") as f:
        json.dump(responses.to_dict(), f, indent=2, default=str)
    
    print("\nResponses saved to: legal_doc_creator/output/questionnaire_responses.json")
