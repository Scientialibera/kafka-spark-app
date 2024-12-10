FROM node:18-alpine as build

# Install Python for frontend requirements if needed
RUN apk add --no-cache python3 py3-pip

WORKDIR /app
COPY . .  # Copy entire project

# Install Python requirements for frontend (if any)
# If not needed, you can remove these two lines
RUN if [ -f frontend/requirements.txt ]; then pip3 install -r frontend/requirements.txt; fi

WORKDIR /app/frontend
RUN npm install
RUN npm run build

FROM node:18-alpine
WORKDIR /app/frontend
COPY --from=build /app/frontend /app/frontend

EXPOSE 3000
CMD ["npm", "start"]
