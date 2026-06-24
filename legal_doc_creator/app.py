"""
Flask API Backend for Legal Document Creator
Handles questionnaire submission, validation, and document generation
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from pathlib import Path
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import internal modules
try:
    from input_editor_agent import InputEditorWorkflow
    from drafting_agent import RefinedDraftingWorkflow
    from template_system import setup_example_template
    from pdf_generator import generate_pdf_from_document
except ImportError:
    from legal_doc_creator.input_editor_agent import InputEditorWorkflow
    from legal_doc_creator.drafting_agent import RefinedDraftingWorkflow
    from legal_doc_creator.template_system import setup_example_template
    from legal_doc_creator.pdf_generator import generate_pdf_from_document

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Initialize workflows
input_editor_workflow = InputEditorWorkflow()
drafting_workflow = RefinedDraftingWorkflow()

# Output directory
OUTPUT_DIR = Path("legal_doc_creator/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Ensure template exists on startup
try:
    setup_example_template()
    logger.info("Template system initialized")
except Exception as e:
    logger.warning(f"Could not initialize template: {e}")


@app.route('/')
def index():
    """Serve the main questionnaire form"""
    return render_template('index.html')


@app.route('/api/states', methods=['GET'])
def get_states():
    """Return list of US states for dropdown"""
    states = ['California']
    return jsonify(states)


@app.route('/api/validate-questionnaire', methods=['POST'])
def validate_questionnaire():
    """
    Validate questionnaire data
    Returns validation results but doesn't generate document yet
    """
    try:
        data = request.get_json()
        
        # Validate using InputEditorAgent
        review_result = input_editor_workflow.editor.review_input(data, 'advanced_directive')
        
        return jsonify({
            'status': 'success',
            'is_valid': review_result['is_ready_to_draft'],
            'issues': review_result['issues_found'],
            'suggestions': review_result['suggestions']
        })
    
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return jsonify({
            'status': 'error',
            'error_message': str(e)
        }), 400


@app.route('/api/generate-document', methods=['POST'])
def generate_document():
    """
    Generate Advanced Directive document from questionnaire data
    Endpoint: POST /api/generate-document
    Body: JSON questionnaire data
    Returns: Document text + metadata
    """
    try:
        data = request.get_json()
        
        # Step 1: Generate document
        result = drafting_workflow.generate_from_questionnaire(
            data,
            document_type='advanced_directive',
            save_to_file=True
        )
        
        if result.get('status') != 'success':
            return jsonify({
                'status': 'error',
                'error_message': result.get('error_message', 'Document generation failed')
            }), 500
        
        # Step 2: Return success response
        return jsonify({
            'status': 'success',
            'document': result.get('document'),
            'document_file': result.get('file_path'),
            'questionnaire_file': result.get('json_file'),
            'message': 'Document generated successfully'
        })
    
    except Exception as e:
        logger.error(f"Document generation error: {e}")
        return jsonify({
            'status': 'error',
            'error_message': str(e)
        }), 500


@app.route('/api/save-questionnaire', methods=['POST'])
def save_questionnaire():
    """
    Save current questionnaire progress to a JSON file on the server.
    """
    try:
        data = request.get_json()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"questionnaire_progress_{timestamp}.json"
        json_filepath = OUTPUT_DIR / json_filename
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Questionnaire progress saved: {json_filepath}")
        
        return jsonify({
            'status': 'success',
            'message': f'Progress saved to {json_filename} on the server.',
            'filename': json_filename
        })
    
    except Exception as e:
        logger.error(f"Save questionnaire error: {e}")
        return jsonify({
            'status': 'error',
            'error_message': str(e)
        }), 500


@app.route('/api/download-document/<filename>', methods=['GET'])
def download_document(filename):
    """
    Download generated document file
    """
    try:
        return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': str(e)}), 404


@app.route('/api/download-questionnaire/<filename>', methods=['GET'])
def download_questionnaire(filename):
    """
    Download questionnaire JSON file
    """
    try:
        return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': str(e)}), 404


@app.route('/api/recent-files', methods=['GET'])
def recent_files():
    """
    Get list of recently generated files
    """
    try:
        files = []
        
        # Get all files in output directory
        for filepath in OUTPUT_DIR.glob('*'):
            if filepath.is_file():
                files.append({
                    'name': filepath.name,
                    'size': filepath.stat().st_size,
                    'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                    'type': 'questionnaire' if filepath.suffix == '.json' else 'document'
                })
        
        # Sort by modification time, newest first
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'files': files[:20]  # Return last 20 files
        })
    
    except Exception as e:
        logger.error(f"File listing error: {e}")
        return jsonify({
            'status': 'error',
            'error_message': str(e)
        }), 500


@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Generate PDF from questionnaire data or document text
    Endpoint: POST /api/generate-pdf
    Body: JSON with either 'questionnaire_data' or 'document_text'
    Returns: PDF file path
    """
    try:
        data = request.get_json()
        logger.info(f"Received request to generate PDF with data: {data}")
        
        if not data or ('questionnaire_data' not in data and 'document_text' not in data):
            logger.error("No questionnaire_data or document_text provided")
            return jsonify({
                'status': 'error',
                'error_message': 'No questionnaire_data or document_text provided'
            }), 400

        document_text = data.get("document_text")
        questionnaire_data = data.get('questionnaire_data', {})
        full_name = questionnaire_data.get('full_name')

        # If document_text is not provided, generate it from questionnaire_data
        if not document_text:
            
            logger.info("Generating document text from questionnaire...")
            # Generate document text using the drafting workflow
            draft_result = drafting_workflow.generate_from_questionnaire(
                questionnaire_data,
                document_type=data.get('document_type', 'advanced_directive'),
                save_to_file=False  # We just need the text
            )

            if draft_result.get('status') != 'success':
                logger.error(f"Failed to generate document text: {draft_result.get('error_message')}")
                return jsonify({
                    'status': 'error',
                    'error_message': draft_result.get('error_message', 'Failed to generate document text for PDF conversion')
                }), 500
            
            document_text = draft_result.get('document')
            logger.info("Document text generated successfully.")

        logger.info(f"Generating PDF from document text...")
        # Generate PDF from the final document text
        success, message, pdf_path = generate_pdf_from_document(
            document_text,
            OUTPUT_DIR,
            title=data.get('document_type', 'advanced_directive').replace('_', ' ').title(),
            full_name=full_name
        )
        
        if success:
            logger.info(f"PDF generated successfully: {pdf_path}")
            return jsonify({
                'status': 'success',
                'pdf_file': Path(pdf_path).name,
                'pdf_path': str(pdf_path),
                'message': message
            })
        else:
            logger.error(f"PDF generation failed: {message}")
            return jsonify({
                'status': 'error',
                'error_message': message
            }), 500
    
    except Exception as e:
        logger.error(f"PDF generation error: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error_message': str(e)
        }), 500


@app.route('/api/download-pdf/<filename>', methods=['GET'])
def download_pdf(filename):
    """
    Download generated PDF file
    """
    try:
        return send_from_directory(OUTPUT_DIR, filename, as_attachment=True, mimetype='application/pdf')
    except Exception as e:
        logger.error(f"PDF download error: {e}")
        return jsonify({'error': str(e)}), 404


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Legal Document Creator API',
        'timestamp': datetime.now().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("Starting Legal Document Creator API...")
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )
