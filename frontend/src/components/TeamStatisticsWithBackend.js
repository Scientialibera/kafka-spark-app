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
        const response = await axios.get("http://127.0.0.1:8000/team-metrics");
        const data = response.data;

        // Extract data for the chart
        const labels = Object.keys(data["Team Total Distance Per Game"]).map(
          (key, index) => `Game ${index + 1}`
        );
        const totalDistanceData = Object.values(data["Team Total Distance Per Game"]).map(
          (distance) => distance / 1000 // Convert meters to kilometers
        );
        const avgSpeedData = Object.values(data["Team Average Speeds per game"]);
        const maxSpeedData = Object.values(data["Team Max Speeds per Game"]);

        // Prepare data for the chart
        setChartData({
          labels,
          datasets: [
            {
              label: "Total Distance (km)",
              data: totalDistanceData,
              borderColor: "#636AE8",
              backgroundColor: "rgba(99, 106, 232, 0.2)",
              tension: 0.4,
            },
            {
              label: "Avg Speed (km/h)",
              data: avgSpeedData,
              borderColor: "#22CCB2",
              backgroundColor: "rgba(34, 204, 178, 0.2)",
              tension: 0.4,
            },
            {
              label: "Max Speed (km/h)",
              data: maxSpeedData,
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
