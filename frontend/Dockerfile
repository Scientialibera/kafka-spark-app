FROM node:18-alpine

# Set the working directory to frontend
WORKDIR /app/frontend

# Copy package.json and lock files separately to ensure no caching of dependencies
COPY frontend/package*.json ./

# Force install fresh dependencies by removing the npm cache and avoiding cached layers
RUN npm cache clean --force && npm install

# Copy the rest of the frontend directory
COPY frontend/ .

# Expose the port your frontend development server will run on
EXPOSE 3000

# Start the development server
CMD ["npm", "start"]
