import React from "react";
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

// Sample Data
const data = {
  labels: ["Game 1", "Game 2", "Game 3", "Game 4", "Game 5", "Game 6", "Game 7", "Game 8", "Game 9", "Game 10"],
  datasets: [
    {
      label: "Total Distance",
      data: [20, 25, 30, 28, 34, 37, 40, 42, 45, 50],
      borderColor: "#636AE8",
      backgroundColor: "rgba(99, 106, 232, 0.2)",
      tension: 0.4,
    },
    {
      label: "Avg Speed",
      data: [10, 12, 13, 14, 15, 16, 15, 14, 13, 12],
      borderColor: "#22CCB2",
      backgroundColor: "rgba(34, 204, 178, 0.2)",
      tension: 0.4,
    },
    {
      label: "Max Speed",
      data: [15, 18, 20, 22, 25, 27, 28, 30, 32, 35],
      borderColor: "#E8618C",
      backgroundColor: "rgba(232, 97, 140, 0.2)",
      tension: 0.4,
    },
  ],
};

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

const TeamStatistics = () => {
  return (
    <div className="team-statistics-container">
      <h2 className="team-statistics-title">Team Statistics</h2>
      <div className="chart-wrapper">
        <Line data={data} options={options} />
      </div>
    </div>
  );
};

export default TeamStatistics;
