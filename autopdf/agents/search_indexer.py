from crewai import Agent
from core.meilisearch_client import MeilisearchClient
from core.wasabi_client import WasabiClient
from core.config import settings
import hashlib
from langchain.tools import tool
from typing import Dict
from datetime import datetime

meilisearch_client = MeilisearchClient()
wasabi_client = WasabiClient()


class SearchIndexerAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            role='Search Indexer',
            goal='Store and index PDFs for search and versioning',
            backstory="""Expert in data storage, indexing, and version control.
            Stores PDFs in Wasabi and indexes them in Meilisearch.""",
            tools=[],
            verbose=True,
            allow_delegation=False
        )
    def index_and_store_pdf(self, pdf_content: bytes, processed_data: Dict) -> str:
        """Stores the PDF in Wasabi, indexes it in Meilisearch, and handles versioning."""

        incident_id = processed_data['incident_id']
        incident_type = processed_data['incident_type']
        # Use a timestamp for versioning, along with the hash.
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.sha256(pdf_content).hexdigest()
        version_string = f"{now}_{content_hash[:10]}"  # Use part of hash for readability

        object_name = f"{incident_type}/{incident_id}/{version_string}.pdf"


        # Check if the document already exists (using the new naming)
        if wasabi_client.document_exists(settings.bucket_name, object_name):
            return f"Document with identical content and timestamp already exists: {object_name}"

        # Upload to Wasabi
        wasabi_client.upload_document(settings.bucket_name, object_name, pdf_content)

        # Create index if it doesn't exist
        meilisearch_client.create_index("glpi_incidents")

        # Prepare document for Meilisearch
        index_document = {
            'id': f"{incident_id}-{version_string}",  # Unique ID
            'incident_id': incident_id,
            'incident_type': incident_type,
            'version': version_string,
            'object_name': object_name,
            'content': processed_data.get('generated_content', ''),  # Include summary
            'solution': processed_data.get('solution', ''),
            'tasks': processed_data.get('tasks', []),
            'date': processed_data.get('date', ''),
            'name': processed_data.get('name', ''),
            'updated_at': now,  # Add an updated_at timestamp
        }

        # Index in Meilisearch
        meilisearch_client.index_document("glpi_incidents", index_document)
        return f"PDF stored and indexed: {object_name}"
