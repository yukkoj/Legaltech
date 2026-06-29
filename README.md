# Legal Document Creator

A web-based platform for generating legal documents through an intuitive user interface and backend document automation. Currently supporting Advance Directives (Living Wills) with a clean, responsive form-based UI.

## Architecture

The system uses a **template-based JSON approach**:
- **Frontend**: Web UI (HTML/CSS/JavaScript) for user input
- **Backend**: Flask API that validates data and generates documents
- **Documents**: Generated from Jinja2 templates using validated questionnaire data

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Features

✅ **Web-Based UI** - Modern, responsive form with multi-step questionnaire
✅ **Real-Time Validation** - Input validation before document generation
✅ **Template-Based Generation** - Documents created from Jinja2 templates
✅ **JSON Data Storage** - Questionnaires saved as JSON for easy editing and regeneration
✅ **Download Documents** - Export generated documents as text and PDF files
✅ **Comprehensive Questionnaire** - Covers personal info, healthcare preferences, values, witnesses

## Quick Start

### Prerequisites
- Python 3.7+
- pip

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r legal_doc_creator/requirements.txt
   ```

2. **Start the Flask server:**
   ```bash
   cd legal_doc_creator
   python app.py
   ```

3. **Open in browser:**
   ```
   http://localhost:5000
   ```

4. **Fill out the questionnaire** across 6 tabs:
   - Personal Information
   - Healthcare Agent
   - Treatment Preferences
   - Values & Beliefs
   - Witnesses
   - Review & Generate
  
5. **Click "Validate Input"** for LLM validation

6. **Click "Generate Document"** to create your Advance Directive

7. **Download or copy** the generated document

See [RUNNING_UI.md](RUNNING_UI.md) for detailed setup and troubleshooting.

## Project Structure

```
legal_doc_creator/
├── app.py                     ← Flask web server
├── templates/
│   └── index.html             ← Web form UI
├── static/
│   ├── css/style.css         ← Styling
│   └── js/app.js             ← Frontend logic
├── input_editor_agent.py      ← Data validation
├── drafting_agent.py          ← Document generation
├── template_system.py         ← Template management
├── questionnaires.py          ← Data models
├── orchestrator.py            ← Workflow coordination
├── output/                    ← Generated documents
└── requirements.txt
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Serve main form UI |
| POST | `/api/generate-document` | Validate & generate document |
| POST | `/api/validate-questionnaire` | Validate questionnaire only |
| GET | `/api/states` | Get list of US states |
| GET | `/api/health` | Health check |

## How It Works

1. **User fills form** in web UI (6 tabs)
2. **JavaScript collects** form data
3. **Flask API receives** JSON questionnaire
4. **InputEditorAgent validates** data (checks completeness, consistency, legal validity)
5. **If valid**: questionnaire saved as JSON, DraftingAgent renders template
6. **Document returned** to UI for download/copy
7. **User edits** questionnaire JSON if needed, regenerates document

## Generating Documents

### Web UI (Recommended)
```bash
cd legal_doc_creator
python app.py
# Then open http://localhost:5000
```

### Command Line (Alternative)
```bash
cd legal_doc_creator
python orchestrator.py
# Follow interactive menu
```

### Programmatic (Python)
```python
from legal_doc_creator.orchestrator import DocumentOrchestrator

orchestrator = DocumentOrchestrator()
result = orchestrator.create_advanced_directive(interactive=False)
# Pass questionnaire data directly
```

## Document Types Supported

- **Advanced Directive** (Living Will) - Complete support
  - Healthcare agent designation
  - Life-sustaining treatment preferences
  - Personal values and beliefs
  - Organ donation
  - Witness signatures

## Validation Features

The Input Editor Agent validates:
- ✓ All required fields are present
- ✓ Data is logically consistent
- ✓ Text entries are reasonable length
- ✓ Dates are in valid format
- ✓ Legal requirements met (2 witnesses, etc.)
- ✓ No conflicts (witnesses ≠ healthcare agent, etc.)

## Customization

### Add Form Fields
Edit `templates/index.html`

### Customize Document Template
Edit `templates/advanced_directive.jinja2`

### Change Styling
Edit `static/css/style.css`

### Modify Validation Rules
Edit `input_editor_agent.py`

### Add New Document Types
1. Create new template in `templates/`
2. Add new questionnaire class in `questionnaires.py`
3. Add API endpoint in `app.py`

## File Outputs

Generated files are saved to `output/`:
- `questionnaire_YYYYMMDD_HHMMSS.json` - User questionnaire data
- `advanced_directive_draft.txt` - Generated document

## Technologies

- **Backend**: Flask (Python web framework)
- **Templates**: Jinja2 (template engine)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Data**: JSON for questionnaire storage
- **Validation**: Custom Python validation agents

## License

See LICENSE file for details.

## Support & Documentation

- **Setup Guide**: See [RUNNING_UI.md](RUNNING_UI.md)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Legal Disclaimer**: Consult with an attorney for legal advice
    LEGAL DOCUMENT CREATOR - ADVANCED DIRECTIVE
    ======================================================================
    
    1. Create New Advanced Directive
    2. Regenerate from Existing Questionnaire
    3. Exit
    
    Choose an option (1-3):
    ```

3.  **Complete the Questionnaire and Find Your Document:**
    Answer the questions as prompted. After you finish, the system will automatically review your answers and generate the document.
    *   **Document Location:** `output/advanced_directive_draft.pdf`
    *   **Data File:** `output/advanced_directive_questionnaire.json`

### Regenerating a Document

If you want to make changes, you can edit the saved JSON file and regenerate the document without re-doing the entire questionnaire.

1.  Run the orchestrator again: `python legal_doc_creator/orchestrator.py`
2.  Choose option `2` (Regenerate from Existing Questionnaire).
3.  When prompted, provide the path to your JSON file (e.g., `output/advanced_directive_questionnaire.json`).
4.  The system will re-validate the data and generate a new document with your changes.
