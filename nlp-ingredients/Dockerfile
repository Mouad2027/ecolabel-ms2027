FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy models (optional, can be downloaded at runtime)
RUN python -m spacy download en_core_web_sm || echo "Warning: en_core_web_sm not downloaded"
RUN python -m spacy download fr_core_news_sm || echo "Warning: fr_core_news_sm not downloaded"
RUN python -m spacy download de_core_news_sm || echo "Warning: de_core_news_sm not downloaded"

# Pre-download Hugging Face models to avoid runtime download issues
RUN python -c "from transformers import pipeline; pipeline('zero-shot-classification', model='facebook/bart-large-mnli')" || echo "Warning: BART model not downloaded"

# Copy application code
COPY . .

# Expose port
EXPOSE 8002

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
