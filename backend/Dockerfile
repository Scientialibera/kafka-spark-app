# Base Image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install OS-level dependencies
RUN apt-get update && apt-get install -y procps default-jdk && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Dynamically set JAVA_HOME after installation
ENV JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
ENV PATH="$JAVA_HOME/bin:$PATH"

# Copy the rest of the application files
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Set the default command
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
