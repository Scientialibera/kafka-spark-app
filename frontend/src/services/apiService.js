/**
 * API Service for Sports Prophet Frontend
 * 
 * This service provides a centralized interface for all API calls
 * with consistent error handling and response formatting.
 */

import API_ENDPOINTS from '../config/api';

/**
 * Default fetch options
 */
const defaultOptions = {
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * Handle API response and errors consistently
 */
async function handleResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: `HTTP error! status: ${response.status}`
    }));
    throw new Error(error.detail || 'An error occurred');
  }
  return response.json();
}

/**
 * Make a GET request
 */
async function get(url, options = {}) {
  const response = await fetch(url, {
    ...defaultOptions,
    ...options,
    method: 'GET',
  });
  return handleResponse(response);
}

/**
 * Make a POST request
 */
async function post(url, data, options = {}) {
  const response = await fetch(url, {
    ...defaultOptions,
    ...options,
    method: 'POST',
    body: JSON.stringify(data),
  });
  return handleResponse(response);
}

/**
 * Make a PUT request
 */
async function put(url, data, options = {}) {
  const response = await fetch(url, {
    ...defaultOptions,
    ...options,
    method: 'PUT',
    body: JSON.stringify(data),
  });
  return handleResponse(response);
}

/**
 * Make a DELETE request
 */
async function del(url, options = {}) {
  const response = await fetch(url, {
    ...defaultOptions,
    ...options,
    method: 'DELETE',
  });
  return handleResponse(response);
}

/**
 * API Service object with all available endpoints
 */
const apiService = {
  // Health
  checkHealth: () => get(API_ENDPOINTS.health),
  
  // Devices
  getAllDevices: () => get(API_ENDPOINTS.getAllDevices),
  getDevice: (deviceId) => get(API_ENDPOINTS.getDevice(deviceId)),
  registerDevice: (deviceData) => post(API_ENDPOINTS.registerDevice, deviceData),
  updateDevice: (deviceData) => put(API_ENDPOINTS.updateDevice, deviceData),
  deleteDevice: (deviceId) => del(API_ENDPOINTS.deleteDevice(deviceId)),
  
  // Statistics
  getStats: (deviceId, runId, aggType = 'average') => 
    get(`${API_ENDPOINTS.getStats(deviceId, runId)}?agg_type=${aggType}`),
  
  getSpeed: (deviceId, runId, type = 'speed') =>
    get(`${API_ENDPOINTS.getSpeed(deviceId, runId)}?type=${type}`),
  
  getTeamAverageStats: (numPlayers, runId) =>
    get(API_ENDPOINTS.getTeamAverageStats(numPlayers, runId)),
  
  // Streaming
  startStream: (deviceId, runId, triggers, windowSeconds = 5) =>
    post(API_ENDPOINTS.startStream(deviceId, runId), {
      triggers,
      window_seconds: windowSeconds,
    }),
  
  stopStream: (deviceId, runId) =>
    post(API_ENDPOINTS.stopStream(deviceId, runId)),
  
  startSyntheticData: (numPlayers, streamSeconds) =>
    post(API_ENDPOINTS.startSyntheticData, null, {
      headers: {
        ...defaultOptions.headers,
      },
    }).then(() => 
      fetch(`${API_ENDPOINTS.startSyntheticData}?num_players=${numPlayers}&stream_seconds=${streamSeconds}`, {
        method: 'POST',
      }).then(handleResponse)
    ),
  
  // Kafka Topics
  getTopicMessages: (deviceId, runId, limit = null) => {
    let url = API_ENDPOINTS.getTopicMessages(deviceId, runId);
    if (limit) url += `?limit=${limit}`;
    return get(url);
  },
  
  getTeamKafkaStats: (numPlayers, runId) =>
    get(API_ENDPOINTS.getTeamKafkaStats(numPlayers, runId)),
  
  listTopics: () => get(API_ENDPOINTS.listTopics),
  deleteTopic: (deviceId, runId) => del(API_ENDPOINTS.deleteTopic(deviceId, runId)),
  deleteAllTopics: () => del(API_ENDPOINTS.deleteAllTopics),
  
  // Historical Stats
  getGameStatistics: () => get(API_ENDPOINTS.gameStatistics),
  getTeamMetrics: () => get(API_ENDPOINTS.teamMetrics),
  getPlayerOverview: (playerId) => get(API_ENDPOINTS.playerOverview(playerId)),
  getFatigueDistribution: () => get(API_ENDPOINTS.fatigueDistribution),
  getRecommendations: () => get(API_ENDPOINTS.recommendations),
};

export default apiService;
