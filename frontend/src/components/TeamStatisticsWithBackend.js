import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
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
import axios from "axios";
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
  // State to store chart data
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data from the backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/team-statistics");
        const data = response.data;

        // Transform the response to the format required by the chart
        const transformedData = {
          labels: Object.keys(data["Total Distance Per Game"]), // Games as labels
          datasets: [
            {
              label: "Total Distance",
              data: Object.values(data["Total Distance Per Game"]),
              borderColor: "#636AE8",
              backgroundColor: "rgba(99, 106, 232, 0.2)",
              tension: 0.4,
            },
            {
              label: "Avg Speed",
              data: Object.values(data["Average Speed Per Game"]),
              borderColor: "#22CCB2",
              backgroundColor: "rgba(34, 204, 178, 0.2)",
              tension: 0.4,
            },
            {
              label: "Max Speed",
              data: Object.values(data["Max Speed Per Game"]),
              borderColor: "#E8618C",
              backgroundColor: "rgba(232, 97, 140, 0.2)",
              tension: 0.4,
            },
          ],
        };

        setChartData(transformedData); // Update chart data
        setLoading(false);
      } catch (err) {
        setError("Failed to fetch data.");
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Chart options
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

  // Show loading or error state
  if (loading) return <div>Loading Team Statistics...</div>;
  if (error) return <div>{error}</div>;

  // Render the chart with fetched data
  return (
    <div className="team-statistics-container">
      <h2 className="team-statistics-title">Team Statistics</h2>
      <div className="chart-wrapper">
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
};

export default TeamStatisticsWithBackend;
