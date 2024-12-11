import React, { useEffect, useState } from "react";
import "../styles/MetricsCards.css";

// Utility function to render arrow and percentage
const renderArrowAndPercentage = (positive, directionPositive, percentage) => {
  const arrowDirection = positive ? "▲" : "▼"; // Direction based on `positive`
  const colorClass = directionPositive ? "positive" : "negative"; // Color based on `directionPositive`
  return (
    <span className={`metrics-arrow-percentage ${colorClass}`}>
      <span className="arrow">{arrowDirection}</span>
      {percentage}
    </span>
  );
};

const MetricsCardsWithBackend = () => {
  const [gameStats, setGameStats] = useState({ Wins: 0, Losses: 0, Draws: 0 });
  const [teamMetrics, setTeamMetrics] = useState({
    totalDistance: 0,
    recoveryRate: 0,
  });

  useEffect(() => {
    // Fetch game statistics
    const fetchGameStats = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/game-statistics");
        const data = await response.json();
        setGameStats(data);
      } catch (error) {
        console.error("Error fetching game statistics:", error);
      }
    };

    // Fetch team metrics
    const fetchTeamMetrics = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/team-metrics");
        const data = await response.json();

        // Calculate the average of all runs for "Total Distance Per Game"
        const distances = Object.values(data["Total Distance Per Game"]);
        const averageDistance =
          distances.reduce((acc, value) => acc + value, 0) / distances.length;

        setTeamMetrics({
          totalDistance: averageDistance.toFixed(2), // Round to 2 decimal places
          recoveryRate: data["Average Team Recovery Rate"].toFixed(2),
        });
      } catch (error) {
        console.error("Error fetching team metrics:", error);
      }
    };

    fetchGameStats();
    fetchTeamMetrics();
  }, []);

  return (
    <div className="metrics-container">
      {/* Grouped Metrics Card */}
      <div
        className="metrics-card grouped-card"
        style={{ background: "#fdf1f5" }}
      >
        <div className="group-content">
          <div className="group-item">
            <h4>Wins</h4>
            <div className="metrics-value">{gameStats.Wins}</div>
            <div>
              {renderArrowAndPercentage(
                true,
                true,
                "N/A" // No percentage provided yet
              )}
            </div>
          </div>
          <div className="group-item">
            <h4>Losses</h4>
            <div className="metrics-value">{gameStats.Losses}</div>
            <div>
              {renderArrowAndPercentage(
                true,
                false,
                "N/A" // No percentage provided yet
              )}
            </div>
          </div>
          <div className="group-item">
            <h4>Draws</h4>
            <div className="metrics-value">{gameStats.Draws}</div>
            <div>
              {renderArrowAndPercentage(
                false,
                true,
                "N/A" // No percentage provided yet
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Single Metrics Cards */}
      <div
        className="metrics-card"
        style={{ background: "#f2f2fd" }}
      >
        <h4 className="distance-title">Total Distance Covered / Game</h4>
        <div className="metrics-value">{teamMetrics.totalDistance} km</div>
        <div>
          {renderArrowAndPercentage(false, false, "N/A")}
        </div>
      </div>

      <div
        className="metrics-card"
        style={{ background: "#effcfa" }}
      >
        <h4 className="recovery-title">Average Team Recovery Time</h4>
        <div className="metrics-value">{teamMetrics.recoveryRate} bpm/s</div>
        <div>
          {renderArrowAndPercentage(false, true, "N/A")}
        </div>
      </div>
    </div>
  );
};

export default MetricsCardsWithBackend;
