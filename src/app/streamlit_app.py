import os
import tempfile
import logging
import streamlit as st

# Local imports
from src.processors.cv_processor import CVProcessor
from src.analyzers.cv_analyzer import CVAnalyzer
from src.database.cv_database import CVDatabase
from src.query.query_engine import CVQueryEngine

logger = logging.getLogger(__name__)

class CVAnalysisApp:
    """Streamlit application for CV analysis and querying"""
    
    def __init__(self, cv_processor: CVProcessor, cv_analyzer: CVAnalyzer, 
                 cv_database: CVDatabase, query_engine: CVQueryEngine):
        self.cv_processor = cv_processor
        self.cv_analyzer = cv_analyzer
        self.cv_database = cv_database
        self.query_engine = query_engine
    
    def process_cv(self, file_path: str) -> str:
        """Process CV file and store in database"""
        cv_id = os.path.basename(file_path)
        
        # Skip if already processed
        if self.cv_database.get_cv(cv_id):
            logger.info(f"CV {cv_id} already processed, skipping")
            return f"CV {cv_id} already in database"
        
        # Extract text from CV
        cv_text = self.cv_processor.process_document(file_path)
        if not cv_text:
            return f"Failed to extract text from {cv_id}"
        
        # Extract structured information using LLM
        cv_data = self.cv_analyzer.extract_cv_information(cv_text)
        
        # Store in database
        self.cv_database.add_cv(cv_id, cv_data)
        
        return f"Successfully processed CV: {cv_id}"
    
    def batch_process_cvs(self, folder_path: str) -> list:
        """Process all CVs in a folder"""
        results = []
        
        if not os.path.exists(folder_path):
            return ["Folder not found"]
        
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) and filename.lower().endswith(('.pdf', '.docx', '.doc')):
                result = self.process_cv(file_path)
                results.append(result)
        
        return results
    
    def run_streamlit_app(self):
        """Run the Streamlit application"""
        st.title("CV Analysis System")
        
        # Sidebar for processing CVs
        with st.sidebar:
            st.header("Upload and Process CVs")
            
            uploaded_files = st.file_uploader("Upload CV documents", type=["pdf", "docx"], accept_multiple_files=True)
            
            if uploaded_files:
                process_button = st.button("Process CVs")
                
                if process_button:
                    progress_bar = st.progress(0)
                    for i, uploaded_file in enumerate(uploaded_files):
                        # Save the uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            temp_path = tmp_file.name
                        
                        # Process the CV
                        result = self.process_cv(temp_path)
                        st.write(result)
                        
                        # Clean up the temporary file
                        os.unlink(temp_path)
                        
                        # Update progress bar
                        progress_bar.progress((i + 1) / len(uploaded_files))
            
            st.divider()
            
            # Folder processing option
            folder_path = st.text_input("Or enter a folder path containing CVs:")
            if folder_path and st.button("Process Folder"):
                results = self.batch_process_cvs(folder_path)
                for result in results:
                    st.write(result)
            
            st.divider()
            
            # Database management
            st.subheader("Database Management")
            
            # Display database stats
            cv_count = len(self.cv_database.get_all_cvs())
            st.write(f"Database contains {cv_count} CVs")
            
            # Option to reset conversation
            if st.button("Reset Conversation"):
                self.query_engine.clear_conversation()
                if "chat_history" in st.session_state:
                    st.session_state.chat_history = []
                st.success("Conversation history cleared")
        
        # Main area for the chatbot
        st.header("CV Query Assistant")
        st.write("Ask questions about the CVs in the database:")
        
        # Initialize chat history in session state if not present
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Chat input
        user_query = st.chat_input("Ask a question about the CVs")
        if user_query:
            # Display user message
            with st.chat_message("user"):
                st.write(user_query)
            
            # Add to session state
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            # Get response from query engine
            with st.spinner("Thinking..."):
                response = self.query_engine.query(user_query)
            
            # Display assistant response
            with st.chat_message("assistant"):
                st.write(response)
            
            # Add to session state
            st.session_state.chat_history.append({"role": "assistant", "content": response})