import React, { useState } from "react";
import "../styles/PlayerOverview.css";

const ITEMS_PER_PAGE = 7; // Number of items per page for pagination

const games = [
  {
    game: 1,
    heartRateRecovery: 78,
    injuries: 2,
    bestPlayerRecommendation: "Player 5: Good heart rate recovery",
    worstPlayerRecommendation: "Player 2: To train more",
  },
  {
    game: 2,
    heartRateRecovery: 85,
    injuries: 1,
    bestPlayerRecommendation: "Player 3: Improved endurance",
    worstPlayerRecommendation: "Player 4: Needs better recovery",
  },
  {
    game: 3,
    heartRateRecovery: 95,
    injuries: 3,
    bestPlayerRecommendation: "Player 1: Consistent performance",
    worstPlayerRecommendation: "Player 6: High fatigue observed",
  },
  {
    game: 4,
    heartRateRecovery: 72,
    injuries: 0,
    bestPlayerRecommendation: "Player 7: Maintains stable stats",
    worstPlayerRecommendation: "Player 8: Needs strength training",
  },
  {
    game: 5,
    heartRateRecovery: 102,
    injuries: 4,
    bestPlayerRecommendation: "Player 9: Quick recovery post-game",
    worstPlayerRecommendation: "Player 10: Lacks endurance",
  },
  {
    game: 6,
    heartRateRecovery: 78,
    injuries: 0,
    bestPlayerRecommendation: "Player 9: Best performance",
    worstPlayerRecommendation: "Player 10: Lacks stretching",
  },
  {
    game: 7,
    heartRateRecovery: 78,
    injuries: 0,
    bestPlayerRecommendation: "Player 9: Best performance",
    worstPlayerRecommendation: "Player 10: Lacks stretching",
  },
  {
    game: 8,
    heartRateRecovery: 78,
    injuries: 0,
    bestPlayerRecommendation: "Player 9: Best performance",
    worstPlayerRecommendation: "Player 10: Lacks stretching",
  },
  {
    game: 9,
    heartRateRecovery: 78,
    injuries: 0,
    bestPlayerRecommendation: "Player 9: Best performance",
    worstPlayerRecommendation: "Player 10: Lacks stretching",
  },
];

const PlayerOverview = () => {
  const [currentPage, setCurrentPage] = useState(1);

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

  return (
    <div className="player-overview-container">
      <div className="player-overview-header">
        <h2>Overview</h2>
      </div>
      <table className="player-table">
        <thead>
          <tr>
            <th>Game</th>
            <th>Heart Rate Recovery</th>
            <th>Injuries</th>
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

export default PlayerOverview;
