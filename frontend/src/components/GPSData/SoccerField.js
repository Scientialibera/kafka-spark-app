import React, { useState, useEffect } from "react";
import "../../styles/SoccerField.css";
import soccerFieldBg from "../../icons/soccer-field.jpg"; // Ensure correct path and extension

const SoccerField = ({ runId, players }) => {
  // Field Dimensions in Pixels
  const FIELD_WIDTH = 900; // Increased width
  const FIELD_HEIGHT = 600; // Increased height
  const STREAM_SECONDS = 30; // Duration of the live stream in seconds

  // Define GPS Bounds (Adjust these based on your synthetic or real GPS data)
  const MIN_LATITUDE = 40.00042;
  const MAX_LATITUDE = 40.00058; // Narrower range for better centralization
  const MIN_LONGITUDE = -75.00068;
  const MAX_LONGITUDE = -75.00048; // Narrower range for better centralization

  // Initialise 10 Players to Match deviceIds (gps_1 to gps_10)
  const [playerPositions, setPlayerPositions] = useState([]);

  useEffect(() => {
    const latitudeRange = Math.abs(MAX_LATITUDE - MIN_LATITUDE);
    const longitudeRange = Math.abs(MAX_LONGITUDE - MIN_LONGITUDE);

    const paddings = {
      topBottomPadding: Math.max(50, 0.1 * latitudeRange * FIELD_HEIGHT),
      leftRightPadding: Math.max(100, 0.1 * longitudeRange * FIELD_WIDTH),
    };

    const initialPlayers = players.map((p) => {
      const randomX = Math.random() * FIELD_WIDTH;
      const randomY = Math.random() * FIELD_HEIGHT;
      const { x, y } = constrainPosition(randomX, randomY, paddings); // Apply constraints
      return {
        id: p.id,
        name: p.name,
        x,
        y,
        latitude: null,
        longitude: null,
        timestamp: null,
        }
    });

    setPlayerPositions(initialPlayers);
  }, [players]); // Runs once on mount

    const [live, setLive] = useState(false);
    const [tooltip, setTooltip] = useState({ visible: false, x: 0, y: 0, player: null });
    const [statusMessage, setStatusMessage] = useState("");

    // Calculate dynamic padding based on the spread of GPS data
    const calculateDynamicPadding = (gpsData) => {
      const latitudeRange = Math.abs(MAX_LATITUDE - MIN_LATITUDE);
      const longitudeRange = Math.abs(MAX_LONGITUDE - MIN_LONGITUDE);

      // Top-bottom and left-right paddings calculated relative to data range
      const topBottomPadding = Math.max(50, 0.1 * latitudeRange * FIELD_HEIGHT);
      const leftRightPadding = Math.max(100, 0.1 * longitudeRange * FIELD_WIDTH);

      return { topBottomPadding, leftRightPadding };
    };

      // Utility Function to Constrain Player Positions Within Field Boundaries
      const constrainPosition = (x, y, paddings) => {
      const { topBottomPadding, leftRightPadding } = paddings;
      return {
        x: Math.max(leftRightPadding, Math.min(FIELD_WIDTH - leftRightPadding, x)),
        y: Math.max(topBottomPadding, Math.min(FIELD_HEIGHT - topBottomPadding, y)),
      };
    };

  // Function to Map GPS Coordinates to Field Coordinates
  const mapGPSToField = (latitude, longitude, paddings) => {
    const { topBottomPadding, leftRightPadding } = paddings;

    // Normalize GPS coordinates
    const normalizedX = (latitude - MIN_LATITUDE) / (MAX_LATITUDE - MIN_LATITUDE);
    const normalizedY = (longitude - MIN_LONGITUDE) / (MAX_LONGITUDE - MIN_LONGITUDE);

    // Scale to field dimensions with dynamic padding
    const x = normalizedX * (FIELD_WIDTH - 2 * leftRightPadding) + leftRightPadding;
    const y = normalizedY * (FIELD_HEIGHT - 2 * topBottomPadding) + topBottomPadding;

    return constrainPosition(x, y, paddings);
  };

  // Function to Start Synthetic Data Stream
  const startSyntheticDataStream = async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/start-synthetic-data?num_players=11&stream_seconds=${STREAM_SECONDS}`,
        { method: "POST" }
      );
      if (response.ok) {
        setStatusMessage("Streaming started...");
        setLive(true);
      } else {
        setStatusMessage("Failed to start synthetic data stream.");
      }
    } catch (error) {
      console.error("Error starting synthetic data stream:", error);
      setStatusMessage("Error starting data stream.");
    }
  };

  // Function to Fetch GPS Data and Update Player Positions
  const fetchGPSData = async () => {
    try {
      const deviceIds = players.map((p) => `gps_${p.id}`);
      const gpsResponses = await Promise.all(
        deviceIds.map(async (deviceId) => {
          const response = await fetch(
            `http://127.0.0.1:8000/get-topic-messages/${deviceId}/${runId}?limit=1`
          );
          return response.ok ? response.json() : null;
        })
      );

      const gpsData = gpsResponses
        .filter(Boolean)
        .map((data, index) => ({
          id: players[index].id,
          latitude: data.messages[0].latitude,
          longitude: data.messages[0].longitude,
          timestamp: data.messages[0].timestamp || "No Timestamp",
        }));

      console.log("Fetched GPS Data:", gpsData); // Debugging Purpose

      // Calculate dynamic paddings
      const paddings = calculateDynamicPadding(gpsData);

      setPlayerPositions((prevPlayers) =>
        prevPlayers.map((player) => {
          const gps = gpsData.find((g) => g.id === player.id);
          if (gps) {
            const { x, y } = mapGPSToField(gps.latitude, gps.longitude, paddings);
            return { 
              ...player, 
              x, 
              y, 
              latitude: gps.latitude, 
              longitude: gps.longitude, 
              timestamp: gps.timestamp 
            };
          }
          return player;
        })
      );
    } catch (error) {
      console.error("Error fetching GPS data:", error);
    }
  };

  
  // useEffect Hook to Handle Live Streaming Logic
  useEffect(() => {
    let interval;
    let timeout;

    if (live) {
      // Initial Data Fetch
      fetchGPSData();

      // Set Interval to Fetch Data Every 5 Seconds
      interval = setInterval(() => {
        fetchGPSData();
      }, 5000);

      // Set Timeout to Stop Streaming After STREAM_SECONDS
      timeout = setTimeout(() => {
        setLive(false);
        setStatusMessage("Live stream ended. Press 'Start Live Stream' to restart.");
      }, STREAM_SECONDS * 1000);
    }

    // Cleanup Function to Clear Interval and Timeout
    return () => {
      if (interval) clearInterval(interval);
      if (timeout) clearTimeout(timeout);
    };
  }, [live, runId, players]); // Added runId as a dependency

  // Handlers for Tooltip Display
  // Handlers for Tooltip Display
  const handleMouseEnter = (event, player) => {
    const rect = event.target.getBoundingClientRect();
    setTooltip({
      visible: true,
      x: rect.left + rect.width / 2,
      y: rect.top - 10,
      player,
    });
  };


  const handleMouseLeave = () => {
    setTooltip({ visible: false, x: 0, y: 0, player: null });
  };

  return (
    <div className="soccer-field-container">
      <div className="soccer-field-header">
        <button
          className="button"
          onClick={startSyntheticDataStream}
          disabled={live}
        >
          {live ? "Streaming..." : "Start Live Stream"}
        </button>
        {statusMessage && <p className="status-message">{statusMessage}</p>}
      </div>
      <div
        className="soccer-field"
        style={{
          backgroundImage: `url(${soccerFieldBg})`,
          width: `${FIELD_WIDTH}px`,
          height: `${FIELD_HEIGHT}px`,
        }}
      >
        {playerPositions.map((player) => (
          <div
            key={player.id}
            className="player-marker"
            style={{ left: `${player.x}px`, top: `${player.y}px` }}
            onMouseEnter={(event) => handleMouseEnter(event, player)}
            onMouseLeave={handleMouseLeave}
          >
            {player.id}
          </div>
        ))}
        {tooltip.visible && tooltip.player && (
          <div
            className="tooltip"
            style={{ left: `${tooltip.x}px`, top: `${tooltip.y}px` }}
          >
            <p><strong>{tooltip.player.name}</strong></p>
            <p>Latitude: {tooltip.player.latitude ?? "N/A"}</p>
            <p>Longitude: {tooltip.player.longitude ?? "N/A"}</p>
            <p>Timestamp: {tooltip.player.timestamp ? new Date(tooltip.player.timestamp).toLocaleString() : "N/A"}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SoccerField;
