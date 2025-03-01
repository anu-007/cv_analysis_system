# CV Analysis System

A comprehensive system for processing, analyzing, and querying CV/resume data using Google Gemini AI.

## Features

- CV text extraction from PDF and image files
- AI-powered CV analysis and information extraction using Google Gemini
- Structured CV data storage
- Natural language querying of CV data
- User-friendly Streamlit interface

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Install Tesseract OCR (required for text extraction from images and scanned PDFs):
   - **macOS**: `brew install tesseract`
   - **Windows**: Download from [UB Mannheim GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Linux**: `sudo apt install tesseract-ocr` or `sudo dnf install tesseract`
5. Get a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/)
6. Configure your `.env` file:
   ```
   LLM_API_KEY=your_gemini_api_key_here
   ```

## Usage

1. Run the application:
   ```
   streamlit app.py
   ```
2. Open your browser and navigate to the Streamlit app (typically http://localhost:8501)
3. Upload CV files (PDF or images)
4. View the extracted information and analysis
5. Query the CV database using natural language

## Project Structure

- `app.py`: Main application entry point
- `src/processors/`: CV text extraction and processing
- `src/analyzers/`: AI-powered CV analysis with Google Gemini
- `src/database/`: CV data storage
- `src/query/`: Natural language query engine
- `src/app/`: Streamlit UI components
- `data/`: Storage for CV files and extracted data
- `tests/`: Unit and integration tests

## Dependencies Explained

The system uses several key Python libraries:

- **google-generativeai**: Provides access to Google's Gemini AI models for CV analysis and natural language queries
- **PyPDF2 & pytesseract**: Used for extracting text from PDF files and performing OCR on images
- **streamlit**: Powers the user interface for uploading CVs and displaying results
- **pandas & numpy**: Used for data manipulation and analysis of structured CV data
- **scikit-learn**: Provides machine learning capabilities for:
  - Text vectorization and similarity matching between job descriptions and CVs
  - Candidate ranking and recommendation
  - Skills clustering and categorization
  - Feature extraction from CV text

## Troubleshooting

If you encounter the error `ModuleNotFoundError: No module named 'src'`, make sure you're running the application from the project root directory. The error occurs because Python can't find the `src` module in its path.

If you see `tesseract is not installed or it's not in your PATH`, follow the Tesseract OCR installation instructions in the Setup section.

## License

MIT 