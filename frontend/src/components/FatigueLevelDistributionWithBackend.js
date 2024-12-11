import React, { useState, useEffect } from "react";
import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js"; // Import necessary components
import "../styles/FatigueLevelDistribution.css";

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

const FatigueLevelDistributionWithBackend = () => {
  const [data, setData] = useState(null); // State to store fetched data
  const [error, setError] = useState(null); // State to track errors
  const [isLoading, setIsLoading] = useState(true); // State to track loading status

  useEffect(() => {
    // Fetch fatigue data from backend
    const fetchFatigueData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/fatigue-distribution");
        if (!response.ok) {
          throw new Error("Failed to fetch data from the backend");
        }
        const fatigueData = await response.json();

        // Convert backend data to chart format
        setData({
          labels: ["Low", "Moderate", "High"],
          datasets: [
            {
              data: [
                fatigueData["Low Fatigue"],
                fatigueData["Medium Fatigue"],
                fatigueData["High Fatigue"],
              ],
              backgroundColor: ["#636AE8", "#E8618C", "#ADB5BD"],
              hoverBackgroundColor: ["#5A60D6", "#D7507B", "#9AA1A6"],
            },
          ],
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchFatigueData();
  }, []);

  const options = {
    plugins: {
      legend: {
        display: false, // Use custom legend
      },
    },
    cutout: "60%", // Doughnut style
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 1,
  };

  if (isLoading) {
    return <p>Loading...</p>; // Display loading message
  }

  if (error) {
    return <p style={{ color: "red" }}>{error}</p>; // Display error message
  }

  const totalPlayers =
    data.datasets[0].data.reduce((acc, value) => acc + value, 0) || 1; // Avoid division by zero

  return (
    <div className="fatigue-level-container">
      <h4 className="title">Fatigue Level Distribution</h4>
      <div className="chart-container">
        <Doughnut data={data} options={options} />
      </div>
      <div className="chart-legend">
        <div className="legend-item">
          <span className="legend-color low"></span>
          <span className="legend-label">Low</span>
          <span className="legend-value">{data.datasets[0].data[0]} players</span>
          <span className="legend-percentage low-bg">
            {((data.datasets[0].data[0] / totalPlayers) * 100).toFixed(0)}%
          </span>
        </div>
        <div className="legend-item">
          <span className="legend-color moderate"></span>
          <span className="legend-label">Moderate</span>
          <span className="legend-value">{data.datasets[0].data[1]} players</span>
          <span className="legend-percentage moderate-bg">
            {((data.datasets[0].data[1] / totalPlayers) * 100).toFixed(0)}%
          </span>
        </div>
        <div className="legend-item">
          <span className="legend-color high"></span>
          <span className="legend-label">High</span>
          <span className="legend-value">{data.datasets[0].data[2]} players</span>
          <span className="legend-percentage high-bg">
            {((data.datasets[0].data[2] / totalPlayers) * 100).toFixed(0)}%
          </span>
        </div>
      </div>
    </div>
  );
};

export default FatigueLevelDistributionWithBackend;
