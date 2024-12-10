import React from "react";
import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js"; // Import necessary components
import "../styles/FatigueLevelDistribution.css";

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

const FatigueLevelDistribution = () => {
  const data = {
    labels: ["Low", "Moderate", "High"],
    datasets: [
      {
        data: [46, 18, 36], // Percentages
        backgroundColor: ["#636AE8", "#E8618C", "#ADB5BD"], // Colors
        hoverBackgroundColor: ["#5A60D6", "#D7507B", "#9AA1A6"], // Colors on hover
      },
    ],
  };

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
            <span className="legend-value">5 players</span>
            <span className="legend-percentage low-bg">46%</span>
        </div>
        <div className="legend-item">
            <span className="legend-color moderate"></span>
            <span className="legend-label">Moderate</span>
            <span className="legend-value">2 players</span>
            <span className="legend-percentage moderate-bg">18%</span>
        </div>
        <div className="legend-item">
            <span className="legend-color high"></span>
            <span className="legend-label">High</span>
            <span className="legend-value">4 players</span>
            <span className="legend-percentage high-bg">36%</span>
        </div>
        </div>
    </div>
  );
};

export default FatigueLevelDistribution;
