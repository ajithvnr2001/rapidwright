from crewai import Agent
from langchain.tools import tool
from unstructured.partition.auto import partition
import io
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any, ClassVar  # Import ClassVar


class DataProcessorAgent(Agent):
    def __init__(self):
        super().__init__(
            role='Data Processor',
            goal='Clean, transform, and enrich data for report generation',
            backstory="""Expert in data wrangling and preparation.
            Transforms raw data into a structured format, identifies incident types,
            and handles various data formats.""",
            tools=[],  # No external tools needed
            verbose=True,
            allow_delegation=False
        )

    def process_glpi_data(self, incident_data: str, document_data: str = None, solution_data: str = None, task_data:str=None) -> dict:
        """Processes the raw data from GLPI, including document parsing."""
        try:
            # Convert the string representation of incident data to a dictionary
            incident_data = eval(incident_data)  # Use eval() safely here
            if task_data:
                task_data = eval(task_data)

            processed_data = {}

			# Extract relevant incident details.
            processed_data['incident_id'] = incident_data.get('id')
            processed_data['name'] = incident_data.get('name')
            processed_data['content'] = self.clean_html(incident_data.get('content')) #Clean HTML
            processed_data['status'] = incident_data.get('status')
            processed_data['priority'] = incident_data.get('priority')
            processed_data['urgency'] = incident_data.get('urgency')
            processed_data['impact'] = incident_data.get('impact')
            processed_data['date'] = incident_data.get('date')
            processed_data['solvedate'] = incident_data.get('solvedate')
            processed_data['users_id_recipient'] = incident_data.get('users_id_recipient')

            # Extract and process the solution
            if solution_data:
                processed_data['solution'] = self.clean_html(solution_data) #Clean HTML
            else:
                processed_data['solution'] = ""
            # Extract and process tasks
            if task_data:
                processed_tasks = []
                for task in task_data:
                    cleaned_task = {}
                    cleaned_task['id'] = task.get('id')
                    cleaned_task['content'] = self.clean_html(task.get('content'))  # Clean HTML
                    cleaned_task['state'] = task.get('state')
                    cleaned_task['users_id'] = task.get('users_id')
                    processed_tasks.append(cleaned_task)
                processed_data['tasks'] = processed_tasks
            else:
                processed_data['tasks'] = []

			# Process Document Data using unstructured.io
            if document_data:
                processed_data['document_content'] = self.extract_text_from_document_content(document_data)
            else:
                processed_data['document_content'] = ""

            processed_data['incident_type'] = self.classify_incident_type(processed_data) #Classify
            return processed_data

        except Exception as e:
            print(f"Error processing GLPI data: {e}")
            return {}

    def clean_html(self, html_content: str) -> str:
        """Cleans HTML content and extracts text."""
        if not html_content:
            return ""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Remove script and style tags
            for script_or_style in soup(["script", "style"]):
                script_or_style.extract()
            text = soup.get_text(separator=" ", strip=True)  # Get text with spaces and strip whitespace
            return text
        except Exception as e:
            print(f"Error cleaning HTML: {e}")
            return ""

    def extract_text_from_document_content(self, document_content_str: str) -> str:
        """Extracts text from document content using unstructured.io."""
        try:
            # Convert the string representation to bytes
            document_content_bytes = eval(document_content_str)
            if isinstance(document_content_bytes, str):
                document_content_bytes = document_content_bytes.encode('utf-8')
            # Use BytesIO for in-memory file-like object
            with io.BytesIO(document_content_bytes) as file:
                elements = partition(file=file)  # Auto-detects file type
            # Concatenate text elements
            return "\n".join([str(element) for element in elements])
        except Exception as e:
            print(f"Error extracting text from document: {e}")
            return ""

    def classify_incident_type(self, processed_data: dict) -> str:
        """Classifies the incident type based on keywords (simplified)."""
        content = processed_data.get('content', '').lower()
        solution = processed_data.get('solution', '').lower()
        name = processed_data.get('name', '').lower()
        all_text = content + " " + solution + " " + name

        # Basic keyword matching (expand as needed)
        if any(keyword in all_text for keyword in ['network', 'outage', 'internet', 'connection']):
            return 'Network Issue'
        elif any(keyword in all_text for keyword in ['software', 'install', 'application', 'program']):
            return 'Software Installation'
        elif any(keyword in all_text for keyword in ['password', 'reset', 'login']):
            return 'Password Reset'
        elif any(keyword in all_text for keyword in ['queue', 'purge', 'queued']):
            return 'Queue Management'
        else:
            return 'Other'
