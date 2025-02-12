from crewai import Agent
from langchain.tools import tool
from unstructured.partition.auto import partition
import io
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from typing import Dict, ClassVar

class DataProcessorAgent(Agent):
    def __init__(self):
        super().__init__(
            role='Data Processor',
            goal='Clean, transform, and enrich data for report generation',
            backstory="""Expert in data wrangling and preparation.
            Transforms raw data into a structured format, identifies incident types,
            and handles various data formats.""",
            tools=[],
            verbose=True,
            allow_delegation=False
        )

    def process_glpi_data(self, incident_data: str, document_data: str = None, solution_data: str = None, task_data: str = None) -> dict:
        try:
            incident_data = eval(incident_data)
            if task_data:
                task_data = eval(task_data)

            processed_data = {
                'incident_id': incident_data.get('id'),
                'name': incident_data.get('name'),
                'content': self.clean_html(incident_data.get('content')),
                'status': incident_data.get('status'),
                'priority': incident_data.get('priority'),
                'urgency': incident_data.get('urgency'),
                'impact': incident_data.get('impact'),
                'date': incident_data.get('date'),
                'solvedate': incident_data.get('solvedate'),
                'users_id_recipient': incident_data.get('users_id_recipient'),
                'solution': self.clean_html(solution_data) if solution_data else "",
                'tasks': [{
                    'id': task.get('id'),
                    'content': self.clean_html(task.get('content')),
                    'state': task.get('state'),
                    'users_id': task.get('users_id')
                } for task in eval(task_data)] if task_data else [],
                'document_content': self.extract_text_from_document_content(document_data) if document_data else "",
                'incident_type': self.classify_incident_type({
                    'content': incident_data.get('content', ''),
                    'solution': solution_data or '',
                    'name': incident_data.get('name', '')
                })
            }
            return processed_data
        except Exception as e:
            print(f"Error processing GLPI data: {e}")
            return {}

    def clean_html(self, html_content: str) -> str:
        if not html_content:
            return ""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for element in soup(["script", "style"]):
                element.extract()
            return soup.get_text(separator=" ", strip=True)
        except Exception as e:
            print(f"Error cleaning HTML: {e}")
            return ""

    def extract_text_from_document_content(self, document_content_str: str) -> str:
        try:
            document_content_bytes = eval(document_content_str)
            if isinstance(document_content_bytes, str):
                document_content_bytes = document_content_bytes.encode('utf-8')
            with io.BytesIO(document_content_bytes) as file:
                elements = partition(file=file)
            return "\n".join(str(element) for element in elements)
        except Exception as e:
            print(f"Error extracting text from document: {e}")
            return ""

    def classify_incident_type(self, processed_data: dict) -> str:
        all_text = ' '.join([
            processed_data.get('content', '').lower(),
            processed_data.get('solution', '').lower(),
            processed_data.get('name', '').lower()
        ])
        
        keyword_mapping = {
            'Network Issue': ['network', 'outage', 'internet', 'connection'],
            'Software Installation': ['software', 'install', 'application', 'program'],
            'Password Reset': ['password', 'reset', 'login'],
            'Queue Management': ['queue', 'purge', 'queued']
        }
        
        for incident_type, keywords in keyword_mapping.items():
            if any(keyword in all_text for keyword in keywords):
                return incident_type
        return 'Other'
