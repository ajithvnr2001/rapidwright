import requests
import json
from core.config import settings
from typing import Optional

class GLPIClient:
    def __init__(self) -> None:
        self.base_url: str = settings.glpi_url
        self.app_token: str = settings.glpi_app_token
        self.user_token: str = settings.glpi_user_token
        self.session_token: Optional[str] = None
        self.headers: dict = {
            "Content-Type": "application/json",
            "App-Token": self.app_token,
        }
        self.init_session()

    def init_session(self) -> None:
        """Initiates a session with GLPI and retrieves the session token."""
        url = f"{self.base_url}/initSession"
        headers = self.headers.copy()
        headers["Authorization"] = f"user_token {self.user_token}"

        try:
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            session_data = response.json()
            self.session_token = session_data.get("session_token")
            if not self.session_token:
                raise ValueError("Failed to obtain session token from GLPI.")
            self.headers["Session-Token"] = self.session_token
            print(f"GLPI session initialized. Session Token: {self.session_token}")

        except requests.exceptions.RequestException as e:
            print(f"Error initializing GLPI session: {e}")
            raise
        except ValueError as e:
            print(e)
            raise

    def close_session(self) -> None:
        """Closes the current GLPI session."""
        if not self.session_token:
            return

        url = f"{self.base_url}/killSession"
        try:
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()
            print("GLPI session closed.")
        except requests.exceptions.RequestException as e:
            print(f"Error closing GLPI session: {e}")
        finally:
            self.session_token = None
            self.headers.pop("Session-Token", None)

    def _make_request(self, method: str, endpoint: str, params: dict = None, data: dict = None) -> dict:
        """Centralized request handling with session management."""
        if not self.session_token:
            self.init_session()

        url = f"{self.base_url}/{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params, verify=False)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, verify=False)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print("Session expired or invalid. Re-initializing...")
                self.init_session()
                return self._make_request(method, endpoint, params, data)
            else:
                print(f"HTTP Error during GLPI request: {e}")
                raise
        except requests.exceptions.RequestException as e:
            print(f"Request Exception during GLPI request: {e}")
            raise

    def get_incident(self, incident_id: int) -> dict:
        return self._make_request("GET", f"Ticket/{incident_id}", params={"expand_dropdowns": "true"})

    def get_document(self, document_id: int) -> bytes:
        """Fetches a document from GLPI and returns its content as bytes."""
        doc_info = self._make_request("GET", f"Document/{document_id}")
        if "filepath" not in doc_info or "filename" not in doc_info:
            raise ValueError("Invalid document response from GLPI: missing filepath or filename")

        download_url = f"{self.base_url}/{doc_info['filepath']}"

        try:
            download_headers = {
                "App-Token": self.app_token,
                "Session-Token": self.session_token
            }
            download_response = requests.get(download_url, headers=download_headers, verify=False, stream=True)
            download_response.raise_for_status()
            return download_response.content

        except requests.exceptions.RequestException as e:
            print(f"Error fetching document {document_id} from GLPI: {e}")
            return b""
    
    def get_ticket_solution(self, ticket_id: int) -> str:
        """Retrieves the solution for a given ticket."""
        solutions = self._make_request("GET", f"Ticket/{ticket_id}/ITILSolution")
        if solutions:
            return solutions[-1].get("content", "")
        return ""

    def get_ticket_tasks(self, ticket_id: int) -> list:
        """Retrieves the tasks for a given ticket"""
        return self._make_request("GET", f"Ticket/{ticket_id}/ITILTask")
