import os
import logging
import tempfile
from typing import Optional

# Document processing libraries
import fitz  # PyMuPDF
import docx2txt
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

class CVProcessor:
    """Class to handle document processing and information extraction"""
    
    def __init__(self, ocr_enabled: bool = True, tesseract_path: Optional[str] = None):
        self.ocr_enabled = ocr_enabled
        
        # Configure pytesseract path if provided
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF documents, with optional OCR for scanned documents"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            
            # If text extraction yields little content and OCR is enabled, apply OCR
            if len(text.strip()) < 100 and self.ocr_enabled:
                logger.info(f"Applying OCR to {pdf_path} as limited text was extracted")
                text = self._apply_ocr_to_pdf(doc)
                
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            return ""
    
    def _apply_ocr_to_pdf(self, doc) -> str:
        """Apply OCR to PDF pages and extract text"""
        text = ""
        with tempfile.TemporaryDirectory() as temp_dir:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                image_path = os.path.join(temp_dir, f"page_{page_num}.png")
                pix.save(image_path)
                
                # Apply OCR to the image
                image = Image.open(image_path)
                page_text = pytesseract.image_to_string(image)
                text += page_text + "\n"
                
        return text
    
    def extract_text_from_docx(self, docx_path: str) -> str:
        """Extract text from Word documents"""
        try:
            text = docx2txt.process(docx_path)
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {docx_path}: {str(e)}")
            return ""
    
    def process_document(self, file_path: str) -> str:
        """Process document based on file type"""
        _, file_extension = os.path.splitext(file_path)
        
        if file_extension.lower() == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension.lower() in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        else:
            logger.warning(f"Unsupported file format: {file_extension}")
            return ""