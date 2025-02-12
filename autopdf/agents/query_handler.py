from crewai import Agent
from graphs.rag_graph import rag_app
from typing import Dict, ClassVar

class QueryHandlerAgent(Agent):
    def __init__(self):
        super().__init__(
            role='Query Handler',
            goal='Generate informative content using RAG',
            backstory="""Expert in combining information retrieval and generation.
            Uses a Retrieval-Augmented Generation (RAG) approach to answer questions
            and create summaries.""",
            tools=[],
            verbose=True,
            allow_delegation=False
        )

    def run_rag(self, processed_data: dict) -> str:
        inputs = {
            "processed_data": processed_data,
            "query": f"Summarize the incident and its resolution, including any relevant information from past incidents related to {processed_data.get('incident_type', 'this topic')}.",
        }
        result = rag_app.invoke(inputs)
        return result['generated_content']
