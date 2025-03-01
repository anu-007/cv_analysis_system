import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class CVDatabase:
    """Class to store and query CV information"""
    
    def __init__(self, db_path: str = "data/cv_database.json"):
        self.db_path = db_path
        self.cv_data = {}
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.load_database()
    
    def load_database(self):
        """Load existing database if available"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    self.cv_data = json.load(f)
                logger.info(f"Loaded {len(self.cv_data)} CVs from database")
            except Exception as e:
                logger.error(f"Error loading database: {str(e)}")
                self.cv_data = {}
    
    def save_database(self):
        """Save CV data to database file"""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.cv_data, f, indent=2)
            logger.info(f"Saved {len(self.cv_data)} CVs to database")
        except Exception as e:
            logger.error(f"Error saving database: {str(e)}")
    
    def add_cv(self, cv_id: str, cv_data: Dict[str, Any]):
        """Add or update CV in the database"""
        self.cv_data[cv_id] = cv_data
        self.save_database()
    
    def get_cv(self, cv_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve CV by ID"""
        return self.cv_data.get(cv_id)
    
    def get_all_cvs(self) -> Dict[str, Dict[str, Any]]:
        """Get all CVs in the database"""
        return self.cv_data
    
    def delete_cv(self, cv_id: str) -> bool:
        """Delete a CV from the database"""
        if cv_id in self.cv_data:
            del self.cv_data[cv_id]
            self.save_database()
            return True
        return False
    
    def search_cvs(self, search_function) -> Dict[str, Dict[str, Any]]:
        """Search CVs using a custom search function"""
        return {cv_id: cv_data for cv_id, cv_data in self.cv_data.items() 
                if search_function(cv_data)}