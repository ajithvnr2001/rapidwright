FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    tesseract-ocr \
    poppler-utils \
    libmagic1 \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

# Credentials will be provided via environment variables at runtime.
# DO NOT HARDCODE THEM HERE.

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
