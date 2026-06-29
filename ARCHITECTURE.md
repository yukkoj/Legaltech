# Legal Document Creator - Architecture & Workflow Guide

## Overview

This document outlines the recommended architecture for your legal document creation system using a **template-based approach with JSON data**.

## Key Principle: Separation of Concerns

```
User Input (JSON) → Validation → Template Rendering → Document
                    ↑ Editor     ↑ Drafter         
                  (Data)      (Presentation)
```

---

## Architecture Layers

### Layer 1: Data Collection & Validation (INPUT LAYER)

**Components:**
- `questionnaires.py` - Interactive questionnaire collection
- `input_editor_agent.py` - Input validation and refinement

**Responsibility:** Ensure questionnaire data is complete, consistent, and legally valid

**Agent Role:**
- Checks for missing fields
- Validates logical consistency (e.g., witness ≠ healthcare agent)
- Suggests improvements (not requirements)
- Flags incomplete responses

**Output:** Validated questionnaire data (dictionary/JSON)

### Layer 2: Data Storage (JSON FORMAT)

**Components:**
- Saved as JSON files in `output/` directory

**Why JSON?**
- ✅ Structured and parseable
- ✅ Easy to version control
- ✅ Language agnostic
- ✅ Can be edited directly if needed
- ✅ Easy to debug and validate
- ✅ Supports conditional logic in templates

**Example:**
```json
{
  "full_name": "John Smith",
  "date_of_birth": "01/15/1950",
  "healthcare_agent_name": "Jane Smith",
  "want_cpr": "yes",
  "personal_values": "Family, dignity, independence"
}
```

### Layer 3: Template System (PRESENTATION LAYER)

**Components:**
- `template_system.py` - Template management and rendering
- `templates/` - Jinja2 templates

**Technology:** Jinja2 templating engine

**Responsibility:** Pure data-to-document transformation

**Template Features:**
- Variable substitution: `{{ full_name }}`
- Conditional sections: `{% if want_organ_donation == 'yes' %}`
- Filters: `{{ name | capitalize_words }}`
- Loops: `{% for item in list %}`

**Benefits:**
- ✅ Reusable across documents
- ✅ Easy to maintain
- ✅ No conditional logic in code
- ✅ Non-programmers can edit templates

### Layer 4: Document Generation (DRAFTING LAYER)

**Components:**
- `drafting_agent.py` - Document rendering and output

**Responsibility:** Technical rendering only

**Process:**
1. Load template
2. Pass JSON data to template engine
3. Return rendered document
4. Save to file

---

## Complete Workflow

### Step 1: COLLECT
```
User fills questionnaire interactively
    ↓
AdvancedDirectiveQuestionnaireFlow.run_interactive()
    ↓
Returns: AdvancedDirectiveQuestionnaire dataclass
    ↓
Convert to: dictionary/JSON
```

### Step 2: VALIDATE (INPUT EDITOR AGENT)
```
InputEditorAgent.review_input(questionnaire_data)
    ↓
Checks:
  • Completeness (all required fields)
  • Consistency (no logical contradictions)
  • Clarity (reasonable text length, date formats)
  • Legal validity (state requirements, witness rules)
    ↓
Returns:
  • Issues list (blocks drafting)
  • Suggestions list (optional improvements)
  • Ready to draft? (boolean)
```

### Step 3: SAVE AS JSON
```
questionnaire_data (dict)
    ↓
json.dump() → advanced_directive_questionnaire.json
    ↓
User can edit JSON if needed
```

### Step 4: DRAFT (DRAFTING AGENT)
```
DraftingAgent.generate_advanced_directive(questionnaire_data)
    ↓
1. Load template: advanced_directive.jinja2
2. TemplateManager.render_template(template_name, questionnaire_data)
3. Jinja2 renders: {{ variables }} filled in
    ↓
Returns: Formatted document text
    ↓
Save to: output/advanced_directive_draft.pdf
```

### Step 5: READY FOR USER REVIEW
```
User reviews:
  • Generated document
  • Questionnaire data (JSON)
    
If changes needed:
  • Edit questionnaire JSON OR
  • Run orchestrator.reload_and_regenerate(json_file)
    ↓
Document auto-updates with new data
```

---

## Key Design Decisions

### 1. Why JSON for Questionnaire Data?

| Feature | Benefit |
|---------|---------|
| Structured | Can validate schema |
| Parseable | Easy for tools/scripts |
| Editable | Users can tweak JSON directly |
| Versionable | Track changes in Git |
| Reusable | Same data, different templates |
| Debuggable | Can inspect exact values |

### 2. Why Jinja2 Templates?

| Feature | Benefit |
|---------|---------|
| Simple syntax | `{{ field }}` |
| Conditionals | {% if %} blocks |
| Loops | {% for %} iteration |
| Filters | `{{ date | format }}` |
| No code needed | Lawyers can edit templates |
| Widely used | Large community |

### 3. Why Separate Input Editor from Document Editor?

**Old Approach (Don't Do):**
```
Questionnaire → Draft → Edit (polish wording) → Final
                        ↑ Edits content & structure
               (Problem: Mixes data validation with document refinement)
```

**New Approach (Recommended):**
```
Questionnaire → InputEditor (validate data) → JSON 
                                               ↓
                                          Template
                                               ↓
                                         Document
                                               ↑
                              (User edits INPUT, not output)
```

**Advantages:**
- ✅ Clear responsibility boundaries
- ✅ Input editor focuses on data quality only
- ✅ Prevents inconsistent document regeneration
- ✅ Easy to run multiple times
- ✅ Audit trail (JSON shows what user provided)

---

## File Structure

```
legal_doc_creator/
├── questionnaires.py          # User questionnaire collection
├── input_editor_agent.py      # Input validation & refinement
├── template_system.py         # Template management & rendering
├── drafting_agent.py          # Document generation
├── orchestrator.py            # Main workflow coordinator
├── templates/
│   ├── advanced_directive.jinja2
│   └── [other_templates].jinja2
├── output/
│   ├── advanced_directive_questionnaire.json
│   └── advanced_directive_draft.txt
└── agents/                    # (Optional) Keep existing agents for legacy features
    ├── base_agent.py
    ├── drafting_agent.py      # (Old - can deprecate)
    └── editing_agent.py       # (Old - can deprecate)
```

---

## Usage Examples

### Simple: Run Complete Workflow
```python
from legal_doc_creator.orchestrator import DocumentOrchestrator

orchestrator = DocumentOrchestrator()
result = orchestrator.create_advanced_directive(interactive=True)

# Result contains:
# - questionnaire_data: dict of user responses
# - document: rendered document text
# - document_file: path to saved .txt file
# - questionnaire_file: path to saved .json file
```

### Advanced: Programmatic Control
```python
from legal_doc_creator.questionnaires import AdvancedDirectiveQuestionnaireFlow
from legal_doc_creator.input_editor_agent import InputEditorWorkflow
from legal_doc_creator.drafting_agent import RefinedDraftingWorkflow

# Step 1: Collect (interactive)
flow = AdvancedDirectiveQuestionnaireFlow()
responses = flow.run_interactive()
data = responses.to_dict()

# Step 2: Validate input
editor = InputEditorWorkflow()
is_valid, review = editor.review_and_request_changes(data)

if not is_valid:
    print("Fix issues:", review['issues_found'])
    # User fixes JSON manually
    # Reload and try again

# Step 3: Generate document
draft_workflow = RefinedDraftingWorkflow()
result = draft_workflow.generate_from_questionnaire(data)
print(result['document'])
```

### Regenerate with Updated Data
```python
orchestrator = DocumentOrchestrator()

# User edits the JSON file
result = orchestrator.reload_and_regenerate(
    "legal_doc_creator/output/advanced_directive_questionnaire.json"
)
# Document automatically regenerates with updated data
```

---

## Template Example (Jinja2)

```jinja2
{# Advanced Directive Template #}
ADVANCE DIRECTIVE FOR HEALTH CARE
STATE OF {{ state_of_residence | upper }}

I, {{ full_name }}, being of sound mind, execute this Advance Directive.

HEALTHCARE AGENT: {{ healthcare_agent_name }} ({{ healthcare_agent_relationship }})
Phone: {{ healthcare_agent_phone }}

LIFE-SUSTAINING TREATMENT:
- CPR: {{ want_cpr | yesno }}
- Mechanical Ventilation: {{ want_mechanical_ventilation | yesno }}
- Feeding Tube: {{ want_feeding_tube | yesno }}

{% if personal_values %}
WHAT MATTERS MOST TO ME:
{{ personal_values }}
{% endif %}

{% if want_organ_donation == 'yes' %}
ORGAN DONATION:
I wish to donate: {{ organ_donation_types | join(', ') }}
{% endif %}

WITNESSES:
1. {{ witness_1_name }} - {{ witness_1_phone }}
2. {{ witness_2_name }} - {{ witness_2_phone }}
```

---

## Validation Workflow (Input Editor)

```
COMPLETENESS CHECK
└─ All required fields present and non-empty
   └─ FAIL: "Missing required field: healthcare_agent_name"
   └─ PASS: Continue

CONSISTENCY CHECK
└─ Data logically consistent
   └─ Witness ≠ Healthcare Agent
   └─ If organ_donation=yes → organ_donation_types filled
   └─ Two witnesses ≠ each other
   └─ FAIL: "Witness cannot be healthcare agent"
   └─ PASS: Continue

CLARITY CHECK
└─ Text is reasonable length
   └─ Dates are valid format
   └─ Personal values not blank
   └─ FAIL: "Date format invalid"
   └─ PASS: Continue

LEGAL VALIDITY CHECK
└─ Meets legal requirements
   └─ State-specific witness requirements
   └─ Notary recommendations
   └─ Age verification (DOB provided)
   └─ FAIL: "Most states require 2 witnesses"
   └─ PASS: Continue

READY TO DRAFT: YES/NO
```

---

## Future Enhancements

1. **Template Versioning**
   - Track template changes
   - Regenerate old documents with current template

2. **Multi-Language Support**
   - Create templates in Spanish, etc.
   - Switch based on user preference

3. **State-Specific Templates**
   - advanced_directive_ca.jinja2
   - advanced_directive_ny.jinja2

4. **Export Formats**
   - PDF generation (with styling)
   - DOCX for further editing
   - HTML for web viewing

5. **Validation Enhancement**
   - Gemini API to validate legal language quality
   - Compliance checking against state laws

6. **Data Import/Export**
   - Import from CSV for bulk processing
   - Export data with documents

---

## Summary

✅ **Use JSON** for questionnaire data - structured, editable, reusable
✅ **Use Jinja2 templates** - powerful, maintainable, non-programmer friendly
✅ **Separate concerns** - Input validation vs. Document rendering
✅ **Edit INPUT, not OUTPUT** - Changes trigger regeneration, not manual fixes
✅ **Template-driven** - Single source of truth for document structure
