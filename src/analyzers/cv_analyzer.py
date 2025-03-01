import re
import json
import logging
from typing import Dict, Any

# LLM integration
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class CVAnalyzer:
    """Class to analyze CV content using LLM"""
    
    def __init__(self, api_key: str, provider: str = "gemini"):
        self.provider = provider.lower()
        
        if self.provider == "gemini":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def extract_cv_information(self, cv_text: str) -> Dict[str, Any]:
        """Extract structured information from CV text using LLM"""
        try:
            # Prompt engineering for CV analysis
            prompt = f"""
            Extract the following information from this CV in a structured JSON format:
            1. Personal Information (name, email, phone, location)
            2. Education History (degree, institution, graduation year, field of study)
            3. Work Experience (job title, company, duration, responsibilities)
            4. Skills (technical skills, soft skills, languages)
            5. Projects (name, description, technologies used)
            6. Certifications (name, issuing organization, year)

            Provide the output as a valid JSON object with the following structure:
            {{
                "personal_info": {{
                    "name": "",
                    "email": "",
                    "phone": "",
                    "location": ""
                }},
                "education": [
                    {{
                        "degree": "",
                        "institution": "",
                        "year": "",
                        "field": ""
                    }}
                ],
                "work_experience": [
                    {{
                        "title": "",
                        "company": "",
                        "duration": "",
                        "responsibilities": []
                    }}
                ],
                "skills": {{
                    "technical": [],
                    "soft": [],
                    "languages": []
                }},
                "projects": [
                    {{
                        "name": "",
                        "description": "",
                        "technologies": []
                    }}
                ],
                "certifications": [
                    {{
                        "name": "",
                        "organization": "",
                        "year": ""
                    }}
                ]
            }}

            Here is the CV text:
            {cv_text}
            """
            
            response = self.model.generate_content(prompt)
            result = response.text
            
            # Extract JSON from the response
            json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
            if json_match:
                result = json_match.group(1)
            
            # Parse the JSON response
            cv_data = json.loads(result)
            return cv_data
            
        except Exception as e:
            logger.error(f"Error extracting CV information: {str(e)}")
            # Return a basic structure in case of error
            return {
                "personal_info": {},
                "education": [],
                "work_experience": [],
                "skills": {"technical": [], "soft": [], "languages": []},
                "projects": [],
                "certifications": []
            }