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

# Default environment variables (override in docker-compose.yml)
ENV GLPI_URL=http://glpi:9090
ENV GLPI_APP_TOKEN=your_glpi_app_token
ENV GLPI_USER_TOKEN=your_glpi_user_token
ENV MEILISEARCH_URL=http://meilisearch:7700
ENV MEILISEARCH_MASTER_KEY=your_meilisearch_master_key
ENV WASABI_ENDPOINT=s3.us-east-2.wasabisys.com
ENV WASABI_ACCESS_KEY=your_wasabi_access_key
ENV WASABI_SECRET_KEY=your_wasabi_secret_key
ENV OPENAI_API_BASE=http://llm:8000/v1  # Or external URL
ENV OPENAI_API_KEY=your_openai_api_key
ENV MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.1
ENV BUCKET_NAME=autopdf-bucket

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
