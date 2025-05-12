FROM python:3.12-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY web_parsing/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies needed for scikit-learn
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create web_parsing package directory
RUN mkdir -p /app/web_parsing

# Copy setup.py first
COPY setup.py /app/

# Copy all Python files to web_parsing directory
COPY web_parsing/*.py /app/web_parsing/
COPY web_parsing/configuration /app/web_parsing/configuration
COPY web_parsing/entrypoint.sh /app/entrypoint.sh

# Create __init__.py if it doesn't exist
RUN touch /app/web_parsing/__init__.py

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Install web_parsing as a package
WORKDIR /app
RUN pip install -e .

# Set PYTHONPATH to include the app directory
ENV PYTHONPATH=/app

ENTRYPOINT ["/app/entrypoint.sh"]