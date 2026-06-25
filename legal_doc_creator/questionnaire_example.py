"""
Example usage of the Advance Directive questionnaire
Shows how to integrate the questionnaire into the document creation workflow
"""

try:
    from legal_doc_creator.questionnaires import AdvanceDirectiveQuestionnaireFlow, get_questionnaire
except ImportError:
    from questionnaires import AdvanceDirectiveQuestionnaireFlow, get_questionnaire
import json


def example_collect_advance_directive_info():
    """
    Example: Collect user information for an Advance Directive
    """
    # Create and run the questionnaire
    flow = AdvanceDirectiveQuestionnaireFlow()
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
    
    document_type = "advance_directive"
    
    # Get the questionnaire
    questionnaire = get_questionnaire(document_type)
    
    if questionnaire is None:
        print(f"No questionnaire found for document type: {document_type}")
        return
    
    # Create flow and collect responses
    flow = AdvanceDirectiveQuestionnaireFlow()
    responses = flow.run_interactive()
    
    # Now you can pass responses to agents for document generation
    document_data = responses.to_dict()
    
    # Example: Pass to drafting agent
    # draft = drafting_agent.generate_advance_directive(document_data)
    
    return document_data


if __name__ == "__main__":
    # Run the questionnaire
    print("Starting Advance Directive Questionnaire...")
    responses = example_collect_advance_directive_info()
    
    # Optional: Save responses to file
    import json
    with open("output/questionnaire_responses.json", "w") as f:
        json.dump(responses.to_dict(), f, indent=2, default=str)
    
    print("\nResponses saved to: output/questionnaire_responses.json")
