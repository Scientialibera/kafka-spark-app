# Base Image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
