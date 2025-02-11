from langchain_core.runnables import RunnablePassthrough
from langgraph.graph import StateGraph, END
from core.llm_utils import generate_text
from core.meilisearch_client import MeilisearchClient
from core.config import settings
from typing import Dict, Any, List, Optional

meilisearch_client = MeilisearchClient()

class RAGState:
    def __init__(self) -> None:
        self.processed_data: Dict = {}
        self.query: str = ""
        self.retrieved_documents: List[Dict] = []
        self.generated_content: str = ""
        self.iterations: int = 0

def retrieve_node(state: RAGState) -> Dict[str, Any]:
    """Retrieves documents from Meilisearch."""
    query = state.query
    processed_data = state.processed_data
    
    retrieved_docs = meilisearch_client.search(
        index_name="glpi_incidents",
        query=query,
        limit=5
    )
    return {"retrieved_documents": retrieved_docs}

def generate_node(state: RAGState) -> Dict[str, str]:
    """Generates content using the LLM."""
    processed_data = state.processed_data
    retrieved_documents = state.retrieved_documents
    
    prompt_template = """
    Generate a concise incident report summary including:
    - Incident description
    - Resolution steps
    - Related historical incidents
    - Key learnings
    
    Incident Data: {processed_data}
    
    Related Incidents: {retrieved_documents}
    """
    
    formatted_docs = "\n".join([f"- {doc.get('content', '')}" for doc in retrieved_documents])
    
    return {"generated_content": generate_text(
        prompt_template,
        {
            "processed_data": processed_data,
            "retrieved_documents": formatted_docs
        }
    )}

def check_node(state: RAGState) -> Dict[str, bool]:
    """Controls RAG iteration quality."""
    state.iterations += 1
    if state.iterations >= settings.max_rag_iterations:
        return {"done": True}
    # Simple quality check - expand with proper validation
    content = state.generated_content
    return {"done": any(keyword in content.lower() for keyword in ["resolution", "root cause"])}

def finalize_node(state: RAGState) -> RAGState:
    return state

# Create and configure the workflow
workflow = StateGraph(RAGState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)
workflow.add_node("check", check_node)
workflow.add_node("finalize", finalize_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", "check")
workflow.add_conditional_edges(
    "check",
    lambda x: "retrieve" if not x["done"] else "finalize",
)
workflow.add_edge("finalize", END)

rag_app = workflow.compile()
