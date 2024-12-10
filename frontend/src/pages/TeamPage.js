import React, { useState } from "react";
import { Line } from "react-chartjs-2"; // Import the Line chart component
import "../styles/TeamPage.css";
import Sidebar from "../components/Sidebar";

// Import metric icons
import HeartRateIcon from "../icons/heart-rate.png";
import SpeedIcon from "../icons/speed.png";
import AccelerationIcon from "../icons/acceleration.png";
import TemperatureIcon from "../icons/temperature.png";

const ITEMS_PER_PAGE = 3; // Number of items per page for pagination

const TeamPage = () => {
  const team = {
    name: "Team A",
    manager: "John Doe",
    coach: "Peter Smith",
    totalPlayers: 21,
    seasonRecord: "5-2-3",
    leagueRank: "#2 in League",
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
    games: [
      {
        game: "1",
        totalDistance: "64 km",
        avgHeartRateRecovery: "78 bpm/s",
        percentageFit: "60%",
        teamRecommendation: "Increase lower body stretching",
      },
      {
        game: "2",
        totalDistance: "72 km",
        avgHeartRateRecovery: "70 bpm/s",
        percentageFit: "70%",
        teamRecommendation: "Light training only",
      },
      {
        game: "3",
        totalDistance: "50 km",
        avgHeartRateRecovery: "85 bpm/s",
        percentageFit: "40%",
        teamRecommendation: "Attend physiotherapy session",
      },
      {
        game: "4",
        totalDistance: "58 km",
        avgHeartRateRecovery: "69 bpm/s",
        percentageFit: "65%",
        teamRecommendation: "Stretch regularly",
      },
    ],
  };

  const [currentPage, setCurrentPage] = useState(1);

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

  const displayedGames = team.games.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const totalPages = Math.ceil(team.games.length / ITEMS_PER_PAGE);

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
        data: team.heartbeatData,
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
    <div className="team-page">
      <Sidebar />
      <div className="page-content">
        <div className="team-header">
          <button className="button">Start Live Stream</button>
        </div>

        <div className="team-section">
          <div className="container team-info">
            <img src="https://via.placeholder.com/133" className="team-avatar" alt="Team Avatar" />
            <div className="team-details">
              <h2>{team.name}</h2>
              <p><strong>Manager:</strong> {team.manager}</p>
              <p><strong>Coach:</strong> {team.coach}</p>
              <p><strong>Players:</strong> {team.totalPlayers}</p>
              <p><strong>Season Record:</strong> {team.seasonRecord}</p>
              <p><strong>League Rank:</strong> {team.leagueRank}</p>
            </div>
          </div>

          <div className="action-buttons">
            <button className="button grey">Edit Team Information</button>
            <button className="button grey">View Players</button>
            <button className="button grey">Assign Training Recommendation</button>
            <button className="button primary">Download Full Team Data</button>
          </div>
        </div>

        <div className="metrics-chart-section">
          <div className="live-metrics-container">
            <h3 className="live-metrics-title">Live Metrics</h3>
            <div className="live-metrics">
              {Object.entries(team.metrics).map(([key, value]) => (
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
              <p className="summary-value">{team.overallMetrics.averageHeartRate}</p>
            </div>
          </div>

          <div className="performance-card">
            <div className="rectangle yellow"></div>
            <div className="text-container">
              <p className="summary-title">Overall Average Recovery Time</p>
              <p className="summary-value">{team.overallMetrics.averageRecoveryTime}</p>
            </div>
          </div>

          <div className="performance-card">
            <div className="rectangle red"></div>
            <div className="text-container">
              <p className="summary-title">Overall Maximum Heart Rate</p>
              <p className="summary-value">{team.overallMetrics.maxHeartRate}</p>
            </div>
          </div>
        </div>

        <div className="container health-info">
          <h3>Health Information</h3>
          <table>
            <thead>
              <tr>
                <th>Game</th>
                <th>Total Distance</th>
                <th>Heart Rate Recovery</th>
                <th>% Players Fit</th>
                <th>Team Recommendation</th>
                <th>Action Taken?</th>
              </tr>
            </thead>
            <tbody>
              {displayedGames.map((game, index) => (
                <tr key={index}>
                  <td>{game.game}</td>
                  <td>{game.totalDistance}</td>
                  <td>{game.avgHeartRateRecovery}</td>
                  <td>{game.percentageFit}</td>
                  <td>{game.teamRecommendation}</td>
                  <td>
                    <input
                      type="checkbox"
                      className="action-taken-checkbox"
                      checked={game.actionTaken}
                      onChange={() => {
                        const updatedGames = [...team.games];
                        updatedGames[
                          (currentPage - 1) * ITEMS_PER_PAGE + index
                        ].actionTaken = !game.actionTaken;
                      }}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="pagination">
            <button
              className={`pagination-btn ${currentPage === 1 ? "disabled" : ""}`}
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            <div className="pagination-controls">
              {Array.from({ length: totalPages }, (_, index) => (
                <button
                  key={index}
                  className={`pagination-btn ${currentPage === index + 1 ? "active" : ""}`}
                  onClick={() => handlePageChange(index + 1)}
                >
                  {index + 1}
                </button>
              ))}
            </div>
            <button
              className={`pagination-btn ${currentPage === totalPages ? "disabled" : ""}`}
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeamPage;
