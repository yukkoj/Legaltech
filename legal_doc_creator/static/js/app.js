/**
 * Advanced Directive Form - Frontend JavaScript
 * Handles form navigation, validation, and API communication
 */

const API_BASE = '/api';
let currentTab = 'personal';
const allTabs = ['personal', 'healthcare', 'treatment', 'values', 'witnesses', 'review'];
let isValidated = false;
let generatedDocument = null;

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
}

// Form Utilities
class FormUtils {
    static getFormData() {
        const form = document.getElementById('questionnaireForm');
        const formData = new FormData(form);
        const data = {};

        // Convert FormData to object
        for (let [key, value] of formData.entries()) {
            if (key === 'organ_types' || key === 'want_organ_donation') {
                // Handle organ donation types
                if (!data['organ_donation_types']) {
                    data['organ_donation_types'] = [];
                }
                if (key === 'organ_types' && value) {
                    data['organ_donation_types'].push(value);
                }
            } else if (key.startsWith('want_') || key === 'notary_required' || key === 'pain_management_priority' || key === 'accept_medication_side_effects') {
                // Convert checkbox/radio boolean values
                if (value === 'true') {
                    data[key] = true;
                } else if (value === 'false') {
                    data[key] = false;
                } else {
                    data[key] = value;
                }
            } else {
                data[key] = value;
            }
        }

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

    static displayDocumentResult(result) {
        const resultsDiv = document.getElementById('generationResults');
        const messageDiv = document.getElementById('resultMessage');
        const previewDiv = document.getElementById('documentPreview');
        const contentDiv = document.getElementById('documentContent');

        resultsDiv.style.display = 'block';

        if (result.status === 'success') {
            messageDiv.className = 'result-message success';
            messageDiv.textContent = '✅ Document generated successfully!';

            // Display document preview
            contentDiv.textContent = result.document;
            previewDiv.style.display = 'block';

            generatedDocument = result;

            // Enable download button
            document.getElementById('downloadDocBtn').onclick = () => {
                FormUtils.downloadDocument(result);
            };

            document.getElementById('copyDocBtn').onclick = () => {
                FormUtils.copyToClipboard(result.document);
            };
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

    static downloadDocument(result) {
        const element = document.createElement('a');
        const file = new Blob([result.document], { type: 'text/plain' });
        element.href = URL.createObjectURL(file);
        element.download = `advanced_directive_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    static copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            alert('Document copied to clipboard!');
        }).catch(() => {
            alert('Failed to copy to clipboard');
        });
    }

    static resetForm() {
        if (confirm('Are you sure you want to reset the entire form?')) {
            document.getElementById('questionnaireForm').reset();
            isValidated = false;
            document.getElementById('generationResults').style.display = 'none';
            document.getElementById('validationResults').innerHTML = '';
            TabManager.show('personal');
            alert('Form has been reset.');
        }
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
        isValidated = results.is_valid;

        // Enable generate button if validated
        document.getElementById('generateBtn').disabled = !isValidated;
    });

    // Generate button
    document.getElementById('generateBtn').addEventListener('click', async () => {
        FormUtils.showLoading('Generating your Advanced Directive document...');
        const formData = FormUtils.getFormData();
        const result = await DocumentAPI.generateDocument(formData);
        FormUtils.hideLoading();

        FormUtils.displayDocumentResult(result);
    });

    // Organ donation checkbox
    const organCheckbox = document.querySelector('input[name="want_organ_donation"]');
    if (organCheckbox) {
        organCheckbox.addEventListener('change', (e) => {
            const typesDiv = document.getElementById('organDonationTypes');
            if (e.target.checked) {
                typesDiv.style.display = 'block';
            } else {
                typesDiv.style.display = 'none';
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
