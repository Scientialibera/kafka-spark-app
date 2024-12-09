import React, { useEffect, useState } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2"; // Chart library
import "../styles/PlayersPage.css";
import Sidebar from "../components/Sidebar";
import HeartRateIcon from "../icons/heart-rate.png";
import SpeedIcon from "../icons/speed.png";
import AccelerationIcon from "../icons/acceleration.png";
import TemperatureIcon from "../icons/temperature.png";

const PlayersPageWithBackend = () => {
  const [players, setPlayers] = useState([]); // List of players
  const [selectedPlayer, setSelectedPlayer] = useState(null); // Currently selected player
  const [liveMetrics, setLiveMetrics] = useState(null); // Live metrics for the player
  const [heartbeatData, setHeartbeatData] = useState([]); // Data for the chart
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch players list from backend
    const fetchPlayers = async () => {
      try {
        const response = await axios.get("http://localhost:8000/players"); // Replace with actual backend endpoint
        setPlayers(response.data);
        setSelectedPlayer(response.data[0]); // Select first player by default
        setLoading(false);
      } catch (error) {
        console.error("Error fetching players:", error);
        setLoading(false);
      }
    };

    fetchPlayers();
  }, []);

  useEffect(() => {
    if (!selectedPlayer) return;

    // Fetch live metrics and heartbeat data when player changes
    const fetchMetrics = async () => {
      try {
        const metricsResponse = await axios.get(
          `http://localhost:8000/get-stats/${selectedPlayer.id}/1?agg_type=average`
        ); // Replace with actual backend endpoint for metrics
        setLiveMetrics(metricsResponse.data.metrics);

        const heartbeatResponse = await axios.get(
          `http://localhost:8000/get-heartbeat/${selectedPlayer.id}/1`
        ); // Replace with actual backend endpoint for heartbeat data
        setHeartbeatData(heartbeatResponse.data.heartbeatData);
      } catch (error) {
        console.error("Error fetching metrics or heartbeat data:", error);
      }
    };

    fetchMetrics();
  }, [selectedPlayer]);

  // Handle dropdown change for selecting a player
  const handlePlayerChange = (event) => {
    const selectedId = event.target.value;
    const player = players.find((p) => p.id === selectedId);
    setSelectedPlayer(player);
  };

  const metricIcons = {
    heartRate: HeartRateIcon,
    speed: SpeedIcon,
    acceleration: AccelerationIcon,
    temperature: TemperatureIcon,
  };

  const metricTitles = {
    heartRate: "Heart Rate",
    speed: "Speed",
    acceleration: "Acceleration",
    temperature: "Temperature",
  };

  const heartbeatChartData = {
    labels: ["0–15 min", "15–30 min", "30–45 min", "45–60 min", "60–75 min", "75–90 min"],
    datasets: [
      {
        label: "Average Heartbeat per Minute",
        data: heartbeatData,
        borderColor: "#636ae8",
        backgroundColor: "rgba(99, 106, 232, 0.1)",
        pointBackgroundColor: "#636ae8",
        pointBorderColor: "#636ae8",
        pointRadius: 5,
        fill: true,
      },
    ],
  };

  const heartbeatChartOptions = {
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

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!players.length) {
    return <div>No players found.</div>;
  }

  return (
    <div className="players-page">
      <Sidebar />
      <div className="page-content">
        <div className="header">
          <select className="player-dropdown" onChange={handlePlayerChange} value={selectedPlayer?.id || ""}>
            {players.map((player) => (
              <option key={player.id} value={player.id}>
                {player.name}
              </option>
            ))}
          </select>
          <button className="button">Start Live Stream</button>
        </div>

        <div className="metrics-chart-section">
          {/* Live Metrics */}
          {liveMetrics && (
            <div className="live-metrics-container">
              <h3 className="live-metrics-title">Live Metrics</h3>
              <div className="live-metrics">
                {Object.entries(liveMetrics).map(([key, value]) => (
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
          )}

          {/* Heartbeat Chart */}
          <div className="heartbeat-chart-container">
            <h3>Average Heartbeat per Minute</h3>
            <div className="chart-wrapper">
              <Line data={heartbeatChartData} options={heartbeatChartOptions} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlayersPageWithBackend;
