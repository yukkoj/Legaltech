/**
 * Advanced Directive Form - Frontend JavaScript
 * Handles form navigation, validation, and API communication
 */

const API_BASE = '/api';
let currentTab = 'personal';
const allTabs = ['personal', 'healthcare', 'treatment', 'values', 'witnesses', 'review'];
let generatedDocument = null;
let currentQuestionnaireData = null;

// Tab Management
class TabManager {
    static show(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(el => {
            el.classList.remove('active');
        });
        document.querySelectorAll('.tab-button').forEach(el => {
            el.classList.remove('active');
        });

        // Show selected tab
        document.getElementById(tabName).classList.add('active');
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        currentTab = tabName;
        this.updateNavigation();
        window.scrollTo(0, 0);
    }

    static next() {
        const currentIndex = allTabs.indexOf(currentTab);
        if (currentIndex < allTabs.length - 1) {
            this.show(allTabs[currentIndex + 1]);
        }
    }

    static prev() {
        const currentIndex = allTabs.indexOf(currentTab);
        if (currentIndex > 0) {
            this.show(allTabs[currentIndex - 1]);
        }
    }

    static updateNavigation() {
        const currentIndex = allTabs.indexOf(currentTab);
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');

        // Show/hide prev button
        if (currentIndex === 0) {
            prevBtn.style.display = 'none';
        } else {
            prevBtn.style.display = 'block';
        }

        // Update next button
        if (currentIndex === allTabs.length - 1) {
            nextBtn.textContent = 'Done';
            nextBtn.disabled = false;
            nextBtn.style.pointerEvents = 'auto';
        } else {
            nextBtn.textContent = 'Next';
            nextBtn.disabled = false;
        }
    }
}

// API Communication
class DocumentAPI {
    static async getStates() {
        try {
            const response = await fetch(`${API_BASE}/states`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching states:', error);
            return [];
        }
    }

    static async validateQuestionnaire(formData) {
        try {
            const response = await fetch(`${API_BASE}/validate-questionnaire`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`Validation failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Validation error:', error);
            return {
                status: 'error',
                error_message: error.message
            };
        }
    }

    static async generateDocument(formData) {
        try {
            const response = await fetch(`${API_BASE}/generate-document`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error_message || `Generation failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Generation error:', error);
            return {
                status: 'error',
                error_message: error.message
            };
        }
    }

    static async generatePdf(payload) {
        try {
            const response = await fetch(`${API_BASE}/generate-pdf`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error_message || `PDF generation failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('PDF generation error:', error);
            return {
                status: 'error',
                error_message: error.message
            };
        }
    }

    static async saveQuestionnaire(formData) {
        try {
            const response = await fetch(`${API_BASE}/save-questionnaire`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error_message || `Save failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Save questionnaire error:', error);
            return {
                status: 'error',
                error_message: error.message
            };
        }
    }
}

// Form Utilities
class FormUtils {
    static getFormData() {
        const form = document.getElementById('questionnaireForm');
        const formData = new FormData(form);
        const data = {};

        // Initialize arrays for checkbox groups
        data['organ_donation_types'] = [];
        data['organ_donation_purpose'] = [];

        // Convert FormData to object
        for (let [key, value] of formData.entries()) {
            switch (key) {
                case 'organ_types':
                    data['organ_donation_types'].push(value);
                    break;
                case 'organ_donation_purpose':
                    data['organ_donation_purpose'].push(value);
                    break;
                case 'pain_management_priority':
                case 'accept_medication_side_effects':
                case 'notary_required':
                case 'use_witnesses':
                     data[key] = (value === 'true' || value === 'yes');
                     break;
                default:
                    // For radio buttons or other fields, the last value wins, which is correct.
                    data[key] = value;
                    break;
            }
        }
        
        // Ensure boolean for checkboxes that might not be in formData if unchecked
        const checkboxes = ['pain_management_priority', 'accept_medication_side_effects', 'notary_required', 'use_witnesses'];
        checkboxes.forEach(cb => {
            if (!data.hasOwnProperty(cb)) {
                data[cb] = false;
            }
        });

        // Handle "yes/no" checkboxes for donation
        const yesNoCheckboxes = ['want_organ_donation', 'want_tissue_donation'];
        yesNoCheckboxes.forEach(cb => {
            if (!data.hasOwnProperty(cb)) {
                data[cb] = 'no';
            }
        });

        return data;
    }

    static displayValidationResults(results) {
        const container = document.getElementById('validationResults');
        container.innerHTML = '';

        if (results.status === 'error') {
            container.innerHTML = `
                <div class="validation-item validation-issue">
                    <div>Error: ${results.error_message}</div>
                </div>
            `;
            return;
        }

        // Display issues (errors)
        if (results.issues && results.issues.length > 0) {
            results.issues.forEach(issue => {
                const div = document.createElement('div');
                div.className = 'validation-item validation-issue';
                div.textContent = issue;
                container.appendChild(div);
            });
        }

        // Display suggestions
        if (results.suggestions && results.suggestions.length > 0) {
            results.suggestions.forEach(suggestion => {
                const div = document.createElement('div');
                div.className = 'validation-item validation-suggestion';
                div.textContent = suggestion;
                container.appendChild(div);
            });
        }

        // Display success message
        if (results.is_valid) {
            const div = document.createElement('div');
            div.className = 'validation-item';
            div.style.background = '#d5f4e6';
            div.style.borderLeftColor = '#27ae60';
            div.style.color = '#145a32';
            div.innerHTML = '✅ All validations passed! Ready to generate document.';
            container.appendChild(div);
        }
    }

    static showLoading(message = 'Processing...') {
        const modal = document.getElementById('loadingModal');
        document.getElementById('loadingText').textContent = message;
        modal.style.display = 'flex';
    }

    static hideLoading() {
        document.getElementById('loadingModal').style.display = 'none';
    }

    static displayDocumentResult(result, formData) {
        const resultsDiv = document.getElementById('generationResults');
        const messageDiv = document.getElementById('resultMessage');
        const previewDiv = document.getElementById('documentPreview');
        const contentDiv = document.getElementById('documentContent');

        // Clear previous JSON editor if it exists
        const existingEditor = document.getElementById('jsonEditorContainer');
        if (existingEditor) existingEditor.remove();
        resultsDiv.style.display = 'block';

        if (result.status === 'success') {
            messageDiv.className = 'result-message success';
            messageDiv.textContent = '✅ Document generated successfully!';

            // Display document preview
            contentDiv.textContent = result.document;
            previewDiv.style.display = 'block';

            generatedDocument = result;
            currentQuestionnaireData = formData;

            // Enable download button
            document.getElementById('downloadDocBtn').onclick = () => {
                FormUtils.downloadDocument(result);
            };

            document.getElementById('copyDocBtn').onclick = () => {
                FormUtils.copyToClipboard(result.document);
            };

            // Setup PDF download button
            document.getElementById('downloadPdfBtn').onclick = async () => {
                FormUtils.downloadPDF();
            };

            // Add option to revise JSON
            this.setupJsonEditor(resultsDiv);
        } else if (result.status === 'validation_failed') {
            messageDiv.className = 'result-message error';
            messageDiv.innerHTML = '❌ Validation failed. Please fix the issues below:<br><br>';

            result.issues.forEach(issue => {
                messageDiv.innerHTML += `• ${issue}<br>`;
            });

            previewDiv.style.display = 'none';
        } else {
            messageDiv.className = 'result-message error';
            messageDiv.textContent = `❌ Error: ${result.error_message || 'Unknown error'}`;
            previewDiv.style.display = 'none';
        }
    }

    static setupJsonEditor(container) {
        const editorContainer = document.createElement('div');
        editorContainer.id = 'jsonEditorContainer';
        editorContainer.className = 'json-editor-container';
        editorContainer.style.marginTop = '20px';
        editorContainer.style.borderTop = '1px solid #eee';
        editorContainer.style.paddingTop = '20px';

        editorContainer.innerHTML = `
            <h4 style="margin-bottom: 10px;">Revise Your Answers</h4>
            <p class="section-info" style="margin-bottom: 15px;">You can edit your questionnaire data directly below and regenerate the document.</p>
            <button type="button" id="editJsonBtn" class="btn btn-outline">Edit Questionnaire Data (JSON)</button>
            <div id="jsonEditor" style="display:none; margin-top: 15px;">
                <textarea id="jsonTextarea" style="width: 100%; min-height: 300px; font-family: monospace; padding: 10px; border: 1px solid #ccc; border-radius: 4px;"></textarea>
                <div class="form-actions" style="margin-top: 10px;">
                    <button type="button" id="regenerateJsonBtn" class="btn btn-primary">Regenerate from JSON</button>
                    <button type="button" id="cancelJsonBtn" class="btn btn-secondary">Cancel</button>
                </div>
                <div id="jsonError" class="result-message error" style="display:none; margin-top: 10px;"></div>
            </div>
        `;

        container.appendChild(editorContainer);

        const editJsonBtn = document.getElementById('editJsonBtn');
        const jsonEditorDiv = document.getElementById('jsonEditor');
        const jsonTextarea = document.getElementById('jsonTextarea');
        const regenerateJsonBtn = document.getElementById('regenerateJsonBtn');
        const cancelJsonBtn = document.getElementById('cancelJsonBtn');
        const jsonErrorDiv = document.getElementById('jsonError');

        editJsonBtn.addEventListener('click', () => {
            jsonTextarea.value = JSON.stringify(currentQuestionnaireData, null, 2);
            jsonEditorDiv.style.display = 'block';
            editJsonBtn.style.display = 'none';
        });

        cancelJsonBtn.addEventListener('click', () => {
            jsonEditorDiv.style.display = 'none';
            editJsonBtn.style.display = 'block';
            jsonErrorDiv.style.display = 'none';
        });

        regenerateJsonBtn.addEventListener('click', async () => {
            let updatedData;
            try {
                updatedData = JSON.parse(jsonTextarea.value);
                jsonErrorDiv.style.display = 'none';
            } catch (error) {
                jsonErrorDiv.textContent = `Invalid JSON: ${error.message}`;
                jsonErrorDiv.style.display = 'block';
                return;
            }

            FormUtils.showLoading('Regenerating document from JSON...');
            const result = await DocumentAPI.generateDocument(updatedData);
            FormUtils.hideLoading();

            // The displayDocumentResult function will handle updating the UI,
            // including setting the new currentQuestionnaireData and recreating the editor.
            FormUtils.displayDocumentResult(result, updatedData);
        });
    }

    static downloadDocument(result) {
        const element = document.createElement('a');
        const file = new Blob([result.document], { type: 'text/plain' });
        element.href = URL.createObjectURL(file);
        element.download = `advanced_directive_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    static async downloadPDF() {
        // Show loading indicator
        FormUtils.showLoading('Generating PDF...');
        
        try {
            // Use the questionnaire data that's currently loaded in the form
            if (!currentQuestionnaireData) {
                alert('No questionnaire data found. Please fill out the form or load a saved file.');
                FormUtils.hideLoading();
                return;
            }
            
            // Prepare payload for the API
            const payload = {
                questionnaire_data: currentQuestionnaireData,
                document_type: 'advanced_directive'
            };
            
            // Generate PDF from the document text
            const pdfResult = await DocumentAPI.generatePdf(payload);
            
            FormUtils.hideLoading();
            
            if (pdfResult.status === 'success') {
                // Download the PDF file
                const pdfFilename = pdfResult.pdf_file;
                window.location.href = `${API_BASE}/download-pdf/${pdfFilename}`;
            } else {
                alert(`Error generating PDF: ${pdfResult.error_message || 'Unknown error'}`);
            }
        } catch (error) {
            FormUtils.hideLoading();
            console.error('PDF download error:', error);
            alert(`Failed to generate PDF: ${error.message}`);
        }
    }

    static copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            alert('Document copied to clipboard!');
        }).catch(() => {
            alert('Failed to copy to clipboard');
        });
    }

    static async saveQuestionnaire() {
        const formData = this.getFormData();
        
        FormUtils.showLoading('Saving your progress to the server...');
        const result = await DocumentAPI.saveQuestionnaire(formData);
        FormUtils.hideLoading();

        if (result.status === 'success') {
            alert(`Your form progress has been saved to the server as ${result.filename}.`);
        } else {
            alert(`Error saving progress: ${result.error_message || 'Unknown error'}`);
        }
    }

    static resetForm() {
        if (confirm('Are you sure you want to reset the entire form?')) {
            document.getElementById('questionnaireForm').reset();
            document.getElementById('generationResults').style.display = 'none';
            document.getElementById('validationResults').innerHTML = '';
            TabManager.show('personal');
            alert('Form has been reset.');
        }
    }

    static populateForm(data) {
        const form = document.getElementById('questionnaireForm');
        form.reset(); // Clear the form first

        // Reset conditional fields that reset() might not handle perfectly
        document.getElementById('organDonationTypes').style.display = 'none';
        document.getElementById('organDonationPurpose').style.display = 'none';

        for (const key in data) {
            if (!data.hasOwnProperty(key)) continue;

            const value = data[key];
            const elements = form.querySelectorAll(`[name="${key}"]`);

            if (elements.length === 0) {
                // Handle special cases where key doesn't match a name attribute
                if (key === 'organ_donation_types' && Array.isArray(value)) {
                    value.forEach(organ => {
                        const checkbox = form.querySelector(`input[name="organ_types"][value="${organ}"]`);
                        if (checkbox) checkbox.checked = true;
                    });
                } else if (key === 'organ_donation_purpose' && Array.isArray(value)) {
                    value.forEach(purpose => {
                        const checkbox = form.querySelector(`input[name="organ_donation_purpose"][value="${purpose}"]`);
                        if (checkbox) checkbox.checked = true;
                    });
                }
                continue;
            }

            const el = elements[0];
            const type = el.type;

            if (type === 'radio') {
                const radioToSelect = form.querySelector(`input[name="${key}"][value="${value}"]`);
                if (radioToSelect) radioToSelect.checked = true;
            } else if (type === 'checkbox') {
                // This handles single boolean checkboxes
                if (typeof value === 'boolean') {
                    el.checked = value;
                }
            } else {
                // Handles text, date, select-one, textarea, email, tel
                el.value = value;
            }
        }

        // --- Post-population UI updates ---

        // Trigger change on organ donation checkbox to show/hide specific types
        const organCheckbox = form.querySelector('input[name="want_organ_donation"]');
        if (organCheckbox) {
            organCheckbox.dispatchEvent(new Event('change'));
        }

        // Set signature method checkboxes and trigger change
        const notaryCheckbox = document.getElementById('notaryCheckbox');
        if (notaryCheckbox) {
            notaryCheckbox.checked = !!data.notary_required;
        }

        const useWitnessesCheckbox = document.getElementById('useWitnessesCheckbox');
        if (useWitnessesCheckbox) {
            let shouldUseWitnesses = false;
            if (data.hasOwnProperty('use_witnesses')) {
                shouldUseWitnesses = !!data.use_witnesses;
            } else {
                // Fallback for older JSONs: infer from data presence
                shouldUseWitnesses = !!(data.witness_1_name && data.witness_2_name);
            }
            useWitnessesCheckbox.checked = shouldUseWitnesses;
            useWitnessesCheckbox.dispatchEvent(new Event('change'));
        }
        // Set global data object for later use (e.g., regeneration)
        currentQuestionnaireData = data;

        alert('Form has been populated with data from the JSON file.');
        TabManager.show('personal'); // Go to first tab to start review
    }
}

// Event Listeners Setup
function setupEventListeners() {
    // Tab navigation
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', (e) => {
            TabManager.show(e.target.dataset.tab);
        });
    });

    // Load from JSON button
    document.getElementById('loadJsonBtn').addEventListener('click', () => {
        document.getElementById('jsonFileInput').click();
    });

    document.getElementById('jsonFileInput').addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (!file) {
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const jsonData = JSON.parse(e.target.result);
                FormUtils.populateForm(jsonData);
            } catch (error) {
                alert(`Error parsing JSON file: ${error.message}`);
            }
            // Reset file input value to allow loading the same file again
            event.target.value = '';
        };
        reader.onerror = () => {
            alert('Error reading file.');
        };
        reader.readAsText(file);
    });

    // Next/Previous buttons
    document.getElementById('nextBtn').addEventListener('click', () => {
        const currentIndex = allTabs.indexOf(currentTab);
        if (currentIndex === allTabs.length - 1) {
            // At last tab, do nothing (document generation happens on validate/generate buttons)
        } else {
            TabManager.next();
        }
    });

    document.getElementById('prevBtn').addEventListener('click', () => {
        TabManager.prev();
    });

    // Save button
    document.getElementById('saveBtn').addEventListener('click', async () => {
        await FormUtils.saveQuestionnaire();
    });

    // Reset button
    document.getElementById('resetBtn').addEventListener('click', () => {
        FormUtils.resetForm();
    });

    // Validate button
    document.getElementById('validateBtn').addEventListener('click', async () => {
        FormUtils.showLoading('Validating your information...');
        const formData = FormUtils.getFormData();
        const results = await DocumentAPI.validateQuestionnaire(formData);
        FormUtils.hideLoading();

        FormUtils.displayValidationResults(results);
    });

    // Generate button
    document.getElementById('generateBtn').addEventListener('click', async () => {
        FormUtils.showLoading('Generating your Advanced Directive document...');
        const formData = FormUtils.getFormData();
        const result = await DocumentAPI.generateDocument(formData);
        FormUtils.hideLoading();

        FormUtils.displayDocumentResult(result, formData);
    });

    // Organ donation checkbox
    const organCheckbox = document.querySelector('input[name="want_organ_donation"]');
    if (organCheckbox) {
        organCheckbox.addEventListener('change', (e) => {
            const typesDiv = document.getElementById('organDonationTypes');
            const purposeDiv = document.getElementById('organDonationPurpose');
            if (e.target.checked) {
                typesDiv.style.display = 'block';
                purposeDiv.style.display = 'block';
            } else {
                typesDiv.style.display = 'none';
                purposeDiv.style.display = 'none';
            }
        });
    }

    // --- Witness/Notary Checkbox Logic ---
    const useWitnessesCheckbox = document.getElementById('useWitnessesCheckbox');
    const witnessesContainer = document.getElementById('witnessesContainer');
    if (useWitnessesCheckbox && witnessesContainer) {
        useWitnessesCheckbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                witnessesContainer.style.display = 'block';
            } else {
                witnessesContainer.style.display = 'none';
                // Clear witness fields when unchecked to avoid sending stale data
                document.getElementById('witness1Name').value = '';
                document.getElementById('witness1Phone').value = '';
                document.getElementById('witness1Address').value = '';
                document.getElementById('witness2Name').value = '';
                document.getElementById('witness2Phone').value = '';
                document.getElementById('witness2Address').value = '';
            }
        });
    }
}

// Initialization
async function initialize() {
    // Load states
    const states = await DocumentAPI.getStates();
    const stateSelect = document.getElementById('stateOfResidence');
    states.forEach(state => {
        const option = document.createElement('option');
        option.value = state;
        option.textContent = state;
        stateSelect.appendChild(option);
    });

    // Setup event listeners
    setupEventListeners();

    // Initialize tab view
    TabManager.show('personal');
}

// Run initialization when DOM is ready
document.addEventListener('DOMContentLoaded', initialize);
