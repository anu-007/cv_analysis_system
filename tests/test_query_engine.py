import unittest
from unittest.mock import patch, MagicMock

from src.query.query_engine import CVQueryEngine
from src.database.cv_database import CVDatabase

class TestQueryEngine(unittest.TestCase):
    
    def setUp(self):
        self.api_key = "test_api_key"
        self.cv_database = MagicMock(spec=CVDatabase)
        self.query_engine = CVQueryEngine(self.cv_database, api_key=self.api_key)
        
        # Sample CV data
        self.sample_cv_data = {
            "cv1.pdf": {
                "personal_info": {
                    "name": "John Doe",
                    "email": "john@example.com"
                },
                "skills": {
                    "technical": ["Python", "Machine Learning"]
                }
            },
            "cv2.pdf": {
                "personal_info": {
                    "name": "Jane Smith",
                    "email": "jane@example.com"
                },
                "skills": {
                    "technical": ["Java", "SQL"]
                }
            }
        }
        
        # Set up mock database response
        self.cv_database.get_all_cvs.return_value = self.sample_cv_data
    
    def test_add_to_conversation(self):
        # Test adding messages to conversation history
        self.query_engine.add_to_conversation("user", "Test message")
        self.assertEqual(len(self.query_engine.conversation_history), 1)
        self.assertEqual(self.query_engine.conversation_history[0]["role"], "user")
        self.assertEqual(self.query_engine.conversation_history[0]["content"], "Test message")
    
    def test_clear_conversation(self):
        # Add some messages
        self.query_engine.add_to_conversation("user", "Message 1")
        self.query_engine.add_to_conversation("assistant", "Response 1")
        
        # Clear conversation
        self.query_engine.clear_conversation()
        
        # Verify conversation is empty
        self.assertEqual(len(self.query_engine.conversation_history), 0)
    
    @patch("google.generativeai.GenerativeModel.start_chat")
    def test_query(self, mock_start_chat):
        # Mock chat session
        mock_chat = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "John Doe has Python skills"
        mock_chat.send_message.return_value = mock_response
        mock_start_chat.return_value = mock_chat
        
        # Test query
        result = self.query_engine.query("Who has Python skills?")
        
        # Verify results
        self.assertEqual(result, "John Doe has Python skills")
        mock_start_chat.assert_called_once()
        
        # Verify conversation history was updated
        self.assertEqual(len(self.query_engine.conversation_history), 2)
        self.assertEqual(self.query_engine.conversation_history[0]["role"], "user")
        self.assertEqual(self.query_engine.conversation_history[0]["content"], "Who has Python skills?")
        self.assertEqual(self.query_engine.conversation_history[1]["role"], "assistant")
        self.assertEqual(self.query_engine.conversation_history[1]["content"], "John Doe has Python skills")
    
    @patch("google.generativeai.GenerativeModel.start_chat")
    def test_query_with_exception(self, mock_start_chat):
        # Mock chat session that raises an exception
        mock_chat = MagicMock()
        mock_chat.send_message.side_effect = Exception("Test error")
        mock_start_chat.return_value = mock_chat
        
        # Test query with exception
        result = self.query_engine.query("Who has Python skills?")
        
        # Verify error message is returned
        self.assertTrue("I'm sorry, I encountered an error" in result)
        mock_start_chat.assert_called_once()


if __name__ == "__main__":
    unittest.main() 