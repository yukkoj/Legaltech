# Legal Document Creator

This project provides a framework for generating legal documents, specifically an Advanced Directive, through an interactive questionnaire and a multi-agent system.

## Features

*   **Interactive Questionnaire**: Guides the user through collecting necessary information for an Advanced Directive.
*   **Input Validation**: An `InputEditorAgent` reviews the user's data for completeness, consistency, and legal validity before drafting.
*   **Template-based Drafting**: A `DraftingAgent` uses Jinja2 templates to generate the final document from the validated user data.
*   **State-Specific Guidance**: Provides specific options and rules, for example for California residents.
*   **Regeneration**: Allows users to modify their saved questionnaire data and regenerate the document.

## How to Generate a Document

The primary way to generate an Advanced Directive is by running the main orchestrator script, which provides an interactive command-line menu.

### Prerequisites

*   Python 3.x
*   Required libraries. You can install them using pip:
    ```bash
    pip install Jinja2 reportlab
    ```

### Steps

1.  **Navigate to the project directory:**
    Open your terminal or command prompt and navigate to the `Legaltech` root directory.

2.  **Run the Orchestrator:**
    Execute the main orchestrator script from the project's root directory:

    ```bash
    python legal_doc_creator/orchestrator.py
    ```

3.  **Follow the Interactive Menu:**
    You will be presented with a menu:

    ```
    ======================================================================
    LEGAL DOCUMENT CREATOR - ADVANCED DIRECTIVE
    ======================================================================

    1. Create New Advanced Directive
    2. Regenerate from Existing Questionnaire
    3. Exit

    Choose an option (1-3):
    ```

4.  **Create a New Document:**
    *   Enter `1` to start the questionnaire for a new Advanced Directive.
    *   Answer the questions as prompted. The questionnaire will cover personal information, healthcare agents, treatment preferences, and more.

5.  **Review and Generate:**
    *   After you complete the questionnaire, the `InputEditorAgent` will automatically review your answers.
    *   If all checks pass, the document will be generated. If there are issues, you will be notified.

6.  **Find Your Document:**
    *   The final document will be saved as a PDF file in the `legal_doc_creator/output/` directory (e.g., `advanced_directive_draft.pdf`).
    *   Your questionnaire responses will also be saved as a JSON file (`advanced_directive_questionnaire.json`) in the same directory.

### Regenerating a Document

If you want to make changes, you can edit the saved JSON file and regenerate the document without re-doing the entire questionnaire.

1.  Run the orchestrator again: `python legal_doc_creator/orchestrator.py`
2.  Choose option `2` (Regenerate from Existing Questionnaire).
3.  When prompted, provide the path to your JSON file (e.g., `legal_doc_creator/output/advanced_directive_questionnaire.json`).
4.  The system will re-validate the data and generate a new document with your changes.