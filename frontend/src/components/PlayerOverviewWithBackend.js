import React, { useState, useEffect } from "react";
import "../styles/PlayerOverview.css";

const ITEMS_PER_PAGE = 4; // Number of items per page for pagination

const PlayerOverviewWithBackend = () => {
  const [games, setGames] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTeamMetrics = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/team-metrics");
        if (!response.ok) {
          throw new Error("Failed to fetch team metrics from the backend");
        }
        const teamMetrics = await response.json();

        // Parse the data for games
        const totalInjuries = teamMetrics["Team Total Injuries"];
        const heartRateRecovery = teamMetrics["Player Average Heart Rate Recovery"];
        const recommendations = teamMetrics["Best and Worst Recommendations Per Game"];

        // Transform the data into a format for the table
        const gamesData = Object.keys(totalInjuries)
          .map((key) => {
            const gameNumber = parseInt(key.split("_")[1], 10); // Extract game number
            const averageHeartRateRecovery = Object.values(heartRateRecovery).reduce(
              (acc, playerData) => acc + (playerData[key] || 0),
              0
            ) / 10; // Average across 10 players

            return {
              game: gameNumber,
              heartRateRecovery: averageHeartRateRecovery.toFixed(2), // Two decimal places
              injuries: totalInjuries[key],
              bestPlayerRecommendation: recommendations[key]?.["Best Recommendation"] || "N/A",
              worstPlayerRecommendation: recommendations[key]?.["Worst Recommendation"] || "N/A",
            };
          })
          .sort((a, b) => b.game - a.game); // Sort games from newest to oldest

        setGames(gamesData);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTeamMetrics();
  }, []);

  const totalPages = Math.ceil(games.length / ITEMS_PER_PAGE);

  const displayedGames = games.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const handlePageChange = (newPage) => {
    if (newPage > 0 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  if (isLoading) {
    return <p>Loading...</p>; // Show loading message
  }

  if (error) {
    return <p style={{ color: "red" }}>{error}</p>; // Show error message
  }

  return (
    <div className="player-overview-container">
      <div className="player-overview-header">
        <h2>Overview</h2>
      </div>
      <table className="player-table">
        <thead>
          <tr>
            <th>Game</th>
            <th>Team Avg Heart Rate Recovery (bpm/s)</th>
            <th>Team Total Injuries</th>
            <th>Best Player Recommendation</th>
            <th>Worst Player Recommendation</th>
          </tr>
        </thead>
        <tbody>
          {displayedGames.map((game, index) => (
            <tr key={index}>
              <td>{game.game}</td>
              <td>{game.heartRateRecovery}</td>
              <td>{game.injuries}</td>
              <td>{game.bestPlayerRecommendation}</td>
              <td>{game.worstPlayerRecommendation}</td>
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
  );
};

export default PlayerOverviewWithBackend;
