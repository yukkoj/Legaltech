# Legaltech

Advanced legal document automation using multi-agent AI.

## Projects

### Legal Document Creator
A Python framework for creating and refining legal documents using multiple AI agents. One agent drafts the document based on requirements, while another reviews and edits it for improvement.

#### Quick Start

```bash
cd legal_doc_creator
pip install -r requirements.txt
```

Set your GEmini API key in `.env`:
```
GEMINI_API_KEY=...
```

#### Basic Usage

```python
from orchestrator import DocumentOrchestrator
from models.document import LegalDocument

orchestrator = DocumentOrchestrator(num_edit_passes=1)

document = LegalDocument(
    id="doc_001",
    document_type="Service Agreement",
    requirements="Your requirements here..."
)

result = orchestrator.create_document(document)
orchestrator.save_document(result)
```

#### Architecture

- **DraftingAgent** - Creates initial legal documents from requirements
- **EditingAgent** - Reviews and improves documents with feedback
- **DocumentOrchestrator** - Coordinates multi-agent pipeline
- **LegalDocument** - Tracks revisions and version history

See `legal_doc_creator/` for full framework documentation and examples.
