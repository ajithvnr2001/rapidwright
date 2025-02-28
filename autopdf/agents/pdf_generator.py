from crewai import Agent
from core.pdf_utils import create_pdf_from_text, create_pdf_from_html
from langchain.tools import tool
from typing import ClassVar  # Import ClassVar
from typing import ClassVar

class PDFGeneratorAgent(Agent):
    def __init__(self):
        super().__init__(
            role='PDF Generator',
            goal='Create well-formatted PDF reports',
            backstory="""Skilled in document formatting and PDF generation.
            Uses ReportLab to create professional-looking reports.""",
            tools=[self.create_pdf_from_text_tool_method, self.create_pdf_from_html_tool_method],
            verbose=True,
            allow_delegation=False
        )
    @tool
    def create_pdf_from_text_tool_method(self, content: str, title: str = "Incident Report") -> bytes:
        """Creates a PDF from text content.
        Args:
            content (str): The text content of the PDF.
            title (str): the title of the document (optional)
        Returns:
            bytes: The PDF file as bytes.
        """

        if not content:
            raise ValueError("Content is required for PDF Generation.")

        return create_pdf_from_text(content, title)
    @tool
    def create_pdf_from_html_tool_method(self, content: str, title: str = "Incident Report") -> bytes:
        """Creates a PDF from HTML content.
        Args:
            content (str): The HTML content of the PDF.
            title (str): the title of the document (optional)
        Returns:
            bytes: The PDF file as bytes.
        """
        if not content:
            raise ValueError("Content is required for PDF Generation.")

        return create_pdf_from_html(content, title)
