from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import io
from core.config import settings
from typing import Optional

def create_pdf_from_text(content: str, title: str = "Incident Report") -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(title, styles['h1']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(content, styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

def create_pdf_from_html(html_content: str, title: str = "Incident Report") -> bytes:
    from reportlab.platypus import HTML2PDF

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(title, styles['h1']))
    story.append(Spacer(1, 0.2*inch))

    for flowable in HTML2PDF(html_content).story:
        story.append(flowable)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
