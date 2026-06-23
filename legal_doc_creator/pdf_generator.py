"""
PDF Generator - Converts documents and JSON questionnaires to PDF format
Uses reportlab for robust PDF generation from text content
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.platypus import KeepTogether
from reportlab.lib import colors
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    Generates professional PDF documents from text content or JSON data.
    
    Features:
    - Converts plain text documents to formatted PDF
    - Creates stylized PDFs from JSON questionnaire data
    - Handles long documents with proper pagination
    - Includes professional styling and formatting
    """
    
    def __init__(self, page_size=letter, margin_inch=0.75):
        """
        Initialize PDF generator with page settings
        
        Args:
            page_size: Page size (letter, A4, etc.)
            margin_inch: Margin size in inches
        """
        self.page_size = page_size
        self.margin = margin_inch * inch
        self.styles = self._setup_styles()
        self.full_name = ""
        self.page_count = 0
    
    def _setup_styles(self) -> dict:
        """Setup custom paragraph styles for professional formatting"""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#003366'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading style
        styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#003366'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#CCCCCC'),
            borderWidth=0.5,
            borderPadding=5
        ))
        
        # Body text style
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=14
        ))
        
        # Table body text style
        styles.add(ParagraphStyle(
            name='TableBody',
            parent=styles['BodyText'],
            fontSize=10,
            alignment=TA_LEFT,
            leading=12
        ))
        
        # Signature line style
        styles.add(ParagraphStyle(
            name='SignatureLine',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=15,
            spaceBefore=20
        ))
        
        return styles

    def _footer_canvas(self, canvas, doc):
        """Draws the footer on each page."""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        page_num_text = f"Page {doc.page} of {self.page_count}"
        
        if self.full_name:
            footer_text = f"{self.full_name} | {page_num_text}"
        else:
            footer_text = page_num_text
        
        # Calculate position for the footer
        x = self.page_size[0] / 2
        y = self.margin * 0.5  # Half an inch from the bottom
        
        canvas.drawCentredString(x, y, footer_text)
        canvas.restoreState()

    @staticmethod
    def _format_phone(s: str) -> str:
        """Formats a 10-digit phone number string."""
        if not s:
            return ''
        digits = ''.join(filter(str.isdigit, str(s)))
        if len(digits) == 10:
            return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
        return s
    
    def text_to_pdf(self, text_content: str, output_path: str, 
                   title: Optional[str] = None, full_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Convert plain text document to a formatted PDF, preserving paragraphs.
        
        Args:
            text_content: The document text to convert
            output_path: Path where PDF should be saved
            title: Optional title for the document
            full_name: Name of the person for the footer
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Create PDF document
            pdf_path = Path(output_path)
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=self.page_size,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )
            
            # Build story (content elements)
            story = []
            
            # Add title if provided
            if title:
                story.append(Paragraph(title, self.styles['CustomTitle']))
                story.append(Spacer(1, 0.2 * inch))
            
            # Split content into blocks based on one or more empty lines
            # This preserves paragraphs.
            blocks = re.split(r'\n\s*\n', text_content)
            
            for block in blocks:
                # Sanitize block
                clean_block = block.strip()
                if not clean_block:
                    continue

                # Escape special characters for reportlab XML
                safe_block = self._escape_special_chars(clean_block)
                
                # Check if the block is a heading (all caps and relatively short)
                # The check for underscores handles signature lines.
                if (safe_block.upper() == safe_block and not '_' in safe_block and len(safe_block.splitlines()) == 1):
                    story.append(Paragraph(safe_block, self.styles['SectionHeading']))
                elif '________________' in safe_block:
                    # Handle signature lines specifically to avoid large gaps
                    # Replace newlines with <br/> tags for manual line breaks
                    story.append(Paragraph(safe_block.replace('\n', '<br/>'), self.styles['SignatureLine']))
                else:
                    # Regular paragraph, replace newlines with <br/> to preserve them
                    story.append(Paragraph(safe_block.replace('\n', '<br/>'), self.styles['CustomBody']))
                
                # Add a small spacer after each block for readability
                story.append(Spacer(1, 0.1 * inch))
            
            # Set name for footer
            self.full_name = full_name if full_name else ""

            # Pass 1: Dummy build to get page count
            doc.build(story)
            self.page_count = doc.page

            # Pass 2: Real build with footer
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=self.page_size,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )
            doc.build(story, onFirstPage=self._footer_canvas, onLaterPages=self._footer_canvas)
            
            logger.info(f"PDF generated successfully: {pdf_path}")
            return True, f"PDF saved to {pdf_path}"
        
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return False, f"Error generating PDF: {str(e)}"

    def _add_treatment_preference(self, story, data, key, title, texts):
        """Helper to add a formatted treatment preference to the story."""
        if data.get(key):
            story.append(Paragraph(title, self.styles['CustomBody']))
            preference = data.get(key)
            text_to_render = texts.get(preference, texts.get('uncertain'))
            story.append(Paragraph(self._escape_special_chars(text_to_render), self.styles['CustomBody']))
            story.append(Spacer(1, 0.15 * inch))

    def questionnaire_to_pdf(self, questionnaire_data: Dict[str, Any],
                               output_path: str, document_type: str = 'advanced_directive') -> Tuple[bool, str]:
        """Convert questionnaire JSON data to a formatted PDF."""
        try:
            pdf_path = Path(output_path)
            pdf_path.parent.mkdir(parents=True, exist_ok=True)

            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=self.page_size,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )

            story = []
            data = questionnaire_data

            # --- HEADER ---
            story.append(Paragraph('ADVANCE DIRECTIVE FOR HEALTH CARE', self.styles['CustomTitle']))
            story.append(Paragraph('STATE OF CALIFORNIA', self.styles['SectionHeading']))
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph(f"I, {data.get('full_name', '________________')}, being of sound mind...", self.styles['CustomBody']))

            # --- PART I: AGENT ---
            if data.get('healthcare_agent_name'):
                story.append(Paragraph('PART I: DESIGNATION OF HEALTHCARE AGENT', self.styles['SectionHeading']))
                story.extend(self._build_info_table([('Name', data.get('healthcare_agent_name')), ('Relationship', data.get('healthcare_agent_relationship')), ('Phone', self._format_phone(data.get('healthcare_agent_phone'))), ('Email', data.get('healthcare_agent_email')), ('Address', Paragraph(self._escape_special_chars(data.get('healthcare_agent_address','')).replace('\n', '<br/>'), self.styles['TableBody']))]))
            if data.get('alternate_agent_name'):
                story.append(Paragraph('FIRST ALTERNATE HEALTHCARE AGENT', self.styles['SectionHeading']))
                story.extend(self._build_info_table([('Name', data.get('alternate_agent_name')), ('Relationship', data.get('alternate_agent_relationship')), ('Phone', self._format_phone(data.get('alternate_agent_phone'))), ('Email', data.get('alternate_agent_email')), ('Address', Paragraph(self._escape_special_chars(data.get('alternate_agent_address','')).replace('\n', '<br/>'), self.styles['TableBody']))]))
            if data.get('alternate_agent_2_name'):
                story.append(Paragraph('SECOND ALTERNATE HEALTHCARE AGENT', self.styles['SectionHeading']))
                story.extend(self._build_info_table([('Name', data.get('alternate_agent_2_name')), ('Relationship', data.get('alternate_agent_2_relationship')), ('Phone', self._format_phone(data.get('alternate_agent_2_phone'))), ('Email', data.get('alternate_agent_2_email')), ('Address', Paragraph(self._escape_special_chars(data.get('alternate_agent_2_address','')).replace('\n', '<br/>'), self.styles['TableBody']))]))

            # --- PART II: LIFE-SUSTAINING TREATMENT ---
            treatment_keys = ['want_cpr', 'want_mechanical_ventilation', 'want_feeding_tube', 'want_dialysis', 'want_antibiotics', 'want_blood_transfusions']
            if any(data.get(k) for k in treatment_keys):
                story.append(Paragraph('PART II: LIFE-SUSTAINING TREATMENT PREFERENCES', self.styles['SectionHeading']))
                self._add_treatment_preference(story, data, 'want_cpr', 'A. Cardiopulmonary Resuscitation (CPR)', {'yes': 'I request CPR.', 'no': 'I do NOT want CPR.', 'only_if_recovery': 'I request CPR only if recovery is likely.', 'uncertain': 'My preference is uncertain.'})
                self._add_treatment_preference(story, data, 'want_mechanical_ventilation', 'B. Mechanical Ventilation', {'yes': 'I request mechanical ventilation.', 'no': 'I do NOT want mechanical ventilation.', 'only_if_recovery': 'I request mechanical ventilation only if recovery is likely.', 'uncertain': 'My preference is uncertain.'})
                self._add_treatment_preference(story, data, 'want_feeding_tube', 'C. Artificial Feeding and Hydration', {'yes': 'I request a feeding tube.', 'no': 'I do NOT want a feeding tube.', 'only_if_recovery': 'I request a feeding tube only if needed for recovery.', 'uncertain': 'My preference is uncertain.'})
                self._add_treatment_preference(story, data, 'want_dialysis', 'D. Dialysis', {'yes': 'I request dialysis.', 'no': 'I do NOT want dialysis.', 'only_if_recovery': 'I request dialysis only if needed for recovery.', 'uncertain': 'My preference is uncertain.'})
                self._add_treatment_preference(story, data, 'want_antibiotics', 'E. Antibiotics', {'yes': 'I request antibiotics.', 'no': 'I do NOT want antibiotics to prolong life.', 'only_if_recovery': 'I request antibiotics only if recovery is likely.', 'uncertain': 'My preference is uncertain.'})
                self._add_treatment_preference(story, data, 'want_blood_transfusions', 'F. Blood Transfusions', {'yes': 'I request blood transfusions.', 'no': 'I do NOT want blood transfusions.', 'only_if_recovery': 'I request blood transfusions only if needed for recovery.', 'uncertain': 'My preference is uncertain.'})

            # --- PART III: CONDITION-SPECIFIC ---
            conditions_for_no = [desc for key, desc in self.get_condition_map().items() if data.get(key) == 'no']
            conditions_for_yes = [desc for key, desc in self.get_condition_map().items() if data.get(key) == 'yes']
            conditions_for_recovery = [desc for key, desc in self.get_condition_map().items() if data.get(key) == 'only_if_recovery']
            conditions_for_uncertain = [desc for key, desc in self.get_condition_map().items() if data.get(key) == 'uncertain']

            if any([conditions_for_no, conditions_for_yes, conditions_for_recovery, conditions_for_uncertain]):
                story.append(Paragraph('PART III: CONDITION-SPECIFIC INSTRUCTIONS', self.styles['SectionHeading']))
                if conditions_for_no:
                    story.append(Paragraph('I do NOT want life-sustaining treatment if:', self.styles['CustomBody']))
                    for item in conditions_for_no: story.append(Paragraph(f'- {item}', self.styles['CustomBody']))
                if conditions_for_yes:
                    story.append(Paragraph('I WANT life-sustaining treatment if:', self.styles['CustomBody']))
                    for item in conditions_for_yes: story.append(Paragraph(f'- {item}', self.styles['CustomBody']))
                if conditions_for_recovery:
                    story.append(Paragraph('I want life-sustaining treatment ONLY IF my medical team believes recovery to a meaningful quality of life is likely, in the following situations:', self.styles['CustomBody']))
                    for item in conditions_for_recovery: story.append(Paragraph(f'- {item}', self.styles['CustomBody']))
                if conditions_for_uncertain:
                    story.append(Paragraph('My preference is UNCERTAIN, and I leave the decision to my healthcare agent in the following situations:', self.styles['CustomBody']))
                    for item in conditions_for_uncertain: story.append(Paragraph(f'- {item}', self.styles['CustomBody']))

            # --- PART IV: PAIN MANAGEMENT ---
            if data.get('pain_management_priority') or data.get('accept_medication_side_effects'):
                 story.append(Paragraph('PART IV: PAIN MANAGEMENT', self.styles['SectionHeading']))
                 if data.get('pain_management_priority'): story.append(Paragraph('I direct that my comfort and pain management be prioritized, even if it might shorten my life.', self.styles['CustomBody']))
                 if data.get('accept_medication_side_effects'): story.append(Paragraph('I am willing to accept medications that may have side effects or may hasten death if they are necessary for my comfort.', self.styles['CustomBody']))

            # --- PART V: PERSONAL VALUES ---
            if data.get('personal_values') or data.get('quality_of_life_definition') or data.get('fears_and_concerns'):
                story.append(Paragraph('PART V: PERSONAL VALUES AND BELIEFS', self.styles['SectionHeading']))
                if data.get('personal_values'): story.append(Paragraph(f"What matters most to me: {self._escape_special_chars(data.get('personal_values'))}", self.styles['CustomBody']))
                if data.get('quality_of_life_definition'): story.append(Paragraph(f"Quality of life considerations: {self._escape_special_chars(data.get('quality_of_life_definition'))}", self.styles['CustomBody']))
                if data.get('fears_and_concerns'): story.append(Paragraph(f"My main concerns: {self._escape_special_chars(data.get('fears_and_concerns'))}", self.styles['CustomBody']))

            # --- PART VI: RIGHT NOT TO KNOW ---
            if data.get('right_not_to_know_preference') and data.get('right_not_to_know_preference') != 'none':
                story.append(Paragraph('PART VI: RIGHT NOT TO KNOW', self.styles['SectionHeading']))
                if data.get('right_not_to_know_preference') == 'agent_receives_info':
                    story.append(Paragraph('I do not wish to be informed of my specific diagnosis/prognosis, and instead authorize my designated agent to receive and act upon this information.', self.styles['CustomBody']))
                elif data.get('right_not_to_know_preference') == 'waive_risk_info':
                    story.append(Paragraph('I wish to be informed of my diagnosis, but I waive the right to be informed of the specific technical risks associated with the specific procedure.', self.styles['CustomBody']))

            # --- PART VII: ORGAN DONATION ---
            if data.get('want_organ_donation') == 'yes' or data.get('want_tissue_donation') == 'yes':
                story.append(Paragraph('PART VII: ORGAN AND TISSUE DONATION', self.styles['SectionHeading']))
                if data.get('want_organ_donation') == 'yes':
                    organs = ", ".join(data.get('organ_donation_types', []))
                    story.append(Paragraph(f"I wish to donate my organs for transplant. The specific organs I wish to donate are: {organs}.", self.styles['CustomBody']))

            # --- PART VIII: BODY DISPOSITION ---
            if data.get('body_disposition') or data.get('specific_wishes_body'):
                story.append(Paragraph('PART VIII: BODY DISPOSITION', self.styles['SectionHeading']))
                if data.get('body_disposition'): story.append(Paragraph(f"Preference for my body: {data.get('body_disposition').replace('_', ' ').title()}", self.styles['CustomBody']))
                if data.get('specific_wishes_body'): story.append(Paragraph(f"Special wishes: {self._escape_special_chars(data.get('specific_wishes_body'))}", self.styles['CustomBody']))

            # --- PART IX: SIGNATURE AND VALIDATION ---
            story.append(Paragraph('PART IX: SIGNATURE AND VALIDATION', self.styles['SectionHeading']))
            story.append(Paragraph('I acknowledge this is my wishes regarding health care...', self.styles['CustomBody']))
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph(f"_____________________________", self.styles['SignatureLine']))
            story.append(Paragraph(f"{data.get('full_name', '')}", self.styles['CustomBody']))
            story.append(Paragraph(f"Date: _______________________", self.styles['CustomBody']))

            if data.get('notary_required'):
                story.append(PageBreak())
                story.append(Paragraph('NOTARIZATION', self.styles['SectionHeading']))
                story.append(Paragraph("A notary public or other officer completing this certificate...", self.styles['CustomBody']))
                # ... full notary text

            if data.get('witness_1_name') and data.get('witness_2_name'):
                story.append(PageBreak())
                story.append(Paragraph('STATEMENT OF WITNESSES', self.styles['SectionHeading']))
                story.append(Paragraph("I declare under penalty of perjury...", self.styles['CustomBody']))
                story.append(Spacer(1, 0.2 * inch))
                story.append(Paragraph(f"Witness 1: {data.get('witness_1_name')} ({self._format_phone(data.get('witness_1_phone'))})", self.styles['CustomBody']))
                story.append(Paragraph(f"Address: {data.get('witness_1_address')}", self.styles['CustomBody']))
                story.append(Spacer(1, 0.5 * inch))
                story.append(Paragraph(f"Witness 2: {data.get('witness_2_name')} ({self._format_phone(data.get('witness_2_phone'))})", self.styles['CustomBody']))
                story.append(Paragraph(f"Address: {data.get('witness_2_address')}", self.styles['CustomBody']))

            # Set name for footer
            self.full_name = questionnaire_data.get('full_name', '')

            # Pass 1: Dummy build to get page count
            doc.build(story)
            self.page_count = doc.page

            # Pass 2: Real build with footer
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=self.page_size,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )
            doc.build(story, onFirstPage=self._footer_canvas, onLaterPages=self._footer_canvas)
            
            logger.info(f"PDF generated from questionnaire: {pdf_path}")
            return True, f"PDF saved to {pdf_path}"
        
        except Exception as e:
            logger.error(f"Error generating questionnaire PDF: {e}")
            return False, f"Error generating PDF: {str(e)}"

    def get_condition_map(self):
        """Returns the mapping of condition keys to descriptions."""
        return {
            'condition_permanently_unconscious': 'I am permanently unconscious (e.g., a persistent vegetative state).',
            'condition_terminal_illness': 'I am diagnosed with a terminal illness.',
            'condition_severe_dementia': 'I am diagnosed with severe dementia or another irreversible cognitive condition.',
            'condition_other_incurable': 'I am diagnosed with another incurable condition.'
        }

    def _build_info_table(self, items: list) -> list:
        """
        Build a styled information table
        
        Args:
            items: List of tuples (label, value)
        
        Returns:
            List with table and spacer
        """
        if not items:
            return []
        
        # Convert items to table data
        table_data = [[item[0], item[1]] for item in items]
        
        table = Table(table_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F0F7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ]))
        
        return [table, Spacer(1, 0.1 * inch)]
    
    @staticmethod
    def _escape_special_chars(text: str) -> str:
        """Escape special characters for reportlab XML parser"""
        if not isinstance(text, str):
            return str(text)
        
        # Escape XML special characters
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&apos;'
        }
        
        result = text
        for char, escaped in replacements.items():
            result = result.replace(char, escaped)
        
        return result


def generate_pdf_from_document(document_text: str, output_dir: Path, 
                              title: str = "Advanced Directive", full_name: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
    """
    Utility function to generate PDF from document text
    
    Args:
        document_text: The document content as text
        output_dir: Directory to save PDF
        title: Title for the PDF document
        full_name: Name of the person for the footer
    
    Returns:
        Tuple of (success: bool, message: str, file_path: Optional[str])
    """
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"{title.lower().replace(' ', '_')}_{timestamp}.pdf"
        pdf_path = output_dir / pdf_filename
        
        # Generate PDF
        generator = PDFGenerator()
        success, message = generator.text_to_pdf(document_text, str(pdf_path), title=title, full_name=full_name)
        
        if success:
            return True, message, str(pdf_path)
        else:
            return False, message, None
    
    except Exception as e:
        logger.error(f"Error in generate_pdf_from_document: {e}")
        return False, f"Error: {str(e)}", None


def generate_pdf_from_questionnaire(questionnaire_data: Dict[str, Any], 
                                   output_dir: Path,
                                   document_type: str = 'advanced_directive') -> Tuple[bool, str, Optional[str]]:
    """
    Utility function to generate PDF from questionnaire data
    
    Args:
        questionnaire_data: Questionnaire responses as dictionary
        output_dir: Directory to save PDF
        document_type: Type of document
    
    Returns:
        Tuple of (success: bool, message: str, file_path: Optional[str])
    """
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"{document_type}_{timestamp}.pdf"
        pdf_path = output_dir / pdf_filename
        
        # Generate PDF
        generator = PDFGenerator()
        success, message = generator.questionnaire_to_pdf(
            questionnaire_data,
            str(pdf_path),
            document_type=document_type
        )
        
        if success:
            return True, message, str(pdf_path)
        else:
            return False, message, None
    
    except Exception as e:
        logger.error(f"Error in generate_pdf_from_questionnaire: {e}")
        return False, f"Error: {str(e)}", None
