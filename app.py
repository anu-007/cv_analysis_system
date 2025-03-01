import os
import logging
import streamlit as st
from dotenv import load_dotenv

from src.processors.cv_processor import CVProcessor
from src.analyzers.cv_analyzer import CVAnalyzer
from src.database.cv_database import CVDatabase
from src.query.query_engine import CVQueryEngine
from src.app.streamlit_app import CVAnalysisApp

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment variables
    api_key = os.getenv("LLM_API_KEY")
    
    if not api_key:
        logger.error("No API key found. Please set LLM_API_KEY in .env file")
        st.error("No API key found. Please set LLM_API_KEY in .env file")
        return
    
    # Initialize components
    cv_processor = CVProcessor(ocr_enabled=True)
    cv_analyzer = CVAnalyzer(api_key=api_key)
    cv_database = CVDatabase()
    query_engine = CVQueryEngine(cv_database, api_key=api_key)
    
    # Initialize and run the application
    app = CVAnalysisApp(
        cv_processor=cv_processor,
        cv_analyzer=cv_analyzer,
        cv_database=cv_database,
        query_engine=query_engine
    )
    
    # Run the Streamlit app
    app.run_streamlit_app()

if __name__ == "__main__":
    main()