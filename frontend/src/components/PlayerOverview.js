import React from "react";
import "../styles/PlayerOverview.css";

const players = [
  {
    name: "Player A",
    heartRate: 78,
    injuries: 2,
    lastRecommendation: "Avoid high-impact movements",
    fatigueLevel: "Moderate",
  },
  {
    name: "Player B",
    heartRate: 85,
    injuries: 0,
    lastRecommendation: "Focus on endurance training",
    fatigueLevel: "Low",
  },
  {
    name: "Player C",
    heartRate: 95,
    injuries: 1,
    lastRecommendation: "Increase rest",
    fatigueLevel: "High",
  },
  {
    name: "Player D",
    heartRate: 72,
    injuries: 0,
    lastRecommendation: "Continue regular training",
    fatigueLevel: "Low",
  },
  {
    name: "Player E",
    heartRate: 102,
    injuries: 3,
    lastRecommendation: "Physio session recommended",
    fatigueLevel: "Moderate",
  },
];

const PlayerOverview = () => {
  return (
    <div className="player-overview-container">
      <div className="player-overview-header">
        <h2>Player Overview</h2>
        <a href="#" className="view-all-link">
          View all
        </a>
      </div>
      <table className="player-table">
        <thead>
          <tr>
            <th>Player</th>
            <th>Heart Rate</th>
            <th>Injuries</th>
            <th>Last Recommendation</th>
            <th>Fatigue Level</th>
          </tr>
        </thead>
        <tbody>
          {players.map((player, index) => (
            <tr key={index}>
              <td>{player.name}</td>
              <td>{player.heartRate}</td>
              <td>{player.injuries}</td>
              <td>{player.lastRecommendation}</td>
              <td>
                <span className={`fatigue-badge ${player.fatigueLevel.toLowerCase()}`}>
                  {player.fatigueLevel}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="pagination">
        <span>1 - 10 of 145</span>
        <div className="pagination-controls">
          <button>{"<"}</button>
          <button className="active">1</button>
          <button>2</button>
          <button>...</button>
          <button>11</button>
          <button>{">"}</button>
        </div>
      </div>
    </div>
  );
};

export default PlayerOverview;
