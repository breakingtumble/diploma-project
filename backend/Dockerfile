FROM python:3.12-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory
COPY backend /app/backend
COPY setup.py /app/

# Install the backend package
RUN pip install -e .

# Set PYTHONPATH to include the app directory
ENV PYTHONPATH=/app

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
