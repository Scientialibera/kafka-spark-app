# Base Image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Update and install required packages
RUN apt-get update && apt-get install -y procps default-jdk

# Dynamically set JAVA_HOME after installation
RUN export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:/bin/java::") && \
    echo "JAVA_HOME=$JAVA_HOME" >> /etc/environment

# Source /etc/environment to set JAVA_HOME globally in the container
RUN . /etc/environment

# Add JAVA_HOME to PATH
ENV PATH="$JAVA_HOME/bin:$PATH"

# Copy application files
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
