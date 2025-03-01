import json
import logging
from typing import List, Dict, Any

# LLM integration
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

# Local imports
from src.database.cv_database import CVDatabase

logger = logging.getLogger(__name__)

class CVQueryEngine:
    """Class to handle natural language queries about CVs"""
    
    def __init__(self, cv_database: CVDatabase, api_key: str, provider: str = "gemini"):
        self.cv_database = cv_database
        self.provider = provider.lower()
        self.conversation_history = []
        
        if self.provider == "gemini":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def add_to_conversation(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})
        # Keep conversation history manageable
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_history = []
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def query(self, user_query: str) -> str:
        """Process natural language query about CVs"""
        # Add user query to conversation history
        self.add_to_conversation("user", user_query)
        
        # Prepare CV data for context
        cv_data = self.cv_database.get_all_cvs()
        cv_context = json.dumps(cv_data, indent=2)
        
        # Create system prompt with context
        system_prompt = f"""
        You are a CV analysis assistant. You have access to the following CV data:
        {cv_context}

        Answer questions about this CV data accurately and concisely. You can:
        1. Find candidates with specific skills
        2. Compare education levels
        3. Search for experience in specific industries
        4. Identify matching candidates for job requirements
        5. Provide detailed information about any candidate
        
        Only use the information provided in the CV data. If the information is not available, say so.
        """
        
        try:
            # Format conversation history for Gemini
            chat = self.model.start_chat(history=[])
            
            # Add system prompt as first message
            chat.send_message(system_prompt)
            
            # Add conversation history
            for msg in self.conversation_history:
                if msg["role"] == "user":
                    chat.send_message(msg["content"])
                # Skip assistant messages as they're already in the chat history
            
            # Send the latest query and get response
            response = chat.send_message(user_query)
            result = response.text
            
            # Add response to conversation history
            self.add_to_conversation("assistant", result)
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return "I'm sorry, I encountered an error while processing your query. Please try again."