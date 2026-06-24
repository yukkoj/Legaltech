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
        Convert plain text document to a formatted PDF, preserving paragraphs and line breaks.

        Args:
            text_content: The document text to convert
            output_path: Path where PDF should be saved
            title: Optional title for the document
            full_name: Name of the person for the footer

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

            if title:
                story.append(Paragraph(title, self.styles['CustomTitle']))
                story.append(Spacer(1, 0.2 * inch))
            
            initial_story_len = len(story)

            # Process content by splitting into paragraphs based on blank lines
            text_paragraphs = re.split(r'\n\s*\n', text_content)

            for para in text_paragraphs:
                clean_para = para.strip()
                if not clean_para:
                    continue

                safe_para = self._escape_special_chars(clean_para)

                # Heuristic for identifying headings (single line, all caps)
                if (safe_para.isupper() and len(safe_para.splitlines()) == 1 and len(safe_para) < 80 and not '_' in safe_para):
                    story.append(Paragraph(safe_para, self.styles['SectionHeading']))
                elif '________________' in safe_para:
                    story.append(Paragraph(safe_para.replace('_', '&#95;'), self.styles['SignatureLine']))
                else:
                    # Preserve line breaks within a paragraph by replacing them with <br/>
                    story.append(Paragraph(safe_para.replace('\n', '<br/>'), self.styles['CustomBody']))

            # Fallback mechanism: If parsing failed to add content, add the whole text as one block.
            if len(story) == initial_story_len and text_content and text_content.strip():
                logger.warning("PDF parsing logic did not add any content. Adding entire text as a single block.")
                escaped_text = self._escape_special_chars(text_content).replace('\n', '<br/>')
                story.append(Paragraph(escaped_text, self.styles['CustomBody']))

            self.full_name = full_name if full_name else ""

            # --- Two-Pass Build for "Page X of Y" Footer ---
            # This is a standard reportlab pattern.
            # Pass 1: Render the document to determine the total number of pages.
            # The output of this pass is incorrect (footer shows "Page X of 0"), but it gives us the page count.
            doc.build(story, onFirstPage=self._footer_canvas, onLaterPages=self._footer_canvas)
            self.page_count = doc.page # Get the page count from the first pass

            # Pass 2: Render the document again to the same file.
            # This time, `self.page_count` is correct, so the footer will be "Page X of Y".
            # This overwrites the file created in Pass 1.
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
            logger.error(f"Error generating PDF: {e}", exc_info=True)
            return False, f"Error generating PDF: {str(e)}"

    def _add_treatment_preference(self, story, data, key, title, texts):
        """Helper to add a formatted treatment preference to the story."""
        if data.get(key):
            story.append(Paragraph(title, self.styles['CustomBody']))
            preference = data.get(key)
            text_to_render = texts.get(preference, texts.get('uncertain'))
            story.append(Paragraph(self._escape_special_chars(text_to_render), self.styles['CustomBody']))
            story.append(Spacer(1, 0.15 * inch))



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
