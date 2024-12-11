FROM node:18-alpine

# Set the working directory to frontend
WORKDIR /app/frontend

# Copy only frontend-related files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend directory
COPY frontend/ .

# Expose the port your frontend development server will run on
EXPOSE 3000

# Start the development server
CMD ["npm", "start"]
