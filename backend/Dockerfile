# Base Image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install OS-level dependencies
RUN apt-get update && apt-get install -y \
    procps \
    default-jdk \
    iputils-ping \
    netcat \
    nano && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME dynamically
RUN update-alternatives --config java | grep '/usr/lib/jvm/' | awk '{print $NF}' | head -n 1 > /java_home.txt
ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
ENV PATH="$JAVA_HOME/bin:$PATH"

# Verify Java installation during build (for debugging purposes)
RUN java -version

# Copy requirements first for better layer caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Set the default command
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
