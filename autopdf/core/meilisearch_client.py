import meilisearch
from core.config import settings
from typing import List, Optional, Dict

class MeilisearchClient:
    def __init__(self) -> None:
        self.client = meilisearch.Client(settings.meilisearch_url, settings.meilisearch_master_key) # Using settings

    def index_document(self, index_name: str, document: dict) -> None:
        index = self.client.index(index_name)
        index.add_documents([document])

    def search(self, index_name: str, query: str, limit:int = 5) -> List[dict]:
        index = self.client.index(index_name)
        result = index.search(query, {"limit": limit})
        return result['hits']

    def create_index(self, index_name: str) -> None:
        try:
            self.client.create_index(index_name)
        except meilisearch.errors.MeilisearchCommunicationError as e:
            print("Meilisearch Communication Error:", e)
            raise
        except meilisearch.errors.MeilisearchAPIError as e:
            print("Meilisearch API Error:", e)
            if e.code == 'index_already_exists':
                print(f"Index '{index_name}' already exists.")
            else:
                raise

    def delete_index(self, index_name:str) -> None:
        try:
            self.client.delete_index(index_name)
        except meilisearch.errors.MeilisearchCommunicationError as e:
            print("Meilisearch Communication Error:", e)
            raise
        except meilisearch.errors.MeilisearchAPIError as e:
            print("Meilisearch API Error:", e)
            if e.code == 'index_not_found':
                print(f"Index '{index_name}' not found.")
            else:
                raise

    def get_document(self, index_name: str, doc_id: str) -> Optional[Dict]:
        index = self.client.index(index_name)
        try:
            return index.get_document(doc_id)
        except meilisearch.errors.MeilisearchCommunicationError as e:
            print("Meilisearch Communication Error:", e)
            return None
        except meilisearch.errors.MeilisearchAPIError as e:
             if e.code == 'document_not_found':
                return None
             else:
                 print("Meilisearch API Error:", e)
                 return None

    def update_document(self, index_name: str, document: dict) -> Dict:
        index = self.client.index(index_name)
        response = index.update_documents([document])
        return response
