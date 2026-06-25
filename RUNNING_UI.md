# Running the Web-Based UI

This guide explains how to run the Advance Directive Creator with the web-based UI.

## Setup

### 1. Install Dependencies

```bash
pip install -r legal_doc_creator/requirements.txt
```

This installs:
- Flask (web framework)
- Jinja2 (template engine)
- python-dotenv (environment variables)

### 2. Verify Template System is Set Up

The system automatically creates the template if it doesn't exist. Check that these files exist:
- `legal_doc_creator/template_system.py`
- `legal_doc_creator/templates/advance_directive.jinja2` (auto-created on first run)

### 3. Start the Flask Server

```bash
cd legal_doc_creator
python app.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 4. Open the Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

## Workflow

### User Interface Flow

1. **Personal Information Tab**
   - Fill in name, DOB, state of residence

2. **Healthcare Agent Tab**
   - Designate primary and alternate healthcare agents
   - Add contact information

3. **Treatment Preferences Tab**
   - Indicate preferences for life-sustaining treatments
   - Answer condition-specific questions
   - Set pain management priorities

4. **Values & Beliefs Tab**
   - Describe what matters most to you
   - Add religious/cultural considerations
   - Indicate organ donation wishes

5. **Witnesses Tab**
   - Add witness information (required)
   - Indicate notarization preference

6. **Review & Generate Tab**
   - Click "Validate Input" to check for issues
   - Click "Generate Document" to create the Advance Directive
   - Download or copy the document

### Data Flow (Backend)

```
Web Form (HTML)
    ↓
JavaScript (app.js) - Collects form data
    ↓
Flask API (app.py) - Receives JSON data
    ↓
InputEditorAgent - Validates questionnaire data
    ↓
If valid:
    - Save questionnaire as JSON
    - DraftingAgent renders template
    - Return document to UI
    ↓
JavaScript - Display document in UI
    ↓
User - Download or copy document
```

## API Endpoints

### POST /api/validate-questionnaire
Validates questionnaire data without generating document
- **Request**: JSON questionnaire data
- **Response**: Validation results (issues, suggestions, is_valid)

### POST /api/generate-document
Validates and generates Advance Directive document
- **Request**: JSON questionnaire data
- **Response**: Document text + metadata

### GET /api/states
Get list of US states for dropdown
- **Request**: None
- **Response**: Array of state names

### GET /api/health
Health check endpoint
- **Request**: None
- **Response**: Service status

## File Outputs

Generated files are saved in `legal_doc_creator/output/`:

- `questionnaire_YYYYMMDD_HHMMSS.json` - User questionnaire data
- `advance_directive_draft.txt` - Generated document

You can download these files from the UI or access them directly from the output folder.

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify `app.py`:
```python
app.run(host='127.0.0.1', port=5001, debug=True)
```

### Template Not Found Error
The template is auto-created on first use. If missing, run:
```python
from legal_doc_creator.template_system import setup_example_template
setup_example_template()
```

### Validation Errors
Check that:
- All required fields are filled (marked with *)
- Healthcare agent and witnesses are different people
- State of residence is selected
- Date of birth is in valid format

### Form Doesn't Submit
Check browser console for JavaScript errors:
1. Open DevTools (F12)
2. Go to Console tab
3. Look for any red error messages

## Development

### Enable/Disable Debug Mode
In `app.py`, change debug setting:
```python
app.run(debug=False)  # Production
app.run(debug=True)   # Development (auto-reload)
```

### Modify Form Fields
Edit `templates/index.html` to add/remove form fields

### Customize Styling
Edit `static/css/style.css`

### Customize Frontend Logic
Edit `static/js/app.js`

### Customize Validation Rules
Edit `legal_doc_creator/input_editor_agent.py`

### Customize Document Template
Edit `legal_doc_creator/templates/advance_directive.jinja2`

## Architecture

```
legal_doc_creator/
├── app.py                          ← Flask web server
├── templates/
│   └── index.html                  ← Web form UI
├── static/
│   ├── css/style.css              ← Styling
│   └── js/app.js                  ← Frontend logic
├── input_editor_agent.py           ← Validation backend
├── drafting_agent.py               ← Document generation
├── template_system.py              ← Template management
├── questionnaires.py               ← Data models
├── orchestrator.py                 ← Workflow coordination
└── output/                         ← Generated files
    ├── questionnaire_*.json
    └── advance_directive_*.txt
```

## Next Steps

1. **Customize Templates**
   - Edit `legal_doc_creator/templates/advanced_directive.jinja2` for document content
   - Add state-specific variations

2. **Add More Document Types**
   - Create new questionnaires
   - Add new templates
   - Register in API endpoints

3. **Enhance Validation**
   - Add state-specific requirements
   - Add legal compliance checks
   - Integrate with legal databases

4. **Deploy to Production**
   - Use gunicorn instead of Flask dev server
   - Set up HTTPS
   - Add authentication if needed
   - Deploy to cloud (Heroku, AWS, Azure, etc.)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review browser console (F12)
3. Check Flask server logs
4. Review code comments in `app.py` and `static/js/app.js`
