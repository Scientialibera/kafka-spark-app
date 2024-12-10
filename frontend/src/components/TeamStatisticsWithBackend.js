import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import axios from "axios";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import "../styles/TeamStatistics.css";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const TeamStatisticsWithBackend = () => {
  const [chartData, setChartData] = useState(null); // State to store chart data
  const [error, setError] = useState(null); // State to store errors
  const [loading, setLoading] = useState(true); // State to track loading status

  useEffect(() => {
    // Fetch data from the backend
    const fetchData = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/team-statistics");
        const data = response.data;

        // Extract Total Distance Per Game
        const labels = Object.keys(data["Total Distance Per Game"]).map(
          (key, index) => `Game ${index + 1}`
        );
        const totalDistanceData = Object.values(data["Total Distance Per Game"]);

        // Handle Average Speed and Max Speed (currently single values)
        const avgSpeed = Array(labels.length).fill(data["Average Speed Per Game"]);
        const maxSpeed = Array(labels.length).fill(data["Max Speed Per Game"]);

        // Prepare data for the chart
        setChartData({
          labels,
          datasets: [
            {
              label: "Total Distance",
              data: totalDistanceData,
              borderColor: "#636AE8",
              backgroundColor: "rgba(99, 106, 232, 0.2)",
              tension: 0.4,
            },
            {
              label: "Avg Speed",
              data: avgSpeed,
              borderColor: "#22CCB2",
              backgroundColor: "rgba(34, 204, 178, 0.2)",
              tension: 0.4,
            },
            {
              label: "Max Speed",
              data: maxSpeed,
              borderColor: "#E8618C",
              backgroundColor: "rgba(232, 97, 140, 0.2)",
              tension: 0.4,
            },
          ],
        });
      } catch (error) {
        setError("Failed to fetch data from the server.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: "top",
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
      },
      y: {
        grid: {
          drawBorder: false,
        },
      },
    },
  };

  // Render loading state, error, or the chart
  return (
    <div className="team-statistics-container">
      <h2 className="team-statistics-title">Team Statistics</h2>
      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p style={{ color: "red" }}>{error}</p>
      ) : (
        <div className="chart-wrapper">
          <Line data={chartData} options={options} />
        </div>
      )}
    </div>
  );
};

export default TeamStatisticsWithBackend;
