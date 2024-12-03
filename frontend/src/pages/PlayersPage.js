import React, { useState } from "react";
import { Line } from "react-chartjs-2"; // Import the Line chart component
import "../styles/PlayersPage.css";
import Sidebar from "../components/Sidebar";

// Import metric icons
import HeartRateIcon from "../icons/heart-rate.png";
import SpeedIcon from "../icons/speed.png";
import AccelerationIcon from "../icons/acceleration.png";
import TemperatureIcon from "../icons/temperature.png";

const ITEMS_PER_PAGE = 3; // Number of items per page for pagination

const PlayersPage = () => {
  const players = [
    {
      id: "player-a",
      name: "John Doe",
      age: 20,
      team: "Team A",
      position: "Midfielder",
      fatigueLevel: "High",
      metrics: {
        heartRate: "142 BPM",
        speed: "24 KM/H",
        acceleration: "0.8 M/S",
        temperature: "37.2 °C",
      },
      heartbeatData: [72, 85, 78, 90, 95, 100],
      overallMetrics: {
        averageHeartRate: "78 bpm",
        averageRecoveryTime: "4 bpm/s",
        maxHeartRate: "142 bpm",
      },
      injuries: [
        {
          date: "2024-11-05",
          type: "Muscle Strain",
          severity: "High",
          recommendation: "Increase lower body stretching",
          actionTaken: false,
        },
        {
          date: "2024-10-15",
          type: "Concussion",
          severity: "Low",
          recommendation: "Light training only",
          actionTaken: true,
        },
        {
          date: "2024-09-22",
          type: "Ankle Sprain",
          severity: "Moderate",
          recommendation: "Attend physiotherapy session",
          actionTaken: false,
        },
        {
          date: "2024-08-10",
          type: "Back Pain",
          severity: "Low",
          recommendation: "Stretch regularly",
          actionTaken: true,
        },
        {
          date: "2024-07-15",
          type: "Shoulder Strain",
          severity: "Moderate",
          recommendation: "Reduce overhead lifting",
          actionTaken: false,
        },
        {
          date: "2024-06-20",
          type: "Hamstring Pull",
          severity: "High",
          recommendation: "Focus on physiotherapy sessions",
          actionTaken: true,
        },
      ],
    },
    {
      id: "player-b",
      name: "Jane Smith",
      age: 23,
      team: "Team B",
      position: "Defender",
      fatigueLevel: "Low",
      metrics: {
        heartRate: "128 BPM",
        speed: "22 KM/H",
        acceleration: "0.6 M/S",
        temperature: "36.8 °C",
      },
      heartbeatData: [65, 70, 68, 72, 75, 78],
      overallMetrics: {
        averageHeartRate: "72 bpm",
        averageRecoveryTime: "3 bpm/s",
        maxHeartRate: "128 bpm",
      },
      injuries: [
        {
          date: "2024-09-12",
          type: "Knee Injury",
          severity: "Moderate",
          recommendation: "Avoid heavy squats",
          actionTaken: true,
        },
        {
          date: "2024-08-10",
          type: "Back Pain",
          severity: "Low",
          recommendation: "Stretch regularly",
          actionTaken: true,
        },
      ],
    },
  ];

  const [selectedPlayer, setSelectedPlayer] = useState(players[0]);
  const [currentPage, setCurrentPage] = useState(1);

  const handlePlayerChange = (event) => {
    const selectedId = event.target.value;
    const player = players.find((p) => p.id === selectedId);
    setSelectedPlayer(player);
    setCurrentPage(1); // Reset to the first page when changing the player
  };

  const metricTitles = {
    heartRate: "Heart Rate",
    speed: "Speed",
    acceleration: "Acceleration",
    temperature: "Temperature",
  };

  const metricIcons = {
    heartRate: HeartRateIcon,
    speed: SpeedIcon,
    acceleration: AccelerationIcon,
    temperature: TemperatureIcon,
  };

  const displayedInjuries = selectedPlayer.injuries.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const totalPages = Math.ceil(selectedPlayer.injuries.length / ITEMS_PER_PAGE);

  const handlePageChange = (newPage) => {
    if (newPage > 0 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  const heartbeatData = {
    labels: ["0–15 min", "15–30 min", "30–45 min", "45–60 min", "60–75 min", "75–90 min"],
    datasets: [
      {
        label: "Average Heartbeat per Minute",
        data: selectedPlayer.heartbeatData,
        borderColor: "#636ae8",
        backgroundColor: "rgba(99, 106, 232, 0.1)",
        pointBackgroundColor: "#636ae8",
        pointBorderColor: "#636ae8",
        pointRadius: 5,
        fill: true,
      },
    ],
  };

  const heartbeatOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        grid: {
          display: false,
        },
      },
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 20,
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
    },
  };

  return (
    <div className="players-page">
      <Sidebar />
      <div className="page-content">
        <div className="header">
          <select
            className="player-dropdown"
            onChange={handlePlayerChange}
            value={selectedPlayer.id}
          >
            {players.map((player) => (
              <option key={player.id} value={player.id}>
                {player.name}
              </option>
            ))}
          </select>
          <button className="button">Start Live Stream</button>
        </div>

        <div className="player-section">
          <div className="container player-info">
            <img
              src="https://via.placeholder.com/133"
              alt={selectedPlayer.name}
              className="player-avatar"
            />
            <div className="player-details">
              <h2>{selectedPlayer.name}</h2>
              <p>
                {selectedPlayer.position} | {selectedPlayer.age} years |{" "}
                {selectedPlayer.team}
              </p>
              <span
                className={`badge ${selectedPlayer.fatigueLevel.toLowerCase()}-fatigue`}
              >
                {selectedPlayer.fatigueLevel} Fatigue
              </span>
            </div>
          </div>

          <div className="action-buttons">
            <button className="button grey">Edit Player Information</button>
            <button className="button grey">Add Injury Record</button>
            <button className="button grey">Assign Training Recommendation</button>
            <button className="button primary">Download Full Player Data</button>
          </div>
        </div>

        <div className="metrics-chart-section">
          <div className="live-metrics-container">
            <h3 className="live-metrics-title">Live Metrics</h3>
            <div className="live-metrics">
              {Object.entries(selectedPlayer.metrics).map(([key, value]) => (
                <div key={key} className="metric-box">
                  <div className={`metric-icon ${key.toLowerCase()}-icon`}>
                    <img src={metricIcons[key]} alt={`${key} icon`} className="icon" />
                  </div>
                  <div className="metric-info">
                    <h4>{metricTitles[key]}</h4>
                    <p>{value}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="heartbeat-chart-container">
            <h3>Average Heartbeat per Minute</h3>
            <div className="chart-wrapper">
              <Line data={heartbeatData} options={heartbeatOptions} />
            </div>
          </div>
        </div>

        <div className="performance-summary">
          <div className="performance-card">
            <div className="rectangle green"></div>
            <div className="text-container">
              <p className="summary-title">Overall Average Heart Rate</p>
              <p className="summary-value">
                {selectedPlayer.overallMetrics.averageHeartRate}
              </p>
            </div>
          </div>

          <div className="performance-card">
            <div className="rectangle yellow"></div>
            <div className="text-container">
              <p className="summary-title">Overall Average Recovery Time</p>
              <p className="summary-value">
                {selectedPlayer.overallMetrics.averageRecoveryTime}
              </p>
            </div>
          </div>

          <div className="performance-card">
            <div className="rectangle red"></div>
            <div className="text-container">
              <p className="summary-title">Overall Maximum Heart Rate</p>
              <p className="summary-value">
                {selectedPlayer.overallMetrics.maxHeartRate}
              </p>
            </div>
          </div>
        </div>

        <div className="container health-info">
          <h3>Health Information</h3>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Injury Type</th>
                <th>Severity</th>
                <th>Recommendation</th>
                <th>Action Taken?</th>
              </tr>
            </thead>
            <tbody>
              {displayedInjuries.map((injury, index) => (
                <tr key={index}>
                  <td>{injury.date}</td>
                  <td>{injury.type}</td>
                  <td>{injury.severity}</td>
                  <td>{injury.recommendation}</td>
                  <td>
                    <input type="checkbox" checked={injury.actionTaken} readOnly />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="pagination">
            <button onClick={() => handlePageChange(currentPage - 1)}>Previous</button>
            <span>
              Page {currentPage} of {totalPages}
            </span>
            <button onClick={() => handlePageChange(currentPage + 1)}>Next</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlayersPage;
