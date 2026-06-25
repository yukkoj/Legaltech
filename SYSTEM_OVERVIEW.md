# Legal Document Creator - Complete System Overview

## 🎯 What You Have

A **complete web-based legal document generation system** with:
- ✅ Modern, responsive web UI (HTML/CSS/JavaScript)
- ✅ Flask REST API backend (Python)
- ✅ Input validation system
- ✅ Template-based document generation
- ✅ JSON questionnaire storage
- ✅ Document preview and download

## 🚀 Quick Start (3 Steps)

### Step 1: Install Python Dependencies
```bash
pip install -r legal_doc_creator/requirements.txt
```

### Step 2: Start the Server
**Windows:**
```bash
start_ui.bat
```

**Mac/Linux:**
```bash
chmod +x start_ui.sh
./start_ui.sh
```

**Manual (Any OS):**
```bash
cd legal_doc_creator
python app.py
```

### Step 3: Open Browser
Navigate to:
```
http://localhost:5000
```

Done! You now have a working web interface.

## 📋 System Architecture

### Frontend (User-Facing)
```
Web Browser
    ↓
HTML Form (6 tabs)
    ├─ Personal Information
    ├─ Healthcare Agent
    ├─ Treatment Preferences
    ├─ Values & Beliefs
    ├─ Witnesses
    └─ Review & Generate
    ↓
JavaScript (Form Logic & API Calls)
    ↓
Flask API Endpoint
```

### Backend (Processing)
```
Flask API (/api/generate-document)
    ↓
InputEditorAgent (Validates)
    ├─ Completeness
    ├─ Consistency
    ├─ Clarity
    └─ Legal Validity
    ↓
DraftingAgent (Generates)
    ├─ Loads Template
    ├─ Renders with Data
    └─ Returns Document
    ↓
Response to Browser
    └─ Document Preview & Download
```

### Data Flow
```
User Form Input (HTML)
    ↓
JSON Data
    ↓
API Request
    ↓
Validation ✓
    ↓
Save JSON (questionnaire.json)
    ↓
Jinja2 Template Rendering
    ↓
Document Generated
    ↓
Response to UI
    ↓
User Downloads/Copies
```

## 📁 Project Structure

```
Legaltech/
├── legal_doc_creator/
│   ├── app.py                    ← Flask web server
│   ├── requirements.txt           ← Python dependencies
│   ├── templates/
│   │   ├── index.html            ← Main form UI
│   │   └── advance_directive.jinja2  ← Document template
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css         ← Form styling
│   │   └── js/
│   │       └── app.js            ← Form logic
│   ├── input_editor_agent.py     ← Validation
│   ├── drafting_agent.py         ← Document generation
│   ├── template_system.py        ← Template management
│   ├── questionnaires.py         ← Data models
│   └── output/                   ← Generated files
│       ├── questionnaire_*.json
│       └── advance_directive_*.txt
├── start_ui.bat                  ← Windows launcher
├── start_ui.sh                   ← Mac/Linux launcher
├── README.md                     ← Project overview
├── ARCHITECTURE.md               ← System design
├── RUNNING_UI.md                 ← Setup guide
└── WEB_UI_SUMMARY.md             ← UI summary
```

## 🔌 API Reference

### Generate Document
**Endpoint:** `POST /api/generate-document`

**Request Body:**
```json
{
  "full_name": "John Smith",
  "date_of_birth": "1950-01-15",
  "state_of_residence": "California",
  "healthcare_agent_name": "Jane Smith",
  "healthcare_agent_relationship": "Daughter",
  "healthcare_agent_phone": "(555) 123-4567",
  "healthcare_agent_email": "jane@email.com",
  "want_cpr": "yes",
  "want_mechanical_ventilation": "no",
  "want_feeding_tube": "only_if_recovery",
  "want_antibiotics": "yes",
  "personal_values": "Family, independence, dignity",
  "quality_of_life_definition": "Able to spend time with loved ones",
  "witness_1_name": "Bob Johnson",
  "witness_1_phone": "(555) 234-5678",
  "witness_2_name": "Alice Brown",
  "witness_2_phone": "(555) 345-6789",
  "notary_required": true
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "document": "[Full document text]",
  "document_file": "legal_doc_creator/output/advance_directive_draft.txt",
  "questionnaire_file": "legal_doc_creator/output/questionnaire_20240609_120000.json",
  "message": "Document generated successfully"
}
```

**Validation Error (400):**
```json
{
  "status": "validation_failed",
  "issues": [
    "Missing required field: full_name",
    "Witness cannot be healthcare agent"
  ],
  "suggestions": [
    "Consider notarization for interstate validity"
  ]
}
```

### Validate Questionnaire
**Endpoint:** `POST /api/validate-questionnaire`

Returns validation results WITHOUT generating document. Useful for checking data before generation.

### Get States
**Endpoint:** `GET /api/states`

Returns list of US states for form dropdown.

### Health Check
**Endpoint:** `GET /api/health`

Simple health check for monitoring.

## 🎨 User Interface

### Form Layout
The form is organized into 6 easy-to-navigate tabs:

1. **Personal Information** (3 fields)
   - Full Legal Name *
   - Date of Birth *
   - State of Residence *

2. **Healthcare Agent** (7 fields)
   - Primary Agent Info *
   - Alternate Agent Info (optional)

3. **Treatment Preferences** (10 fields)
   - CPR, Ventilation, Feeding Tube, etc.
   - Pain Management Priority

4. **Values & Beliefs** (9 fields)
   - Personal Values *
   - Quality of Life Definition
   - Religious/Cultural Considerations
   - Organ Donation

5. **Witnesses** (5 fields)
   - Witness 1 *
   - Witness 2 *
   - Notarization Preference

6. **Review & Generate** (2 buttons)
   - Validate Input
   - Generate Document

### Validation Features
- Real-time feedback on input issues
- Checks for missing required fields
- Validates logical consistency (no duplicate witnesses, etc.)
- Suggests improvements (state-specific requirements)
- Shows success when ready to generate

### Document Output
- Preview in browser before downloading
- Copy to clipboard option
- Download as .txt file
- Questionnaire saved as .json for future editing

## ✨ Key Capabilities

✅ **Input Validation**
   - Completeness checking
   - Consistency validation
   - Legal requirement verification
   - User-friendly error messages

✅ **Document Generation**
   - Template-based rendering
   - Data-driven customization
   - Conditional content inclusion
   - Professional formatting

✅ **Data Management**
   - JSON storage for easy editing
   - Regeneration support (edit JSON, regenerate document)
   - File management (list, download recent files)

✅ **User Experience**
   - Multi-step form (less intimidating)
   - Real-time validation feedback
   - Progress through tabs
   - Document preview
   - Easy download/copy

## 🔧 Customization Guide

### Add Form Fields
Edit `templates/index.html`:
```html
<div class="form-group">
  <label for="newField">New Field Name</label>
  <input type="text" id="newField" name="new_field">
</div>
```

### Modify Document Template
Edit `templates/advanced_directive.jinja2`:
```jinja2
{% if my_field %}
Some content based on {{ my_field }}
{% endif %}
```

### Change Validation Rules
Edit `input_editor_agent.py` - Add methods to InputEditorAgent class

### Customize Styling
Edit `static/css/style.css` - Modify colors, fonts, spacing

### Add New Document Type
1. Create questionnaire class in `questionnaires.py`
2. Create template file in `templates/`
3. Add API endpoint in `app.py`

## 🐛 Troubleshooting

### Port 5000 Already in Use
Change port in `legal_doc_creator/app.py`:
```python
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
```

### Dependencies Not Installed
```bash
pip install --upgrade -r legal_doc_creator/requirements.txt
```

### Template File Not Found
The template is created automatically on first run. If missing:
```bash
cd legal_doc_creator
python -c "from template_system import setup_example_template; setup_example_template()"
```

### Form Won't Submit
Check browser console (F12):
1. Open DevTools (F12)
2. Go to Console tab
3. Look for error messages
4. Check Network tab to see API response

### Document Looks Wrong
Check the template file: `templates/advanced_directive.jinja2`
Make sure variables match form field names (Python snake_case)

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| README.md | Project overview & quick start |
| ARCHITECTURE.md | Detailed system design |
| RUNNING_UI.md | Complete setup & usage guide |
| WEB_UI_SUMMARY.md | UI features & workflow |
| THIS FILE | Complete system overview |

## 🎓 Learning Resources

### Understanding the Flow
1. Read ARCHITECTURE.md to understand layers
2. Look at templates/index.html to see form structure
3. Review static/js/app.js for frontend logic
4. Check app.py for API endpoints
5. See input_editor_agent.py for validation
6. View drafting_agent.py for document generation

### Modifying the System
1. Form changes → Edit templates/index.html
2. Validation changes → Edit input_editor_agent.py
3. Document changes → Edit templates/advanced_directive.jinja2
4. Styling changes → Edit static/css/style.css
5. Logic changes → Edit static/js/app.js or app.py

## 🚀 Next Steps

1. ✅ **Start the server** - Run start_ui.bat or start_ui.sh
2. ✅ **Test the form** - Fill it out with sample data
3. ✅ **Generate a document** - Click Generate Document button
4. ✅ **Review output** - Check questionnaire.json and document
5. 📝 **Customize** - Edit templates/documents to match your needs
6. 🎨 **Brand** - Update colors, header, footer in CSS
7. 🚀 **Deploy** - Set up on production server when ready

## 📞 Support

For setup issues:
1. Check RUNNING_UI.md troubleshooting section
2. Review browser console (F12) for errors
3. Check Flask server logs for API errors
4. Verify Python 3.7+ is installed
5. Confirm all dependencies are installed

## ✅ System Status

- **Backend API**: ✅ Complete
- **Web UI Form**: ✅ Complete
- **Validation System**: ✅ Complete
- **Document Generation**: ✅ Complete
- **File Management**: ✅ Complete
- **Documentation**: ✅ Complete

**Status: READY FOR USE** 🎉

---

**To get started:** Run `start_ui.bat` (Windows) or `./start_ui.sh` (Mac/Linux)
Then open `http://localhost:5000` in your browser.
