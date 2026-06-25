# 🚀 QUICK START GUIDE

## In 3 Steps

### 1️⃣ Install
```bash
pip install -r legal_doc_creator/requirements.txt
```

### 2️⃣ Run
**Windows:**
```bash
start_ui.bat
```

**Mac/Linux:**
```bash
./start_ui.sh
```

**Manual:**
```bash
cd legal_doc_creator
python app.py
```

### 3️⃣ Open Browser
```
http://localhost:5000
```

---

## What You're Getting

### 🎨 User Interface
- **6-Tab Form** - Organized questionnaire
- **Real-Time Validation** - Instant feedback
- **Live Preview** - See document before download
- **1-Click Download** - Export as TXT

### 🔧 Backend System
- **Input Validation** - Checks completeness & consistency
- **Template Rendering** - Jinja2-powered documents
- **JSON Storage** - Editable questionnaire data
- **REST API** - Full document generation endpoints

### 📄 Output Files
- `questionnaire_*.json` - User data (editable)
- `advance_directive_*.txt` - Generated document

---

## File Organization

```
Legaltech/
├── legal_doc_creator/
│   ├── app.py              ← Flask server
│   ├── templates/          ← HTML + templates
│   └── static/             ← CSS + JavaScript
├── start_ui.bat            ← Windows starter
├── start_ui.sh             ← Mac/Linux starter
└── docs/                   ← Documentation
```

---

## Documentation

| Document | What's Inside |
|----------|---------------|
| README.md | Overview & quick start |
| SYSTEM_OVERVIEW.md | Everything about the system |
| ARCHITECTURE.md | Technical design details |
| RUNNING_UI.md | Setup & troubleshooting |
| WEB_UI_SUMMARY.md | UI features explained |

---

## Common Tasks

### Start Server
```bash
start_ui.bat  (Windows)
# or
./start_ui.sh (Mac/Linux)
```

### Change Port
Edit `legal_doc_creator/app.py`:
```python
app.run(host='127.0.0.1', port=5001, debug=True)
```

### Edit Form Fields
Edit `legal_doc_creator/templates/index.html`

### Customize Document
Edit `legal_doc_creator/templates/advance_directive.jinja2`

### Change Styling
Edit `legal_doc_creator/static/css/style.css`

---

## API Endpoints

```
POST /api/generate-document      ← Main endpoint (send form data)
POST /api/validate-questionnaire  ← Validate without generating
GET /api/states                   ← Get US states
GET /api/health                   ← Health check
GET /                             ← Load form UI
```

---

## Form Data Required (*)

- Full Legal Name *
- Date of Birth *
- State of Residence *
- Healthcare Agent Name *
- Healthcare Agent Relationship *
- Personal Values *
- Witness 1 Name *
- Witness 2 Name *

---

## Validation Checks

✓ All required fields filled
✓ No duplicate witnesses
✓ Witnesses ≠ healthcare agent
✓ Reasonable text lengths
✓ Valid date formats
✓ State-specific requirements

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port already in use | Change port in app.py |
| Python not found | Install Python 3.7+ |
| Dependencies missing | Run pip install -r requirements.txt |
| Template not found | Restart app (auto-creates) |
| Form won't submit | Check browser console (F12) |

---

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5 + CSS3 + JavaScript
- **Templates**: Jinja2
- **Data**: JSON

---

## Status

✅ **Complete and Ready to Use**

**Next Step**: Run `start_ui.bat` and open `http://localhost:5000`
