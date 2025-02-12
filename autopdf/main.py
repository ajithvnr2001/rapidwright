from crewai import Crew, Task, Process
from agents.data_extractor import DataExtractorAgent
from agents.data_processor import DataProcessorAgent
from agents.query_handler import QueryHandlerAgent
from agents.pdf_generator import PDFGeneratorAgent
from agents.search_indexer import SearchIndexerAgent
from core.glpi import GLPIClient
from core.config import settings
from typing import Dict
from fastapi import FastAPI, Request, HTTPException
from datetime import datetime

app = FastAPI()

# Initialize GLPI client
glpi_client = GLPIClient()

# Initialize agents
data_extractor_agent = DataExtractorAgent(glpi_client)
data_processor_agent = DataProcessorAgent()
query_handler_agent = QueryHandlerAgent()
pdf_generator_agent = PDFGeneratorAgent()
search_indexer_agent = SearchIndexerAgent()

def run_autopdf(incident_id: int, update_solution : bool = False) -> str:
    """Runs the AutoPDF workflow for a given incident ID."""
    extract_incident_task = Task(
        description=f"Extract details for GLPI incident ID {incident_id}",
        agent=data_extractor_agent,
        tools=[data_extractor_agent.get_glpi_incident_details],
        expected_output="Raw data of the incident",
    )
    extract_solution_task = Task(
        description=f"Extract solution for GLPI incident ID {incident_id}",
        agent=data_extractor_agent,
        tools=[data_extractor_agent.get_glpi_ticket_solution],
        expected_output="Raw solution data",
        context=[extract_incident_task],
    )
    extract_tasks_task = Task(
        description=f"Extract tasks for GLPI incident ID {incident_id}",
        agent=data_extractor_agent,
        tools=[data_extractor_agent.get_glpi_ticket_tasks],
        expected_output="Raw tasks data",
        context=[extract_incident_task],
    )
    document_id = 12345  # TODO: Get this dynamically from GLPI
    extract_document_task = Task(
        description=f"Extract content of document ID {document_id}",
        agent=data_extractor_agent,
        tools=[data_extractor_agent.get_glpi_document_content],
        expected_output="Raw document content",
        context=[],
    )
    process_data_task = Task(
        description="Process the extracted data from GLPI",
        agent=data_processor_agent,
        expected_output="Cleaned and structured data",
        context=[extract_incident_task, extract_document_task, extract_solution_task, extract_tasks_task],
        function=data_processor_agent.process_glpi_data
    )
    generate_content_task = Task(
        description="Generate report content using RAG",
        agent=query_handler_agent,
        expected_output="Generated content for the report",
        context=[process_data_task],
        function=query_handler_agent.run_rag
    )
    create_pdf_task = Task(
        description="Create a PDF report",
        agent=pdf_generator_agent,
        tools=[pdf_generator_agent.create_pdf_from_text_tool_method],
        expected_output="PDF file as bytes.",
        function=lambda x: pdf_generator_agent.create_pdf_from_text_tool_method(content=x, title=f"Incident Report - {incident_id}"),
        context=[generate_content_task]
    )
    index_pdf_task = Task(
        description="Store PDF and index",
        agent=search_indexer_agent,
        expected_output="Confirmation message",
        context=[create_pdf_task, process_data_task],
        function=search_indexer_agent.index_and_store_pdf
    )

    crew = Crew(
        agents=[
            data_extractor_agent,
            data_processor_agent,
            query_handler_agent,
            pdf_generator_agent,
            search_indexer_agent,
        ],
        tasks=[
            extract_incident_task,
            extract_solution_task,
            extract_tasks_task,
            extract_document_task,
            process_data_task,
            generate_content_task,
            create_pdf_task,
            index_pdf_task
        ],
        process=Process.sequential,
        verbose=2
    )

    try:
        result = crew.kickoff()
        if update_solution:
            solution_update_result = glpi_client.update_ticket_solution(incident_id, result['generated_content'])
            if solution_update_result:
                 print(f"Solution for incident {incident_id} updated successfully.")
            else:
                 print(f"Failed to update solution for incident {incident_id}.")
        return result

    finally:
        glpi_client.close_session()


@app.post("/webhook")
async def glpi_webhook(request: Request):
    """Handles incoming webhooks from GLPI."""
    try:
        body = await request.body()
        data = json.loads(body.decode())

        if not isinstance(data, list):
            raise HTTPException(status_code=400, detail="Invalid webhook payload format")

        for event in data:
            if 'event' not in event or 'itemtype' not in event or 'items_id' not in event:
                raise HTTPException(status_code=400, detail="Missing required fields in event")

            if event['itemtype'] == 'Ticket':
                incident_id = int(event['items_id'])

                if event['event'] in ('add', 'update'):
                    print("*"*50)
                    print(f"Received event: {event['event']} for Ticket ID: {incident_id}")
                    print("*"*50)
                    if event['event'] == 'update':
                         run_autopdf(incident_id, update_solution = True)
                    else:
                         run_autopdf(incident_id, update_solution = False)
                else:
                    print(f"Ignoring event type: {event['event']} for Ticket")

        return {"message": "Webhook received and processed"}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        print(f"Error in webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/")
async def root():
    return {"message": "AutoPDF is running!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port="8000")
