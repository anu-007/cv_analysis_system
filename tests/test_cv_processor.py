import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile

from src.processors.cv_processor import CVProcessor

class TestCVProcessor(unittest.TestCase):
    
    def setUp(self):
        self.cv_processor = CVProcessor(ocr_enabled=True)
        
        # Create a temporary test file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file_path = os.path.join(self.temp_dir.name, "test_document.pdf")
        
        # Create an empty file for testing
        with open(self.test_file_path, "w") as f:
            f.write("")
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    @patch("fitz.open")
    def test_extract_text_from_pdf(self, mock_fitz_open):
        # Mock the PDF document
        mock_doc = MagicMock()
        mock_page = MagicMock()
        # Set up the page to return substantial text (more than 100 chars)
        mock_page.get_text.return_value = "Sample CV text with more than 100 characters to ensure OCR is not triggered. This is a test of the text extraction functionality in the CVProcessor class."
        mock_doc.load_page.return_value = mock_page
        mock_doc.__len__.return_value = 1
        mock_fitz_open.return_value = mock_doc
        
        # Test text extraction
        result = self.cv_processor.extract_text_from_pdf(self.test_file_path)
        
        # Verify results
        self.assertEqual(result, "Sample CV text with more than 100 characters to ensure OCR is not triggered. This is a test of the text extraction functionality in the CVProcessor class.")
        mock_fitz_open.assert_called_once_with(self.test_file_path)
        mock_doc.load_page.assert_called_once_with(0)
        mock_page.get_text.assert_called_once()
    
    @patch("fitz.open")
    @patch.object(CVProcessor, "_apply_ocr_to_pdf")
    def test_extract_text_from_pdf_with_ocr(self, mock_apply_ocr, mock_fitz_open):
        # Mock the PDF document with minimal text to trigger OCR
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Short text"  # Less than 100 chars
        mock_doc.load_page.return_value = mock_page
        mock_doc.__len__.return_value = 1
        mock_fitz_open.return_value = mock_doc
        
        # Mock OCR result
        mock_apply_ocr.return_value = "OCR extracted text"
        
        # Test text extraction with OCR
        result = self.cv_processor.extract_text_from_pdf(self.test_file_path)
        
        # Verify results
        self.assertEqual(result, "OCR extracted text")
        mock_fitz_open.assert_called_once_with(self.test_file_path)
        mock_apply_ocr.assert_called_once_with(mock_doc)
    
    @patch("docx2txt.process")
    def test_extract_text_from_docx(self, mock_docx2txt):
        mock_docx2txt.return_value = "Sample DOCX CV text"
        
        result = self.cv_processor.extract_text_from_docx(self.test_file_path)
        
        self.assertEqual(result, "Sample DOCX CV text")
        mock_docx2txt.assert_called_once_with(self.test_file_path)
    
    @patch.object(CVProcessor, "extract_text_from_pdf")
    @patch.object(CVProcessor, "extract_text_from_docx")
    def test_process_document(self, mock_extract_docx, mock_extract_pdf):
        # Set up return values
        mock_extract_pdf.return_value = "PDF content"
        mock_extract_docx.return_value = "DOCX content"
        
        # Test PDF processing
        pdf_path = "test.pdf"
        result_pdf = self.cv_processor.process_document(pdf_path)
        self.assertEqual(result_pdf, "PDF content")
        mock_extract_pdf.assert_called_once_with(pdf_path)
        
        # Test DOCX processing
        docx_path = "test.docx"
        result_docx = self.cv_processor.process_document(docx_path)
        self.assertEqual(result_docx, "DOCX content")
        mock_extract_docx.assert_called_once_with(docx_path)
        
        # Test unsupported format
        unsupported_path = "test.txt"
        result_unsupported = self.cv_processor.process_document(unsupported_path)
        self.assertEqual(result_unsupported, "")


# tests/test_cv_analyzer.py

import unittest
from unittest.mock import patch, MagicMock

from src.analyzers.cv_analyzer import CVAnalyzer

class TestCVAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.api_key = "test_api_key"
        self.cv_analyzer = CVAnalyzer(api_key=self.api_key, provider="gemini")
        self.sample_cv_text = "John Doe\nSoftware Engineer\nExperience: 5 years at ABC Corp"
    
    @patch("google.generativeai.GenerativeModel.generate_content")
    def test_extract_cv_information_gemini(self, mock_generate_content):
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = """```json
{
  "personal_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "123-456-7890",
    "location": "New York"
  },
  "education": [],
  "work_experience": [],
  "skills": {"technical": [], "soft": [], "languages": []},
  "projects": [],
  "certifications": []
}
```"""
        mock_generate_content.return_value = mock_response
        
        # Test extraction
        result = self.cv_analyzer.extract_cv_information(self.sample_cv_text)
        
        # Verify results
        self.assertEqual(result["personal_info"]["name"], "John Doe")
        self.assertEqual(result["personal_info"]["email"], "john@example.com")
        mock_generate_content.assert_called_once()
    
    def test_unsupported_provider(self):
        with self.assertRaises(ValueError):
            CVAnalyzer(api_key=self.api_key, provider="unsupported")


# tests/test_cv_database.py

import os
import json
import unittest
import tempfile
from src.database.cv_database import CVDatabase

class TestCVDatabase(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary file for the database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_database.json")
        self.cv_database = CVDatabase(db_path=self.db_path)
        
        # Sample CV data
        self.sample_cv = {
            "personal_info": {
                "name": "John Doe",
                "email": "john@example.com"
            },
            "education": [
                {
                    "degree": "Bachelor's",
                    "institution": "Test University"
                }
            ]
        }
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_add_and_get_cv(self):
        # Add a CV
        self.cv_database.add_cv("test_cv.pdf", self.sample_cv)
        
        # Get the CV
        retrieved_cv = self.cv_database.get_cv("test_cv.pdf")
        
        # Verify results
        self.assertEqual(retrieved_cv, self.sample_cv)
    
    def test_get_all_cvs(self):
        # Add multiple CVs
        self.cv_database.add_cv("cv1.pdf", self.sample_cv)
        self.cv_database.add_cv("cv2.pdf", self.sample_cv)
        
        # Get all CVs
        all_cvs = self.cv_database.get_all_cvs()
        
        # Verify results
        self.assertEqual(len(all_cvs), 2)
        self.assertIn("cv1.pdf", all_cvs)
        self.assertIn("cv2.pdf", all_cvs)
    
    def test_delete_cv(self):
        # Add a CV
        self.cv_database.add_cv("test_cv.pdf", self.sample_cv)
        
        # Delete the CV
        result = self.cv_database.delete_cv("test_cv.pdf")
        
        # Verify results
        self.assertTrue(result)
        self.assertIsNone(self.cv_database.get_cv("test_cv.pdf"))
    
    def test_database_persistence(self):
        # Add a CV
        self.cv_database.add_cv("test_cv.pdf", self.sample_cv)
        
        # Create a new database instance with the same path
        new_database = CVDatabase(db_path=self.db_path)
        
        # Get the CV from the new instance
        retrieved_cv = new_database.get_cv("test_cv.pdf")
        
        # Verify results
        self.assertEqual(retrieved_cv, self.sample_cv)


# Run all tests
if __name__ == "__main__":
    unittest.main()