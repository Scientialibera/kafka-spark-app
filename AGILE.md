# Project Issues

## Epic: FrontEnd

### Feature: User Dashboard
**Description:** Create a user-facing dashboard to display game and player statistics.

#### Story: Create Dashboard Layout
**Description:** Design the layout for the dashboard to display real-time stats, player data, and recommendations.

- **Subtask:** Wireframe Dashboard
  - **Description:** Design wireframes for the dashboard, showing player data, game stats, and recommended actions.
  
- **Subtask:** Develop UI Components
  - **Description:** Build reusable UI components such as cards, graphs, and stat tables for the dashboard.
  
- **Subtask:** Integrate Live Data Feed
  - **Description:** Connect the UI to the backend's live data feed for real-time statistics.

#### Story: Player and Team Data Visualization
**Description:** Visualize player and team performance metrics using charts and graphs.

- **Subtask:** Design Player Data Visuals
  - **Description:** Create dynamic charts to display player performance metrics like speed, stress levels, etc.
  
- **Subtask:** Team Statistics Overview
  - **Description:** Develop a team overview page showing collective performance metrics for the team.
  
- **Subtask:** Implement Filtering and Sorting
  - **Description:** Enable filtering by date, player, and metrics to view specific data trends.

#### Story: User Login and Authentication
**Description:** Implement user authentication for access to personalized data and settings.

- **Subtask:** Design Login Page
  - **Description:** Create a UI for user login, registration, and password recovery.
  
- **Subtask:** Implement Authentication API
  - **Description:** Connect frontend to authentication backend to validate users and manage sessions.
  
- **Subtask:** Build Role-based Access Control
  - **Description:** Implement access control for different user types, including admins, coaches, and players.

### Feature: Real-Time Notifications
**Description:** Notify users with live updates on player status, game events, and performance alerts.

#### Story: Build Notification System
**Description:** Develop a system to show real-time notifications for events such as injuries or performance alerts.

- **Subtask:** Design Notification UI
  - **Description:** Create a UI for in-app notifications and alerts.
  
- **Subtask:** Connect WebSocket for Live Notifications
  - **Description:** Integrate WebSockets to display live notifications from the backend.
  
- **Subtask:** Implement Notification Preferences
  - **Description:** Allow users to customize the type of notifications they want to receive.

## Epic: BackEnd

### Feature: Project Setup
**Description:** Setup the overall project structure and configurations.

#### Story: Organize Project Structure
**Description:** Organize folders and necessary files for API, Spark, and Docker.

- **Subtask:** Create Project Folders and Files
  - **Description:** Organize folders for API, Spark processing, config, and Docker.
  
- **Subtask:** Add Configuration Files
  - **Description:** Add necessary config files (e.g., `config.py` for API and Spark).
  
- **Subtask:** Setup Virtual Environment
  - **Description:** Setup virtual environment and install dependencies (FastAPI, Kafka, Spark).
  
- **Subtask:** Create `.gitignore` and README
  - **Description:** Define `.gitignore` and add README with project instructions.

### Feature: Kafka Setup
**Description:** Set up Kafka as a message broker for data ingestion.

#### Story: Install and Configure Kafka
**Description:** Set up Kafka services using Docker and integrate with the API.

- **Subtask:** Add Docker Service for Kafka
  - **Description:** Add Kafka service in `docker-compose.yml` and configure it with Zookeeper.
  
- **Subtask:** Configure Kafka Producer in API
  - **Description:** Configure a Kafka producer in FastAPI to stream data.
  
- **Subtask:** Configure Kafka Consumer for Spark
  - **Description:** Set up Kafka consumer logic in Spark for real-time data ingestion.

### Feature: Spark Setup
**Description:** Set up Apache Spark for real-time data processing using Kafka.

#### Story: Install and Configure Apache Spark
**Description:** Configure Apache Spark with Kafka for real-time streaming.

- **Subtask:** Add Docker Service for Spark
  - **Description:** Configure a Spark service in `docker-compose.yml`.
  
- **Subtask:** Set Up Spark Dependencies
  - **Description:** Install and set up dependencies for Spark in `Dockerfile`.
  
- **Subtask:** Implement Spark Streaming
  - **Description:** Set up Spark Structured Streaming to consume Kafka data.

### Feature: Data Ingestion
**Description:** Ingest and process data from recording devices, games, and player stats.

#### Story: Device Data Interface
**Description:** Create an interface to capture data from recording devices monitoring player movements and stress using Kafka.

- **Subtask:** Setup Device APIs
  - **Description:** Develop APIs to ingest data from multiple recording devices.
  
- **Subtask:** Data Validation and Cleaning
  - **Description:** Implement validation and cleaning of incoming device data to ensure accuracy.
  
- **Subtask:** Store Data in Database
  - **Description:** Develop logic to store device data in a structured format in the database.

#### Story: Game Stats Ingestion
**Description:** Build a system to gather game and player stats for analysis.

- **Subtask:** Develop Game Stats API
  - **Description:** Create APIs to gather and ingest statistics from games and players.
  
- **Subtask:** Database Design for Stats
  - **Description:** Design a database schema to store game and player statistics for analysis.
  
- **Subtask:** Implement Batch Processing
  - **Description:** Develop a batch processing system to handle large volumes of stats data.

### Feature: Performance Analysis and Recommendations
**Description:** Analyze player data to identify improvements and generate training/injury recommendations.

#### Story: Build Performance Metrics Analyzer
**Description:** Analyze player stats and device data to identify performance metrics.

- **Subtask:** Implement Data Analysis Logic
  - **Description:** Develop the backend logic to analyze stress, speed, and other performance metrics.
  
- **Subtask:** Integrate with Machine Learning Models
  - **Description:** Connect data analysis with machine learning models to detect trends and predict outcomes.
  
- **Subtask:** Store and Serve Analysis Results
  - **Description:** Store analysis results in the database and make them accessible via APIs.

#### Story: Generate Injury Prevention Recommendations
**Description:** Provide injury prevention tips based on analyzed player performance data.

- **Subtask:** Define Injury Risk Factors
  - **Description:** Use data to identify risk factors for injuries in players.
  
- **Subtask:** Build Recommendation Engine
  - **Description:** Develop an engine to generate recommendations based on risk factors and performance data.
  
- **Subtask:** Create Recommendation API
  - **Description:** Develop an API to serve injury prevention recommendations to the frontend.

### Feature: User Authentication and Role Management
**Description:** Provide secure user authentication and role-based access control.

#### Story: User Authentication System
**Description:** Develop a system for user authentication, including login and registration.

- **Subtask:** Setup Authentication API
  - **Description:** Create APIs for user login, registration, and password management.
  
- **Subtask:** JWT Token Management
  - **Description:** Implement JWT-based authentication for session management and secure APIs.

#### Story: Role-Based Access Control
**Description:** Define and implement roles for different user types (players, coaches, admins).

- **Subtask:** Define User Roles
  - **Description:** Establish user roles and permissions for accessing different sections of the application.
  
- **Subtask:** Build Access Control Middleware
  - **Description:** Create middleware to enforce role-based access restrictions.
