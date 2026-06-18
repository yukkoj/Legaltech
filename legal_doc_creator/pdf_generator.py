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
        
        # Signature line style
        styles.add(ParagraphStyle(
            name='SignatureLine',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=15,
            spaceBefore=20
        ))
        
        return styles
    
    def text_to_pdf(self, text_content: str, output_path: str, 
                   title: Optional[str] = None) -> Tuple[bool, str]:
        """
        Convert plain text document to a formatted PDF, preserving paragraphs.
        
        Args:
            text_content: The document text to convert
            output_path: Path where PDF should be saved
            title: Optional title for the document
        
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
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF generated successfully: {pdf_path}")
            return True, f"PDF saved to {pdf_path}"
        
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return False, f"Error generating PDF: {str(e)}"
    
    def questionnaire_to_pdf(self, questionnaire_data: Dict[str, Any], 
                           output_path: str, document_type: str = 'advanced_directive') -> Tuple[bool, str]:
        """
        Convert questionnaire JSON data to a formatted PDF
        
        Args:
            questionnaire_data: Dictionary with questionnaire responses
            output_path: Path where PDF should be saved
            document_type: Type of document (advanced_directive, etc.)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
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
            
            # Add title based on document type
            if document_type == 'advanced_directive':
                title = 'ADVANCE DIRECTIVE FOR HEALTH CARE'
            else:
                title = f'{document_type.upper().replace("_", " ")}'
            
            story.append(Paragraph(title, self.styles['CustomTitle']))
            story.append(Spacer(1, 0.3 * inch))
            
            # Add document date
            date_str = datetime.now().strftime('%B %d, %Y')
            story.append(Paragraph(f"<i>Generated on {date_str}</i>", self.styles['CustomBody']))
            story.append(Spacer(1, 0.2 * inch))
            
            # Personal Information Section
            story.append(Paragraph('PERSONAL INFORMATION', self.styles['SectionHeading']))
            
            personal_info = [
                ('Name', questionnaire_data.get('full_name', 'N/A')),
                ('Date of Birth', questionnaire_data.get('date_of_birth', 'N/A')),
                ('State of Residence', questionnaire_data.get('state_of_residence', 'N/A')),
            ]
            
            story.extend(self._build_info_table(personal_info))
            story.append(Spacer(1, 0.15 * inch))
            
            # Healthcare Agent Section
            story.append(Paragraph('HEALTHCARE AGENT (PRIMARY)', self.styles['SectionHeading']))
            
            agent_info = [
                ('Name', questionnaire_data.get('healthcare_agent_name', 'N/A')),
                ('Relationship', questionnaire_data.get('healthcare_agent_relationship', 'N/A')),
                ('Phone', questionnaire_data.get('healthcare_agent_phone', 'N/A')),
                ('Email', questionnaire_data.get('healthcare_agent_email', 'N/A')),
                ('Address', questionnaire_data.get('healthcare_agent_address', 'N/A')),
            ]
            
            story.extend(self._build_info_table(agent_info))
            story.append(Spacer(1, 0.15 * inch))
            
            # Alternate Agents Section
            if questionnaire_data.get('alternate_agent_name'):
                story.append(Paragraph('FIRST ALTERNATE HEALTHCARE AGENT', self.styles['SectionHeading']))
                
                alt_agent_info = [
                    ('Name', questionnaire_data.get('alternate_agent_name', 'N/A')),
                    ('Relationship', questionnaire_data.get('alternate_agent_relationship', 'N/A')),
                    ('Phone', questionnaire_data.get('alternate_agent_phone', 'N/A')),
                    ('Email', questionnaire_data.get('alternate_agent_email', 'N/A')),
                    ('Address', questionnaire_data.get('alternate_agent_address', 'N/A')),
                ]
                
                story.extend(self._build_info_table(alt_agent_info))
                story.append(Spacer(1, 0.15 * inch))
            
            # Second Alternate Agent Section
            if questionnaire_data.get('alternate_agent_2_name'):
                story.append(Paragraph('SECOND ALTERNATE HEALTHCARE AGENT', self.styles['SectionHeading']))
                
                alt_agent_2_info = [
                    ('Name', questionnaire_data.get('alternate_agent_2_name', 'N/A')),
                    ('Relationship', questionnaire_data.get('alternate_agent_2_relationship', 'N/A')),
                    ('Phone', questionnaire_data.get('alternate_agent_2_phone', 'N/A')),
                    ('Email', questionnaire_data.get('alternate_agent_2_email', 'N/A')),
                    ('Address', questionnaire_data.get('alternate_agent_2_address', 'N/A')),
                ]
                
                story.extend(self._build_info_table(alt_agent_2_info))
                story.append(Spacer(1, 0.15 * inch))
            
            # Treatment Preferences
            story.append(Paragraph('TREATMENT PREFERENCES', self.styles['SectionHeading']))
            
            treatment_prefs = [
                ('CPR (Cardiopulmonary Resuscitation)', questionnaire_data.get('want_cpr', 'Not specified')),
                ('Mechanical Ventilation', questionnaire_data.get('want_mechanical_ventilation', 'Not specified')),
                ('Feeding Tube', questionnaire_data.get('want_feeding_tube', 'Not specified')),
                ('Dialysis', questionnaire_data.get('want_dialysis', 'Not specified')),
                ('Antibiotics', questionnaire_data.get('want_antibiotics', 'Not specified')),
                ('Blood Transfusions', questionnaire_data.get('want_blood_transfusions', 'Not specified')),
            ]
            
            story.extend(self._build_info_table(treatment_prefs))
            story.append(Spacer(1, 0.15 * inch))
            
            # Personal Values
            if questionnaire_data.get('personal_values'):
                story.append(Paragraph('PERSONAL VALUES', self.styles['SectionHeading']))
                story.append(Paragraph(
                    self._escape_special_chars(questionnaire_data.get('personal_values', '')),
                    self.styles['CustomBody']
                ))
                story.append(Spacer(1, 0.15 * inch))
            
            # Organ Donation
            if questionnaire_data.get('want_organ_donation') == 'yes':
                story.append(Paragraph('ORGAN DONATION', self.styles['SectionHeading']))
                donation_info = [
                    ('Wishes', questionnaire_data.get('organ_donation_types', 'As specified by law')),
                ]
                story.extend(self._build_info_table(donation_info))
                story.append(Spacer(1, 0.15 * inch))
            
            # Body Disposition
            if questionnaire_data.get('body_disposition'):
                story.append(Paragraph('BODY DISPOSITION', self.styles['SectionHeading']))
                disposition_info = [
                    ('Preference', questionnaire_data.get('body_disposition', 'Not specified')),
                ]
                if questionnaire_data.get('specific_wishes_body'):
                    disposition_info.append(('Special Wishes', questionnaire_data.get('specific_wishes_body')))
                story.extend(self._build_info_table(disposition_info))
                story.append(Spacer(1, 0.15 * inch))
            
            # Signature section
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph('SIGNATURE', self.styles['SectionHeading']))
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph('_' * 50, self.styles['SignatureLine']))
            story.append(Paragraph('Print Name', self.styles['CustomBody']))
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph('_' * 50, self.styles['SignatureLine']))
            story.append(Paragraph('Signature', self.styles['CustomBody']))
            story.append(Spacer(1, 0.15 * inch))
            story.append(Paragraph('_' * 50, self.styles['SignatureLine']))
            story.append(Paragraph('Date', self.styles['CustomBody']))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF generated from questionnaire: {pdf_path}")
            return True, f"PDF saved to {pdf_path}"
        
        except Exception as e:
            logger.error(f"Error generating questionnaire PDF: {e}")
            return False, f"Error generating PDF: {str(e)}"
    
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
                              title: str = "Advanced Directive") -> Tuple[bool, str, Optional[str]]:
    """
    Utility function to generate PDF from document text
    
    Args:
        document_text: The document content as text
        output_dir: Directory to save PDF
        title: Title for the PDF document
    
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
        success, message = generator.text_to_pdf(document_text, str(pdf_path), title=title)
        
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
