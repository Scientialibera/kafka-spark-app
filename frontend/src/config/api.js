/**
 * API Configuration for Sports Prophet Frontend
 * 
 * This file centralizes all API endpoint configurations.
 * Use environment variables for production deployments.
 */

// Base API URL - use environment variable or default to localhost
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// WebSocket URL
const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

/**
 * API Endpoints
 */
export const API_ENDPOINTS = {
  // Root
  root: `${API_BASE_URL}/`,
  health: `${API_BASE_URL}/health`,
  
  // Device Management
  registerDevice: `${API_BASE_URL}/register-device`,
  updateDevice: `${API_BASE_URL}/update-device`,
  deleteDevice: (deviceId) => `${API_BASE_URL}/delete-device/${deviceId}`,
  getAllDevices: `${API_BASE_URL}/devices`,
  getDevice: (deviceId) => `${API_BASE_URL}/device/${deviceId}`,
  
  // Streaming
  sendStream: (deviceId, runId) => `${WS_BASE_URL}/send-stream/${deviceId}/${runId}`,
  startStream: (deviceId, runId) => `${API_BASE_URL}/start-stream/${deviceId}/${runId}`,
  stopStream: (deviceId, runId) => `${API_BASE_URL}/stop-stream/${deviceId}/${runId}`,
  startSyntheticData: `${API_BASE_URL}/start-synthetic-data`,
  
  // Statistics
  getStats: (deviceId, runId) => `${API_BASE_URL}/get-stats/${deviceId}/${runId}`,
  getSpeed: (deviceId, runId) => `${API_BASE_URL}/get-speed/${deviceId}/${runId}`,
  getNotification: (deviceId, runId) => `${API_BASE_URL}/get-notification/${deviceId}/${runId}`,
  getTeamAverageStats: (numPlayers, runId) => `${API_BASE_URL}/get-team-average-stats/${numPlayers}/${runId}`,
  
  // Kafka Topics
  getTopicMessages: (deviceId, runId) => `${API_BASE_URL}/get-topic-messages/${deviceId}/${runId}`,
  getTeamKafkaStats: (numPlayers, runId) => `${API_BASE_URL}/get-team-kafka-stats/${numPlayers}/${runId}`,
  deleteTopic: (deviceId, runId) => `${API_BASE_URL}/delete-topic/${deviceId}/${runId}`,
  deleteAllTopics: `${API_BASE_URL}/delete-all-topics`,
  listTopics: `${API_BASE_URL}/list-topics`,
  
  // Historical Stats
  gameStatistics: `${API_BASE_URL}/game-statistics`,
  teamMetrics: `${API_BASE_URL}/team-metrics`,
  playerOverview: (playerId) => `${API_BASE_URL}/player-overview/${playerId}`,
  fatigueDistribution: `${API_BASE_URL}/fatigue-distribution`,
  recommendations: `${API_BASE_URL}/recommendations`,
};

/**
 * Default configuration values
 */
export const CONFIG = {
  // Pagination
  ITEMS_PER_PAGE: 7,
  
  // Streaming
  DEFAULT_STREAM_SECONDS: 100,
  DEFAULT_NUM_PLAYERS: 10,
  
  // Polling intervals (ms)
  STATS_POLL_INTERVAL: 5000,
  NOTIFICATION_POLL_INTERVAL: 1000,
  
  // Thresholds
  HEART_RATE: {
    MIN: 70,
    MAX: 140,
    WARNING_LOW: 60,
    WARNING_HIGH: 160,
  },
  TEMPERATURE: {
    MIN: 36.0,
    MAX: 39.0,
    WARNING_LOW: 35.5,
    WARNING_HIGH: 39.5,
  },
};

export default API_ENDPOINTS;
