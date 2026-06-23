import requests
import json

# Sample questionnaire data
sample_questionnaire = {
    'full_name': 'John Doe',
    'date_of_birth': '01/01/1980',
    'state_of_residence': 'California',
    'healthcare_agent_name': 'Jane Doe',
    'healthcare_agent_relationship': 'Wife',
    'healthcare_agent_phone': '123-456-7890',
    'healthcare_agent_email': 'jane.doe@example.com',
    'want_cpr': 'yes',
    'want_mechanical_ventilation': 'no',
    'want_feeding_tube': 'uncertain',
    'personal_values': 'I value my independence and want to be able to communicate with my loved ones.',
    'quality_of_life_definition': 'I want to be able to recognize my family and friends and to be able to feed myself.',
    'witness_1_name': 'John Smith',
    'witness_1_phone': '111-222-3333',
    'witness_2_name': 'Mary Jones',
    'witness_2_phone': '444-555-6666',
    'right_not_to_know_preference': 'agent_receives_info',
    'want_organ_donation': 'yes',
    'organ_donation_types': ['heart', 'lungs'],
    'organ_donation_purpose': ['transplant', 'research'],
    'organ_donation_purpose_details': 'For research purposes only',
    'want_tissue_donation': 'yes',
    'tissue_donation_types': ['skin', 'bone'],
}

# API endpoint
url = "http://127.0.0.1:5000/api/generate-pdf"

# Headers
headers = {
    "Content-Type": "application/json"
}

# Request body
data = {
    "questionnaire_data": sample_questionnaire,
    "document_type": "advanced_directive"
}

# Send POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Print response
print(response.status_code)
print(response.json())
