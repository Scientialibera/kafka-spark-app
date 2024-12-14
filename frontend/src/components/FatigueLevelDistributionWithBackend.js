import React, { useState, useEffect } from "react";
import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import "../styles/FatigueLevelDistribution.css";

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

const FatigueLevelDistributionWithBackend = () => {
  const [data, setData] = useState(null); // State to store fetched data
  const [error, setError] = useState(null); // State to track errors
  const [isLoading, setIsLoading] = useState(true); // State to track loading status

  // Helper function to dynamically handle singular/plural "player(s)"
  const getPlayerText = (count) => (count === 1 ? "player" : "players");

  useEffect(() => {
    const fetchFatigueData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/fatigue-distribution");
        if (!response.ok) {
          throw new Error("Failed to fetch data from the backend");
        }
        const fatigueData = await response.json();

        const totalGames = 15; // Total number of games
        const fatigueMatches = fatigueData["Total Fatigue Levels"].match(
          /Low: (\d+), Medium: (\d+), High: (\d+)/
        );

        if (fatigueMatches) {
          const lowFatigue = parseInt(fatigueMatches[1], 10);
          const mediumFatigue = parseInt(fatigueMatches[2], 10);
          const highFatigue = parseInt(fatigueMatches[3], 10);

          // Calculate average players per game in each category
          const lowAverage = (lowFatigue / totalGames).toFixed(1);
          const mediumAverage = (mediumFatigue / totalGames).toFixed(1);
          const highAverage = (highFatigue / totalGames).toFixed(1);

          const totalPlayers = 10 * totalGames;

          // Convert backend data to chart format
          setData({
            labels: ["Low", "Moderate", "High"],
            datasets: [
              {
                data: [lowAverage, mediumAverage, highAverage],
                backgroundColor: ["#636AE8", "#E8618C", "#ADB5BD"],
                hoverBackgroundColor: ["#5A60D6", "#D7507B", "#9AA1A6"],
              },
            ],
            roundedValues: [
              Math.round(lowAverage),
              Math.round(mediumAverage),
              Math.round(highAverage),
            ],
            percentages: [
              ((lowFatigue / totalPlayers) * 100).toFixed(0),
              ((mediumFatigue / totalPlayers) * 100).toFixed(0),
              ((highFatigue / totalPlayers) * 100).toFixed(0),
            ],
          });
        }
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
      tooltip: {
        callbacks: {
          label: function (tooltipItem) {
            const index = tooltipItem.dataIndex;
            const exactValue = data.datasets[0].data[index];
            return `${data.labels[index]}: ${exactValue} players`;
          },
        },
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
          <span className="legend-value">
            {data.roundedValues[0]} {getPlayerText(data.roundedValues[0])}
          </span>
          <span className="legend-percentage low-bg">
            {data.percentages[0]}%
          </span>
        </div>
        <div className="legend-item">
          <span className="legend-color moderate"></span>
          <span className="legend-label">Moderate</span>
          <span className="legend-value">
            {data.roundedValues[1]} {getPlayerText(data.roundedValues[1])}
          </span>
          <span className="legend-percentage moderate-bg">
            {data.percentages[1]}%
          </span>
        </div>
        <div className="legend-item">
          <span className="legend-color high"></span>
          <span className="legend-label">High</span>
          <span className="legend-value">
            {data.roundedValues[2]} {getPlayerText(data.roundedValues[2])}
          </span>
          <span className="legend-percentage high-bg">
            {data.percentages[2]}%
          </span>
        </div>
      </div>
    </div>
  );
};

export default FatigueLevelDistributionWithBackend;
